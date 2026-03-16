---
name: log-query
description: Use when retrieving IO logs from Redis or other log stores - performs 2-phase query (key scan then selective detail fetch) to minimize context cost
---

# IO Log Query

## Overview

적재된 IO 로그를 2단계 전략으로 조회한다. 컨텍스트 비용을 최소화하면서 필요한 데이터만 정밀 조회.

## 2단계 조회 전략

### Phase 1: 키 스캔 (저비용)

```bash
# Redis에서 traceId의 모든 IO 키 조회
redis-cli SMEMBERS io:index:{traceId}
```

결과 예시:
```
io:abc-123:HTTP:OrderController.createOrder:45
io:abc-123:DB:OrderRepository.save:128
io:abc-123:EXTERNAL_API:PaymentClient.charge:67
io:abc-123:KAFKA:OrderEventProducer.send:89
io:abc-123:REDIS:CartCacheAdapter.get:34
```

키 이름만으로 판단:
- 어떤 메서드가 호출되었는지
- IO 타입이 무엇인지
- 코드 어느 라인에서 발생했는지

### Phase 2: 선택적 값 조회 (필요 시만)

code-explore 결과와 대조하여 의심 구간의 키만 선택:

```bash
# 특정 IO 이벤트 상세 조회
redis-cli HGETALL io:abc-123:DB:OrderRepository.save:128
```

## 조회 필터링 기준

- **IO 타입별**: DB만, EXTERNAL_API만 등
- **메서드명**: 특정 클래스/메서드 패턴
- **에러 여부**: error 필드가 비어있지 않은 것만
- **시간 범위**: invokedAt 기준

## Stale 키 처리

TTL 만료로 Hash는 삭제되었지만 인덱스 Set에 남은 키 → HGETALL 결과가 비어있으면 무시.

## Integration

- **Called by:** ai-debugger:debug-agent (코드 분석으로 불충분할 때)
- **Not standalone** — debug-agent 플로우 내에서만 호출
