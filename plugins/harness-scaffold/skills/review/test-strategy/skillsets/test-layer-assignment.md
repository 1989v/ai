# Test Layer Assignment

## Procedure
1. Tasks에 정의된 각 테스트의 레이어 확인
2. 테스트 대상에 적합한 레이어인지 판단:
   - 순수 로직 → unit
   - Port/Adapter 연동 → integration
   - API 전체 흐름 → component/e2e
3. 레이어 불일치 보고:
   - DB 쿼리 테스트가 unit으로 분류된 경우
   - 순수 계산 테스트가 e2e로 분류된 경우

## Pass Criteria
- 테스트 레이어와 대상의 성격이 일치
- 불필요하게 무거운 레이어 사용 없음
