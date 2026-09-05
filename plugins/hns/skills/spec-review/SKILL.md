---
name: spec-review
description: Use to review an hns spec.md before task creation — six reviewers (architecture, domain, implementation, security, test-strategy, usecase) run in parallel as read-only subagents and return SHIP / REVISE / BLOCK.
user-invocable: false
---

# spec-review

## 절차
1. 스펙 폴더와 `spec.md` 를 확정한다.
2. 6개 차원을 **한 번에 병렬로** 디스패치한다 — `Agent` 도구, `subagent_type: hns:spec-reviewer`, 각 프롬프트에 스펙 경로 · 차원 · 체크리스트 경로 `${CLAUDE_PLUGIN_ROOT}/skills/spec-review/reviewers/{dim}/checklist.md` 를 넣는다.
   차원: `architecture` `domain` `implementation` `security` `test-strategy` `usecase`.
3. 결과 집계.

## 판정 규칙 (`references/review-protocol.md`)
- 하나라도 **BLOCK** → 사람에게 보고, 진행 중단. 스펙 결정 + 코드/문서 위반 이중 근거가 없는 BLOCK 은 REVISE 로 강등.
- **REVISE** → 이슈를 모아 `spec.md` 를 수정하고 해당 차원만 재리뷰. 최대 2회, 그 뒤엔 BLOCK 으로 취급.
- 전부 **SHIP** → 진행.

## 출력
```
| Reviewer | Verdict | Issues |
|---|---|---|
| Architecture | SHIP | 0 |
| … | … | … |
Overall: SHIP | REVISE | BLOCK
Action: {다음 행동}
```
리뷰 원문은 각 리뷰어가 `context/engineer-review-{dim}.md` 에 남긴다.

## 리뷰어 자료
`reviewers/{dim}/checklist.md` 가 체크리스트, `reviewers/{dim}/skillsets/*.md` 가 항목별 절차. 도메인 리뷰는 `references/language-reference.md`, 아키텍처 리뷰는 같은 문서 §3(모듈 깊이·seam) 을 참조한다.
