---
name: shape-spec
description: Use to turn a feature request into clear, testable requirements before any spec is written — creates the spec folder and runs the ambiguity-gated interview in the main conversation.
user-invocable: false
---

# shape-spec

메인 컨텍스트에서 실행한다(서브에이전트는 사용자에게 질문할 수 없다).

## 산출물
`docs/specs/YYYY-MM-DD-{kebab-name}/` 아래 `planning/initialization.md` · `planning/requirements.md` · `planning/test-quality.md` · `planning/shaping-state.yml` · `context/open-questions.yml`.

## 1. 초기화
```bash
SPEC="docs/specs/$(date +%Y-%m-%d)-{name}"; mkdir -p "$SPEC"/{planning/visuals,context,implementation,verifications}
```
사용자 요청 원문을 `planning/initialization.md` 에 그대로 저장한다. `planning/shaping-state.yml` 이 이미 있으면 마지막 라운드부터 재개한다.

## 2. 컨텍스트
- `docs/product/mission.md` · `roadmap.md` · `glossary.md`(있으면). 사전의 `Avoid:` 동의어를 사용자가 쓰면 먼저 바로잡는다.
- 브라운필드 판정: 관련 소스가 있고 요청이 그것을 고치는 것이면 브라운필드 → `Explore` 로 관련 코드를 먼저 지도화한다. **코드가 답하는 것은 묻지 않는다**; 코드 때문에 생긴 질문은 파일·심볼을 인용한다.
- 이전 스펙 `docs/specs/*/planning/requirements.md` 에서 이미 확정된 사실을 재활용한다.

## 3. 인터뷰 — `references/ambiguity-gating-protocol.md`
- 임계값 `hns.shape.ambiguityThreshold` (프로젝트 → 사용자 settings → 기본 0.2) 를 밝힌다.
- Round 0 토폴로지(1–6 컴포넌트) 확인 → 매 라운드 가장 약한 차원 하나에 **한 질문**(`AskUserQuestion`, 선택지 + 자유 입력) → 점수 갱신·온톨로지 추적 → 챌린지 모드(R4 Contrarian / R6 Simplifier / R8 Ontologist) → 정지 조건(R3+ 조기 종료, R10 소프트, R20 하드, 정체).
- 반드시 다루는 것: 재사용할 기존 코드, 실패 의미(재시도·멱등성), 관측 방법(어떻게 디버깅할지), 범위 밖, 시각 자료(`planning/visuals/` 를 `ls` 로 확인하고 있으면 Read).
- 답은 해석하지 말고 그대로 적는다.

## 4. 테스트 전략 — `planning/test-quality.md`
시나리오를 unit / integration / component / e2e 에 배정하고 critical path 를 표시한다. 스택 중립.

## 5. 열린 질문 — `context/open-questions.yml`
미해결 항목을 `pre-impl` 로 시드한다(`hns:spec-evolution` 분류). 없으면 빈 레지스트리.
인터뷰에서 나온 도메인 용어는 `/hns:glossary` 후보로 넘긴다. 여기서 두 번째 사전을 만들지 않는다.

## 완료
```
Spec shaped: {folder}  (ambiguity {score}%, threshold {t}, rounds {n})
Next: hns:write-spec
```
