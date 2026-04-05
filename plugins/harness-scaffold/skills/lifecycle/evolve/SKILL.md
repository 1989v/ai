---
name: evolve
description: Use when a failure pattern is detected and needs to be encoded as a new harness rule to prevent recurrence
---

# Harness Evolution

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

## Process
1. 실패 패턴을 사용자에게 설명
2. 분류 제안 → 사용자 확인
3. 적절한 하네스 계층에 규칙 생성
4. `docs/changelog/harness-changelog.md`에 기록:
   `[date] [evolve] [변경 내용] [근거: {failure description}]`

## NEVER
- 사용자 확인 없이 CLAUDE.md 수정
- 검증 안 된 패턴을 규칙으로 추가
- 한 번의 실패로 과도한 규칙 추가 (최소한의 제약)
