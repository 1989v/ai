---
description: "가상 프롬프트를 입력 받아 현재 합성된 CLAUDE.md/메모리/settings 룰 중 어떤 게 실제로 트리거될지 dry-run 한다. --cheap (룰 매칭, 무료) / --full (LLM 판정, 유료) 모드 분리. 자연어 트리거: 프롬프트 시뮬레이션, 룰 트리거 추론, dry-run 분석."
argument-hint: "\"<prompt>\" [--cheap|--full] [--limit=N] [--json]"
---

# /claude-md:simulate

가상 프롬프트가 현재 세션에서 **어떤 룰을 트리거할지** dry-run 한다.

## 사용 예

```bash
# default (cheap) — 무료, 키워드 매칭 기반
/claude-md:simulate "주문 서비스에 새 기능 추가해줘"

# full — LLM 판정 (Haiku 호출, 비용 발생)
/claude-md:simulate "주문 서비스에 새 기능 추가해줘" --full

# 상위 5개만
/claude-md:simulate "테스트 작성해" --limit=5
```

## 옵션

| Flag | 의미 |
|------|------|
| `--cheap` (default) | 무료, 키워드/heading 기반 룰 매칭. 정확도 보통. |
| `--full` | Haiku 등 가벼운 모델로 의미 기반 룰 매칭. 정확도 높음. 호출당 ≈ $0.001 ~ $0.01 |
| `--limit=N` | 결과 상위 N개만 (default: 10) |
| `--json` | raw JSON 출력 |
| `--source=auto|introspect|fs|hook` | analyze 와 동일 — 룰 인벤토리 소스 |

## 비용 가드 (`--full` 모드)

- 본 모드는 외부 LLM API 호출을 발생시킨다.
- 첫 호출 시 사용자에게 예상 비용 표시 후 명시적 confirm:
  ```
  ⚠ --full mode will call Haiku with ~3.2k input tokens.
    Estimated cost: ~$0.0008
  Proceed? [y/N]
  ```
- `--yes` 옵션으로 confirm skip 가능 (CI 환경).
- 세션당 누적 비용을 추적해 `--full` 호출 5회 초과 시 추가 경고.

## 실행 흐름

### 1. 룰 인벤토리 확보 (analyze 캐시 재사용)

`/claude-md:analyze` 의 캐시 (`~/.claude/projects/{slug}/cma-cache/{hash}.json`) 가 있으면 그대로 사용. 없으면 내부적으로 analyze 를 한 번 실행하고 캐시 채움.

`{summary, rules: [{topic, status, winner, loser, ...}]}` 획득.

### 2. 프롬프트 토큰화

```bash
# 공백 + 한글/영어 단어 분리 + 소문자화 + 마크다운 기호 제거
# 너무 짧은 토큰(2자 미만) 제외
```

### 3. 모드 분기

#### `--cheap` (default)

각 룰에 대해 다음 기준으로 매칭 점수 계산:

- `topic` 과 prompt 키워드 overlap (가중 3x)
- `winner.text` / `loser.text` 와 prompt 키워드 overlap (가중 1x)
- `heading_path` 와 prompt 키워드 overlap (가중 2x)

상위 N개 룰을 트리거 후보로 보고. 각 후보에 trigger_reason 자유서술:
- 예: `"matched keywords: 주문, 테스트"` 또는 `"topic match: 도메인 분리"`

#### `--full`

룰 인벤토리 + 프롬프트를 Haiku 에 단일 호출:

```
System: 다음은 사용자 세션의 활성/덮어쓴 룰 목록이다.
Rules:
- topic: 도메인 분리 원칙 / status: Active / text: ...
- topic: 테스트 작성 규칙 / status: Active / text: ...
...

User prompt: "주문 서비스에 새 기능 추가해줘"

질문: 위 프롬프트를 처리할 때 직접 영향을 줄 룰을 topic 기준으로 나열하라.
각 룰의 trigger_reason 을 한 문장으로 설명하라.
JSON 으로 답변: {"triggered": [{"topic": "...", "trigger_reason": "..."}]}
```

응답 파싱 → 상위 N개로 제한.

### 4. 출력 (default 콘솔)

```
🎯 simulate: "주문 서비스에 새 기능 추가해줘"  [mode: cheap]
─────────────────────────────────────────────────────────
순위 | 주제                | 상태       | 트리거 사유
1   | 도메인 분리 원칙     | ✅ Active  | topic match (도메인)
2   | 테스트 작성 규칙     | ✅ Active  | keyword match (테스트, 작성)
3   | order 서비스 패턴    | ✅ Active  | heading match (order)
4   | @Transactional 규칙 | ⚠ Override | keyword match (서비스)
...

💡 hint: --full 로 다시 돌리면 의미 기반 매칭으로 정확도가 향상됩니다.
         (예상 비용: ~$0.0008)
```

`--json` 면:

```json
{
  "prompt": "...",
  "mode": "cheap"|"full",
  "triggered": [
    {
      "rank": 1,
      "topic": "...",
      "status": "Active"|"Overridden",
      "source": "path:line",
      "trigger_reason": "...",
      "score": 0.85
    }
  ],
  "cost_estimate_usd": 0.0008 | null
}
```

## 구현 노트

- 시뮬레이션 결과는 캐시하지 않음 (프롬프트가 매번 다름 → 캐시 가치 낮음)
- `--cheap` 모드는 외부 호출 없이 분석 캐시 + 정규화만으로 동작 → 빠르고 무료
- `--full` 모드의 LLM 호출은 본 커맨드 본문에서 Claude 가 직접 수행 (별도 API 클라이언트 의존성 없음)
- 본 도구는 **관찰자(observer)** 원칙 유지: 시뮬레이션 결과로 룰을 자동 수정/제안하지 않음. 사용자가 정성적으로 활용.
- v2 검토 항목: hook 스냅샷 기반 "실제 트리거 로그" 와 시뮬레이션 결과 대조해 정확도 검증
