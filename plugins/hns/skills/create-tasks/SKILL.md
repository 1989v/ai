---
name: create-tasks
description: Use to break an approved hns spec.md into dependency-ordered task groups with focused tests and executable verification steps — produces tasks.md.
user-invocable: false
---

# create-tasks

입력: `spec.md` (+ `planning/requirements.md`, `planning/test-quality.md`). 출력: `tasks.md`.

## 규칙
- 그룹은 레이어/스킬 단위(DB · API · Frontend · Test review). 기초 → 의존 순.
- 그룹마다 `dependencies` · `phase` · `required_skills` 메타데이터, 시작은 테스트 작성(2–8개), 끝은 **실행 가능한 검증 명령**.
- 테스트는 핵심 행동만. 기능 전체 16–34개 안팎. 검증은 새로 쓴 테스트만 돌린다(전체 스위트는 verifier 가).
- 프로젝트 표준(`docs/standards/` `docs/conventions/` `.claude/rules/`)을 인용한다.
- 600줄을 넘기면 스펙이 너무 크다 — 스펙 분할을 제안한다.

## tasks.md 형식
```markdown
# Task Breakdown: {Feature}
## Overview
Total Task Groups: {N}

### Task Group 1: {name}
**Dependencies:** None | Task Group X
**Phase:** {phase-id}
**Required Skills:** {list}
- [ ] 1.0 Complete {group}
  - [ ] 1.1 Write 2–8 focused tests for {behavior}
  - [ ] 1.2 {implementation sub-task}
  - [ ] 1.N Verify: `{concrete command}`
**Acceptance Criteria:**
- {measurable}

## Execution Order
1. {dependency-ordered list}
```
체크박스는 검증 통과 후에만 표시한다.

## 완료
`Tasks created: {folder}/tasks.md ({N} groups) → Next: hns:implement-tasks`
