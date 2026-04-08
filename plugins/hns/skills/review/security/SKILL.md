---
name: review-security
description: Use when reviewing specs for security concerns - checks threat model, OWASP vulnerabilities, sensitive data flow, auth boundaries
user-invocable: false
---

# Security Review

## Seed Discovery Protocol
Apply `@references/review-protocol.md` stages 1-4.

## Checklist
- [ ] 위협 모델링 수행? (STRIDE: Spoofing, Tampering, Repudiation, Information Disclosure, DoS, Elevation of Privilege)
- [ ] 인증/인가 경계 명확? (어떤 Actor가 어떤 리소스에 접근 가능한지)
- [ ] 민감 데이터 흐름 추적? (PII, 결제 정보, 토큰 — 전송/저장/로깅 각 단계)
- [ ] 입력 검증 바운더리 정의? (Injection, XSS, SSRF 방어 지점)
- [ ] 서비스 간 통신 보안? (내부 API 인증, 네트워크 경계)
- [ ] 시크릿/크리덴셜 관리 적절? (하드코딩 금지, 환경변수/Vault 사용)
- [ ] 암호화/해싱 적절? (전송 중 TLS, 저장 시 AES/bcrypt 등)
- [ ] 감사 로깅 고려? (보안 이벤트 추적 가능 여부)

## Commerce-Specific Checks
- [ ] 결제 데이터 PCI-DSS 요건 고려?
- [ ] 주문/재고 변경 시 권한 검증?
- [ ] Rate Limiting / Abuse 방어?

## Verdict
- **SHIP** / **REVISE** (max 2) / **BLOCK**

## Output
`docs/specs/{feature}/context/engineer-review-security.md`
