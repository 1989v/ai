# Module Boundary Impact Scan

## Procedure
1. Spec에서 변경되는 모듈 경계 식별
2. 해당 모듈의 public API(controller, port) 변경 사항 확인
3. 다른 모듈에서 해당 API를 사용하는 곳 Grep
4. Breaking change 여부 판단

## Pass Criteria
- 모듈 경계 변경 시 영향 받는 곳 모두 식별
- Breaking change 시 마이그레이션 계획 존재
