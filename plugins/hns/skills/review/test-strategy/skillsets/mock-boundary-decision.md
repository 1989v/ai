# Mock Boundary Decision

## Procedure
1. Spec에서 외부 의존성(DB, API, 메시징) 식별
2. 각 의존성의 mock 여부 판단:
   - Domain 테스트: mock 금지 (순수 단위)
   - Application 테스트: Outbound Port만 mock
   - Integration 테스트: 외부 API만 mock, DB는 실제
3. Over-mocking 패턴 탐지:
   - 내부 서비스를 mock하는 경우
   - 테스트 대상 자체를 mock하는 경우

## Pass Criteria
- mock 경계가 레이어별로 일관
- 과도한 mock 없음
