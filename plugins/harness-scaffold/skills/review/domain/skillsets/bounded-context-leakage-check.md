# Bounded Context Leakage Check

## Procedure
1. Spec에서 정의된 바운디드 컨텍스트 경계를 식별
2. 해당 컨텍스트의 패키지/모듈 경계를 코드에서 확인
3. 경계를 넘는 직접 참조가 있는지 Grep으로 탐지:
   - 다른 컨텍스트의 Entity/Repository 직접 import
   - 다른 컨텍스트의 DB 테이블 직접 접근
4. 발견 시 file:line 증거와 함께 보고

## Pass Criteria
- 컨텍스트 간 통신은 API/이벤트만 사용
- 직접 import/DB 공유 없음
