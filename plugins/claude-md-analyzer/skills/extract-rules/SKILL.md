---
name: extract-rules
description: "주어진 CLAUDE.md / 메모리 / settings 파일 목록에서 룰 후보를 추출해 {source, text, heading_path, last_modified} JSON 으로 반환한다. fs 어댑터의 fallback 분석 및 evidence verifier 의 ground-truth 인덱스로 사용. user-invocable: false."
---

# extract-rules (background skill)

`/claude-md:analyze` 가 fs 모드 fallback 또는 evidence verifier 의 ground-truth 인덱스가 필요할 때 호출되는 백그라운드 스킬.

## 입력

레이어 인벤토리 JSON (collect-layers.sh 출력) — 각 항목 `{ path, layer, bytes, modified, token_estimate }`

## 출력

룰 항목 배열 JSON:

```json
[
  {
    "source": "/abs/path/CLAUDE.md:42-45",
    "layer": "project",
    "heading_path": ["Conventions", "Test"],
    "text": "도메인 테스트는 Kotest BehaviorSpec + MockK 사용",
    "last_modified": "2026-05-21T11:00:00Z"
  }
]
```

## 추출 알고리즘

각 파일 타입별 처리:

### markdown 파일 (CLAUDE.md, memory/*.md)
1. heading (`#`, `##`, `###`...) 별로 섹션 분할
2. 각 섹션 내에서 다음 텍스트를 룰 후보로 식별:
   - bullet (`- `, `* `, `1. `, `2. `) 의 imperative sentence ("...해야 한다", "...금지", "...우선", "must", "never", "always" 등)
   - 강한 키워드 포함 문장 (`반드시`, `필수`, `금지`, `규칙`, `Rule`, `MUST`, `NEVER`)
3. heading_path 는 상위 heading 들을 누적 (예: `["Architecture", "Clean Architecture"]`)
4. source 의 line 범위는 룰 텍스트의 실제 시작/끝 라인 번호 (markdown 파서가 보장)

### settings.json (`.claude/settings.json`, `settings.local.json`)
1. JSON 최상위 키별로 룰 후보 추출
2. 각 키-값 쌍을 자연어로 변환 (예: `permissions.allow.[0] = "Bash(rg:*)"` → "Bash(rg:*) 명령어 허용")
3. heading_path 는 `["settings", "<key path>"]`
4. source 의 line 은 jq + grep 으로 추출

### 빈 파일 / 코드블록 / 표
- 룰 후보로 간주하지 않음 (skip)
- 단, settings.json 의 hooks 항목은 룰로 간주 (자동 동작 정의이므로)

## 구현 노트

- 본 스킬은 의미 매칭/클러스터링 안 함. 단순 추출만.
- introspect 어댑터가 메인일 때는 호출되지 않으며, evidence verifier 가 검증용 인덱스로 호출.
- fs 어댑터 단독(`--source=fs`) 일 때는 추출 결과 위에 keyword + TF-IDF 클러스터링이 별도 단계에서 수행됨 (M2).
