# NFR Anti-Pattern Scan

## Procedure
1. N+1 쿼리 패턴 탐지 (loop 내 DB 조회)
2. 무제한 리스트 반환 (페이지네이션 없음)
3. 동기 호출 체인이 과도하게 긴 경우
4. 캐시 미적용 빈번 조회
5. 트랜잭션 범위가 과도하게 넓은 경우

## Pass Criteria
- 위 안티패턴 없음 또는 의도적 사유 명시
