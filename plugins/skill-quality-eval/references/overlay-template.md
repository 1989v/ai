# Overlay Template (JSON 강제 평가 모드)

`forker/` 가 `source-skill/SKILL.md` 끝에 부착하는 **평가 모드 overlay** 의 표준 문구.

## 부착 방식

source-skill/SKILL.md 의 본문 끝에 다음 블록을 그대로 추가하여 forked-skill/SKILL.md 를 만든다. SKILL.md frontmatter 는 손대지 않는다.

## 표준 Overlay

`fork-and-invoke.sh` 는 `<!-- OVERLAY_BEGIN -->` 와 `<!-- OVERLAY_END -->` 사이의 모든 내용을 추출해서 SKILL.md 뒤에 붙인다.

<!-- OVERLAY_BEGIN -->
---

## ⚠️ EVAL MODE OVERRIDE (skill-quality-eval)

이 SKILL.md 는 평가 모드용 fork 본이다. **본문에 정의된 분석 절차·룰·phase·검증 단계는 그대로 수행하라** — overlay 는 본문 동작을 대체하지 않고 **최종 응답의 출력 형식만 강제**한다.

즉:
- 본문이 "코드를 읽어라" 하면 → 실제로 read tool 로 fixture/code 를 읽는다
- 본문이 "8-phase 분석을 수행하라" 하면 → 그대로 8-phase 수행한다
- 본문이 "tool 호출을 X 회 한다" 하면 → 그대로 X 회 호출한다
- **단 사용자에게 자연어로 보고하는 단계는 생략**하고, 분석 결과만 아래 schema 의 JSON 으로 응답한다

### Output Contract

1. **분석 절차 수행 후, 자연어 보고 단계 생략.** 설명, 해설, markdown, 코드펜스, 이모지, 프롬프트 메아리 일체 출력 금지.
2. **출력은 단일 JSON object 하나.** 다음 schema 에 정확히 부합해야 한다:

```json
{{OUTPUT_SCHEMA_JSON}}
```

3. **모르는 필드는 추측 금지.** schema 가 optional 로 둔 필드는 누락 가능, required 는 반드시 채워야 한다.
4. **여러 답변 후보가 있어도 단일 객체로 응답.** 평가 매칭 정책이 multi-acceptable 을 지원하지 않는 v0.1 단계에서는 가장 확신 있는 단일 답만.

### 평가 컨텍스트

- `skill_id`: `{{SKILL_ID}}`
- `snapshot_id`: `{{SNAPSHOT_ID}}`
- `case_id`: `{{CASE_ID}}`
- `eval_session`: 사람 사용자가 아닌 평가 시스템의 호출이다. 정답 컨펌·해설·후속 질문 일체 불필요.

### 실패 모드

JSON 형식이 깨지거나 schema 검증을 통과하지 못하면 runner 가 retry 한다. retry 한도 (기본 N=2) 도달 시 케이스 fail 로 카운트된다.

---
<!-- OVERLAY_END -->

## 변수 치환

`{{...}}` 마커는 `forker/` 가 평가 진입 시 채운다.

| 마커 | 출처 |
|---|---|
| `{{OUTPUT_SCHEMA_JSON}}` | `goldset/{skill-id}/schema/output.schema.json` 의 raw 내용 (pretty-printed) |
| `{{SKILL_ID}}` | 평가 대상 스킬 ID (예: `hns-glossary`) |
| `{{SNAPSHOT_ID}}` | 현재 스냅샷 디렉토리 이름 (예: `2026-05-22-baseline`) |
| `{{CASE_ID}}` | 현재 케이스 ID (예: `case-001`) |

## Native `--json-schema` 와의 관계

Overlay 는 **스킬 내부에서의 자기 강제** 가이드, `claude --json-schema` 는 **CLI 단의 외부 강제**. **둘 다 적용 = 이중 안전망.**

| 메커니즘 | 효과 |
|---|---|
| Overlay 만 | 스킬이 자발적으로 JSON 출력 시도. LLM 변동성에 노출 |
| `--json-schema` 만 | CLI 가 강제 검증, 위반 시 retry |
| 둘 다 (default) | 스킬·CLI 양측 강제, format-fail 거의 발생 안 함 |

## 주의

- Overlay 본문의 한국어 문구는 LLM 친화 표현이라 그대로 유지 권장
- `OUTPUT_SCHEMA_JSON` 은 항상 JSON 코드펜스 안에 넣어 LLM 이 schema 구조를 정확히 파싱하도록
- Overlay 길이가 30KB 를 넘으면 매우 큰 schema 신호 → schema 단순화 검토
