# Concurrent Write Simulation

## Procedure
1. Spec에서 동시 쓰기가 발생할 수 있는 시나리오 식별
2. 해당 코드의 동시성 제어 메커니즘 확인:
   - Optimistic locking (@Version)
   - Pessimistic locking
   - Redis distributed lock
3. Race condition 가능 경로 분석

## Pass Criteria
- 동시 쓰기 시나리오에 적절한 locking 존재
- Lost update 방지 메커니즘 확인
