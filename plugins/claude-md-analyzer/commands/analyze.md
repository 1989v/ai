---
description: "현재 working directory 기준으로 글로벌/프로젝트/로컬 CLAUDE.md·메모리·settings 가 합성된 결과를 분석한다. 어떤 룰이 살아남았는지(Active) / 덮어써졌는지(Overridden) / 충돌 해소 근거를 가시화. 자연어 트리거: claude.md 분석, 프롬프트 합성 확인, 룰 충돌 점검."
argument-hint: "[--source=auto|introspect|fs] [--strict|--warn|--loose] [--all|--by-topic|--tree|--unverifiable] [--no-cache|--force]"
---

# /claude-md:analyze

세션의 합성된 CLAUDE.md/메모리/settings 컨텍스트를 introspect 하여, **살아있는 룰(first-win)** 과 **덮어써진 룰(Overridden)** 을 분류하고 충돌 해소 근거를 보고한다.

## 트리거

- `/claude-md:analyze` — auto 모드 + warn evidence + 하이브리드 디폴트 뷰
- `/claude-md:analyze --strict` — fs verifier 통과 항목만 리포트
- `/claude-md:analyze --all` — Active 룰까지 전체 표시
- `/claude-md:analyze --force` — 캐시 무시하고 재분석

## 옵션

| Flag | 의미 |
|------|------|
| `--source=auto` (default) | introspect + fs evidence 검증 (M1: 동일) |
| `--source=introspect` | introspect 단독, fs 검증 생략 |
| `--source=fs` | fs 정적 클러스터링 fallback |
| `--source=hook` | hook 로그 기반 (M3 — 미구현 시 fs 로 폴백) |
| `--strict` | evidence 검증 실패 항목 결과에서 제외 |
| `--warn` (default) | unverifiable 항목 ⚠ 마킹 후 결과 포함 |
| `--loose` | 자유형 인용, fs 검증 생략 |
| `--all` | Active 룰 전체 표시 (default: Conflict-only) |
| `--by-topic` | 주제별 대시보드 |
| `--tree` | 레이어 트리 |
| `--unverifiable` | evidence 검증 실패 항목만 |
| `--no-cache` / `--force` | 캐시 무시 |

## 실행 흐름

### 1. 레이어 인벤토리 수집

`scripts/collect-layers.sh "$PWD"` 를 호출하여 다음 파일들을 JSON 으로 받는다:

- `~/.claude/CLAUDE.md`
- `~/.claude/memory/MEMORY.md`, `~/.claude/memory/*.md`
- `~/.claude/settings.json`
- `~/.claude/projects/{slug}/CLAUDE.md` (slug = cwd 인코딩)
- `~/.claude/projects/{slug}/MEMORY.md` 및 `~/.claude/projects/{slug}/memory/*.md`
- `~/.claude/projects/{slug}/settings.json`, `settings.local.json`
- `$PWD/CLAUDE.md`, `$PWD/.claude/CLAUDE.md`, `$PWD/.claude/settings.json`, `$PWD/.claude/settings.local.json`
- 부모 디렉토리 체인 (홈까지) 의 `CLAUDE.md`
- 서비스/하위 디렉토리의 `*/CLAUDE.md` (cwd 하위 2 depth)

각 항목: `{ path, layer, bytes, modified, token_estimate }`

### 2. 캐시 확인

`--no-cache` / `--force` 가 아니면:

1. `scripts/hash-context.sh <인벤토리 JSON>` → 단일 SHA256 해시
2. `cache-manager` skill 호출: `~/.claude/projects/{slug}/cma-cache/{hash}.json` 존재하면 즉시 반환 후 종료
3. 없으면 진행

### 3. Introspect (메인)

`--source` 가 `introspect` / `auto` 면 self-analysis 수행. **너 자신이 받은 system context 와 1단계 인벤토리를 기반으로** 다음을 결정한다:

- 각 레이어 파일에서 사용자 지시/룰을 추출
- 같은 주제(동의어/패러프레이즈 포함) 룰끼리 짝지움 — LLM 의미 매칭에 위임
- Claude Code 우선순위 규칙(local > project > user > global, settings hierarchy)에 따라 승자 결정
- 각 룰을 `Active` / `Overridden` 로 분류

**출력 형식 (structured)** — 다음 JSON 스키마 엄격 준수:

```json
{
  "summary": {
    "total_rules": 42,
    "conflicts": 5,
    "unverifiable": 0,
    "stale": 0
  },
  "rules": [
    {
      "topic": "테스트 작성 규칙",
      "status": "Overridden",
      "winner": {
        "source": "/abs/path/CLAUDE.md:42",
        "text": "도메인 레이어만 테스트"
      },
      "loser": {
        "source": "/Users/.../.claude/CLAUDE.md:17",
        "text": "테스트 항상 작성"
      },
      "resolution": "프로젝트 CLAUDE.md > 글로벌 CLAUDE.md"
    }
  ]
}
```

- `topic` 은 한글 자유서술 가능 (짧고 식별 가능하게)
- `source` 는 **반드시 절대경로:라인** 형식 — fs verifier 가 이 인용을 검증
- `Active` 룰은 `loser` / `resolution` 없음
- `Overridden` 룰은 `winner` 가 현재 적용 중인 룰, `loser` 는 덮어써진 룰

`--source=fs` 면 introspect 대신 `extract-rules` skill 을 호출해 정적 인벤토리만 사용 (의미 매칭 정확도 낮음, fallback).

### 4. Evidence 검증

`--strict` / `--warn` / `--loose` 에 따라:

- `--loose`: 검증 생략, introspect 결과 그대로 표시
- `--warn` / `--strict`: 각 `source(file:line)` 인용에 대해 `verify-evidence` skill 호출
  - skill 은 `scripts/verify-source.sh` 로 실제 파일·라인을 grep 검증
  - 검증 실패 시:
    - `--warn`: 해당 룰에 `unverifiable=true` 마킹, 결과 포함
    - `--strict`: 해당 룰 제거, `summary.rejected` 카운트 증가

### 5. Dead / Stale 휴리스틱

`scripts/detect-dead-stale.sh <rules.json> "$PWD"` 호출 → 각 룰에 다음 필드 주입:

- `stale_reason`: `path-missing` / `line-out-of-range` / null
- `dead_reason`: `path-bound-irrelevant` / `permanently-overridden` / null

추가로 introspect 가 식별한 `unreferenced` 후보(룰 텍스트의 키워드가 현재 cwd 코드베이스에 0회 등장)는 introspect 단계에서 직접 `dead_reason="unreferenced"` 로 마킹한다. 키워드 추출은 LLM 의미 매칭에 위임.

summary 의 `stale` / `dead` 카운트가 자동 업데이트된다.

### 6. 캐시 저장

검증 + Dead/Stale 태깅 끝난 최종 JSON 을 `~/.claude/projects/{slug}/cma-cache/{hash}.json` 에 저장.

### 7. 출력 렌더링

`references/output-format.md` 명세에 따라 디폴트는 **하이브리드 (요약 헤더 + Conflict-only)**:

```
📊 42 rules / ⚠ 5 conflicts / ❓ 0 unverifiable / 🗂 0 stale
─────────────────────────────────────────────────────────
주제                  | 승자                          | 패자                                  | 근거
테스트 작성 규칙       | CLAUDE.md:42 (project)        | ~/.claude/CLAUDE.md:17 (global)       | project > global
@Transactional 규칙   | order/CLAUDE.md:88 (local)    | CLAUDE.md:120 (project)              | local > project
...
```

`--all` 면 Active 룰까지 추가 섹션으로 출력.
`--by-topic` / `--tree` / `--unverifiable` 는 M2 구현 — 현재는 stub (옵션 수신만, 동작은 default 와 동일 + 안내 메시지).

## M1 범위 제한 (현재 구현)

- `--source=auto|introspect|fs` 만 동작. `hook` 은 자동 fs 폴백 + 안내.
- `--strict` / `--warn` / `--loose` 동작.
- `--all` 동작. `--by-topic` / `--tree` / `--unverifiable` 는 M2 에서 활성화.
- Dead/Stale 검출은 M2.

## 산출물

- 콘솔 표 (default)
- JSON export (옵션 `--json` — M1 부터 동작): `{"summary":{...}, "rules":[...]}`
- markdown 리포트 (옵션 `--report=path.md` — M2)
