---
name: code-explore
description: Use when tracing code paths related to an API issue - explores both source code and docs/ to find root cause, referencing business rules and architecture docs alongside implementation
---

# Codebase Explorer

## Overview

코드베이스와 docs/를 함께 탐색하여 이슈 관련 로직을 추적한다.

## 탐색 전략

### 1. 진입점 식별
- API 엔드포인트 → Controller/Router 찾기
- 에러 메시지/스택트레이스 → 코드 위치 매핑

### 2. 호출 흐름 추적
Controller → UseCase/Service → Repository/Client 순으로 추적:
- 비즈니스 로직 분기 (if/when 조건)
- 예외 처리 경로
- 외부 호출 지점

### 3. docs/ 참조
코드 분석과 병행하여:
- `docs/policies/` — 비즈니스 규칙이 코드에 올바르게 반영되었는지
- `docs/architecture/` — 설계 의도와 실제 구현의 불일치
- `CLAUDE.md` — 프로젝트 컨벤션 위반 여부

### 4. 원인 판단
- 코드 로직 오류 발견 → 수정안 제시
- 데이터/환경 문제 의심 → log-query 필요 판단
- 설계 의도와 구현 불일치 → docs 근거와 함께 보고

## 출력 형식

```
=== Code Analysis ===

Entry: OrderController.createOrder (order/app/.../controller/OrderController.kt:45)
Flow: CreateOrderUseCase → OrderService.create → OrderRepository.save
Suspect: OrderService.kt:89 - 재고 차감 로직에서 동시성 미처리

docs/policies/inventory-rules.md:
   "재고 차감은 비관적 락으로 처리해야 함" — 코드에 락 미적용

Verdict: 코드 이슈 (동시성 처리 누락)
```

## Integration

- **Called by:** ai-debugger:debug-agent
- **Not standalone** — debug-agent 플로우 내에서만 호출
