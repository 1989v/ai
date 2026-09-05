# Threat Model Analysis (STRIDE)

## Procedure
1. Actor 식별: 외부 사용자, 내부 서비스, 관리자 등 모든 접근 주체 나열
2. STRIDE 분석 수행:
   - **Spoofing**: 인증 우회 가능한 진입점?
   - **Tampering**: 요청/응답/저장 데이터 변조 가능 지점?
   - **Repudiation**: 부인 방지 불가능한 중요 액션? (결제, 주문 상태 변경)
   - **Information Disclosure**: 민감 정보 노출 경로? (에러 메시지, 로그, API 응답)
   - **Denial of Service**: 리소스 고갈 공격 가능 지점? (무제한 요청, 대량 업로드)
   - **Elevation of Privilege**: 권한 상승 가능 경로? (IDOR, role 우회)
3. 각 위협에 대해 기존 방어 메커니즘 확인 (gateway 필터, 인증 미들웨어 등)
4. 미방어 위협 목록 작성

## Pass Criteria
- 모든 STRIDE 카테고리 검토 완료
- 미방어 위협에 대한 대응 방안 명시 또는 수용 사유 기술
