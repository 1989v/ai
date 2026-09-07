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
3. **심판** — 발견이 하나라도 있으면 `hns:review-verdict` 에이전트를 1회 호출해 전건의 유지/강등/기각을 받는다(입력: 발견 전건 · 스펙 경로 · 표준 경로). 발견 0건이면 생략.
4. 판정대로 집계한다.

> **메인은 발견을 직접 강등·기각하지 않는다.** 스펙을 쓴 세션이 그대로 구현을 지휘하므로, 여기서의 재량 기각은 재리뷰 루프가 못 잡는 유일한 편향이다(부실 수정은 다음 라운드가 재검출하지만, 기각은 같은 재량이 반복 적용된다). 심판 판정을 재량 없이 따르고, 판정이 틀렸다고 보면 근거를 들어 사용자에게 올린다.
> **서브에이전트를 못 부르면 메인이 대신 리뷰하지 않는다** — 그 자리에서 멈추고 사유를 알린다. 저자가 검증자를 겸하면 이 단계의 존재 이유가 사라진다.

## 판정 규칙 (`references/review-protocol.md`)
- 하나라도 **BLOCK**(심판이 유지한 것) → 사람에게 보고, 진행 중단. 이중 근거(스펙 결정 + 코드/문서 위반) 검사는 심판이 한다.
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

## 지식베이스
`HNS_KB_PATH` 가 설정돼 있으면 각 리뷰어 프롬프트에 "`hns:kb` 로 스펙의 기술 결정 키워드를 조회해 개념 페이지를 표준으로 취급하고 `[[page]] (볼트, updated)` 로 인용" 을 넣는다.

## 리뷰어 자료
`reviewers/{dim}/checklist.md` 가 체크리스트, `reviewers/{dim}/skillsets/*.md` 가 항목별 절차. 도메인 리뷰는 `references/language-reference.md`, 아키텍처 리뷰는 같은 문서 §3(모듈 깊이·seam) 을 참조한다.
