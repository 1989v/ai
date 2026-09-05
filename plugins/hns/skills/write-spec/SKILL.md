---
name: write-spec
description: Use to write spec.md from shaped requirements in an hns spec folder — structure, quality contract, and documentation-only constraints.
user-invocable: false
---

# write-spec

입력: `planning/requirements.md` (+ `planning/visuals/`, `context/open-questions.yml`). 출력: `spec.md`.

## 절차
1. 스펙 폴더 결정(인자 또는 최신 `docs/specs/YYYY-MM-DD-*/`).
2. 관련 `docs/standards/` `docs/conventions/` 와 사전을 읽는다. 열린 `pre-impl` 질문은 스펙에 "미결" 로 명시한다.
3. 재사용할 코드를 찾는다(비슷한 기능·확장 가능한 패턴). 스펙의 `Existing Code to Leverage` 에 경로를 적는다.
4. 작성.

## spec.md 구조
```markdown
# Specification: {Feature}
## Goal                      (1–2문장)
## User Stories              (As a … I want … so that …)
## Specific Requirements     (SR-1 … 각 SR 최대 8항목, 검증 가능한 문장)
## Visual Design             (목업 있을 때)
## Existing Code to Leverage
## Out of Scope
## Open Questions            (pre-impl 미결 항목 링크)
```

## 품질 계약
- 개요는 30초에 읽힌다. 섹션은 독립적으로 읽힌다. 중복 없음.
- 코드 없음 — 요구사항을 서술한다. 인터페이스 이름은 사전 용어를 쓴다.
- TBD/TODO 를 남기지 않는다. 모르는 것은 Open Questions 로.
- 400줄을 넘기면 SR 을 쪼개거나 범위를 줄인 이유를 적는다.

## 완료
`Spec written: {folder}/spec.md → Next: hns:spec-review`
