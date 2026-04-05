# Aggregate Invariant Trace

## Procedure
1. Spec에서 정의된 Aggregate와 불변식(invariant) 식별
2. 해당 Aggregate의 코드 구현 찾기
3. 불변식이 생성자/팩토리/커맨드 메서드에서 검증되는지 확인
4. 불변식 위반 가능 경로가 있는지 탐지:
   - setter로 직접 상태 변경
   - 불변식 체크 없는 상태 전이

## Pass Criteria
- 모든 불변식이 코드에서 강제됨
- 외부에서 Aggregate 내부 상태 직접 변경 불가
