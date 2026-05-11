---
description: "Build and evolve the project's domain glossary (ubiquitous language). Grills the user on ambiguous terms, inline-updates agent-os/product/glossary.md, and offers ADRs for hard-to-reverse naming decisions. Trigger: 유비쿼터스 언어, 용어 사전, 도메인 사전, glossary, ubiquitous language, 용어 정리, 용어 충돌"
---

# /hns:glossary

도메인 유비쿼터스 사전(`agent-os/product/glossary.md`)을 점진적으로 구축·갱신한다.
`shape-spec`, `interview-capture`, `review/domain`, `review/architecture`가 이 사전을 기준으로 일관성을 강제하므로, **모든 피처 작업의 기반 자산**이다.

## Usage

```
/hns:glossary                       # 인터랙티브 grilling 세션 (기본)
/hns:glossary --conflict {term}     # 특정 용어 충돌만 빠르게 해소
/hns:glossary --scan                # 코드베이스에서 도메인 용어 후보 자동 추출
/hns:glossary --review              # 기존 glossary와 코드/문서 정합성 점검
```

## Required Inputs
- (선택) 신규 용어 후보 또는 충돌 의심 용어

## Expected Outputs
- `agent-os/product/glossary.md` (없으면 lazy 생성)
- 필요 시 `docs/adr/{nnnn}-{term-decision}.md`
- 멀티 BC 프로젝트는 `docs/context-map.md`

## Reference
이 커맨드는 `@references/language-reference.md`의 포맷·규칙을 따른다.

---

## PHASE 0: Mode Detection

다음 순서로 모드 결정:

1. `--conflict {term}` 플래그가 있으면 → **Conflict Mode**
2. `--scan` 플래그가 있으면 → **Scan Mode**
3. `--review` 플래그가 있으면 → **Review Mode**
4. `agent-os/product/glossary.md`가 없으면 → **Bootstrap Mode**
5. 그 외 → **Grilling Mode**

각 모드는 `skills/commands/glossary/SKILL.md`의 해당 PHASE를 따른다.

---

## PHASE 1: Load Existing Context

1. `agent-os/product/glossary.md` (있으면)
2. `agent-os/product/mission.md` — 도메인 맥락
3. `docs/context-map.md` (있으면, 멀티 BC 판별)
4. `docs/adr/` — 기존 어휘 관련 결정

---

## PHASE 2: Execute Mode

`skills/commands/glossary/SKILL.md`로 위임.

- **Bootstrap**: 코드/문서 스캔 → 후보 추출 → 사용자와 첫 5-10개 용어 grilling → glossary.md 생성
- **Grilling**: 사용자가 가져온 용어 또는 마지막 작업에서 미확정인 용어 → 1개씩 grilling → inline 갱신
- **Conflict**: 충돌 용어에 대한 사용자 질의 → glossary 갱신 또는 사용 측 수정
- **Scan**: 코드베이스 도메인 용어 후보 자동 추출 → 사용자 검토 큐
- **Review**: glossary ↔ 코드 식별자 ↔ spec 문서 3자 정합성 점검

---

## PHASE 3: ADR Decision

용어 결정이 다음 셋 **모두 참**이면 ADR 자동 제안:
1. Hard to reverse
2. Surprising without context
3. Real trade-off

사용자 승인 시 `docs/adr/{nnnn}-{slug}.md` 생성.

---

## PHASE 4: Completion Report

```
Glossary updated: agent-os/product/glossary.md

Added:    {n} terms ({list})
Updated:  {n} terms ({list})
Avoid:    {n} deprecated synonyms recorded
ADRs:     {n} created ({list})
Next:     {recommendation — e.g. "run /hns:start to use these in your next spec"}
```

## Aliases

- "용어 사전 만들어줘"
- "유비쿼터스 언어 정리"
- "이 용어 사전에 등록해줘"
- "용어가 헷갈리는데 정리해줘"
- "build glossary", "domain language"
