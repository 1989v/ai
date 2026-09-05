# Dependency Direction Analysis

## Procedure
1. Spec에서 새로 추가/변경되는 모듈 간 의존 관계 식별
2. import 문 분석으로 의존 방향 확인:
   - domain → infrastructure (위반)
   - application → infrastructure (위반)
   - infrastructure → domain (정상)
3. 위반 경로 file:line 증거 수집

## Pass Criteria
- 의존 방향이 항상 안쪽(domain) 방향
- 역방향 의존 없음
