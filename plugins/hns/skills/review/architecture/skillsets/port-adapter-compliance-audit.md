# Port-Adapter Compliance Audit

## Procedure
1. Application 레이어의 Outbound Port(인터페이스) 목록 확인
2. Infrastructure 레이어에 대응하는 Adapter(구현체) 존재 여부 확인
3. Application이 Adapter를 직접 참조하는 경우 탐지
4. Port 없이 직접 Repository/Client를 사용하는 경우 보고

## Pass Criteria
- 모든 외부 의존은 Port 인터페이스를 통해 접근
- Application → Adapter 직접 참조 없음
