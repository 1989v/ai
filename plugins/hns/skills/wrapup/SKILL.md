---
name: wrapup
description: Use at the end of a work session to write an evidence-based retrospective (what went well, where blocked, what to change) and route repeatable failures to /hns:evolve.
when_to_use: 세션 정리, 회고, 작업 마무리, session wrapup, retrospective
argument-hint: "[--spec path]"
---

# /hns:wrapup

## 1. 수집
`context/progress.md`(있으면) · `git log --oneline -20` · 검증 리포트(verify · validate · drift-check) · 이 대화의 오류·재시도·블로커.

## 2. 회고 문서 — `docs/retrospectives/{date}-session.md`
```markdown
# Session Retrospective — {date}
## What Went Well      | Item | Evidence (커밋·테스트 결과) | Impact |
## Where Blocked       | Item | Root Cause | Duration | Resolution |
## What to Change      | Suggestion | Risk LOW/MEDIUM/HIGH | Effort | Action |
```

## 3. 실패 분류 → evolve
| 유형 | 신호 | 대상 (`hns:evolve` 표) |
|---|---|---|
| 반복 코딩 실수 | 같은 오류 2회+, 검증 루프 3회 초과 | 훅 또는 규칙 |
| 아키텍처 위반 | validate --code FAIL | `.claude/rules/` 또는 CLAUDE.md |
| 스펙 부족 | drift-check FAIL, 구현 중 재해석 | 리뷰어 체크리스트 |
| 도구 오용 | 서브에이전트 과용, 수동 반복 | `hns:agent-behavior` |
| 프롬프트 품질 | 스킬이 의도와 다른 결과 | 해당 SKILL.md |
| 사용자 교정 | "이렇게 하지 마" | auto memory |

LOW 리스크 항목은 사용자 승인 후 `/hns:evolve` 로 바로 반영하고, MEDIUM/HIGH 는 문서에만 남긴다. 적용 결과를 회고 문서 `## Self-Healing Actions Taken` 표에 적는다.
