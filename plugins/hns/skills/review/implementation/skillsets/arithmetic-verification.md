# Arithmetic Verification

## Procedure
1. Spec에서 금액, 수량, 비율 등 산술 연산이 포함된 요구사항 식별
2. 구현 코드에서 해당 연산 찾기
3. 경계 조건 확인: 0, 음수, overflow, 소수점 정밀도
4. BigDecimal 사용 여부 (금액 연산 시 필수)

## Pass Criteria
- 금액 연산에 BigDecimal 사용
- 경계 조건 처리 존재
