# Ubiquitous Language Drift Scan

## Procedure
1. Spec에서 사용된 도메인 용어 목록을 추출
2. 코드베이스에서 해당 용어가 동일하게 사용되는지 Grep으로 확인
3. 동의어/약어/불일치 패턴 탐지:
   - spec: "주문 취소" vs code: "orderCancel" (OK)
   - spec: "환불" vs code: "refund" + "cancel" (drift)
4. 클래스명, 메서드명, 변수명에서 용어 일관성 확인

## Pass Criteria
- spec 용어와 코드 용어 1:1 매핑 가능
- 동일 개념에 다른 이름 없음
