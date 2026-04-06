---
description: "Encode a failure pattern as a new harness rule to prevent recurrence"
---

# /hns:evolve

## Purpose
실패 패턴을 하네스 규칙으로 인코딩하여 재발 방지.

## Required Inputs
- Failure description (user provides or detected from recent session)

## Expected Outputs
- New rule added to appropriate harness layer
- Entry in docs/changelog/harness-changelog.md

---

## Trigger Sources
- 테스트 실패 (Ralph Loop 기록)
- spec-review BLOCK 판정
- Ralph Loop 3회 초과
- verify 실패
- 사용자 피드백 ("이거 하지 마")

## Classification → Target

| Failure Type | Target |
|-------------|--------|
| 코딩 실수 (반복 패턴) | lint rule 또는 hook enforcement 추가 |
| 아키텍처 위반 | CLAUDE.md constraint 추가 |
| 스펙 부족/모호 | review skillset 강화 |
| 도구 오용 | agent-behavior 규칙 추가 |

## Execution

1. Ask user to describe the failure (or detect from recent session)
2. Classify failure type
3. 분류 제안 → 사용자 확인
4. Propose rule addition with target location
5. 적절한 하네스 계층에 규칙 생성
6. User approves → create rule → record changelog
7. `docs/changelog/harness-changelog.md`에 기록:
   `[date] [evolve] [변경 내용] [근거: {failure description}]`

## NEVER
- 사용자 확인 없이 CLAUDE.md 수정
- 검증 안 된 패턴을 규칙으로 추가
- 한 번의 실패로 과도한 규칙 추가 (최소한의 제약)
