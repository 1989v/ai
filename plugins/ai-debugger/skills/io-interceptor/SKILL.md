---
name: io-interceptor
description: Use when setting up IO capture in a target service - injects unified AOP interceptor with profile-based activation and @IOTraceable annotation
---

# IO Interceptor Setup

## Overview

대상 서비스에 통합 AOP 기반 IO 인터셉터를 주입한다. 서비스의 코드 컨벤션을 준수하며,
`@Profile("debug-trace")`로 활성화하여 평상시 성능 영향 없음.

## 아키텍처: 통합 AOP

5개 개별 인터셉터 대신 **1개 AOP Aspect**로 모든 IO 캡처:

| 컴포넌트 | 역할 |
|---------|------|
| `TraceIdFilter` | X-Trace-Id → MDC 설정만 (경량) |
| `IOSnapshotAspect` | 모든 IO 캡처 + 적재 (통합 AOP) |
| `IOTraceLogAppender` | 애플리케이션 로그 캡처 (WARN 이상) |
| `RedisIOLogStore` | Redis 저장/조회 |
| `@IOTraceable` | 커스텀 어노테이션 (명시적 opt-in) |

## 타겟 식별 3단계

```
execution(* org.springframework.data.repository.Repository+.*(..))  ← 1. Spring Data (자동)
|| @within(IOTraceable)                                              ← 2. 어노테이션 (명시적)
|| execution(* *..*Adapter.*(..))                                    ← 3. *Adapter suffix (폴백)
```

대상 프로젝트에서 할 일:
- Spring Data Repository → **추가 작업 없음** (자동 캡처)
- WebClient 래퍼, Kafka Producer 등 → `@IOTraceable(IOType.EXTERNAL_API)` 부착
- *Adapter suffix 클래스 → **추가 작업 없음** (컨벤션 폴백)

## 활성화 전략

- **Spring**: `@Profile("debug-trace")` — 프로필 미활성 시 빈 자체 미등록, 오버헤드 0
- **비Spring**: 헤더 기반 `X-Debug-Trace: true` — 미들웨어에서 헤더 체크

## 주입 프로세스

### 1. 프로젝트 분석
- 언어/프레임워크 감지
- Redis 의존성 존재 여부 확인
- adapter/repository 패키지 구조 파악

### 2. 언어별 분기

#### Kotlin/Spring (템플릿 사용)

`templates/interceptors/kotlin-spring/` 의 템플릿을 대상 프로젝트에 주입:
- 의존성 추가: Redis 클라이언트, Spring AOP
- 패키지명을 프로젝트 컨벤션에 맞게 변경
- infrastructure/config/ 패키지에 배치
- application-debug-trace.yml 추가
- Spring Data가 아닌 IO 클래스에 `@IOTraceable` 부착 안내
- 검증: `./gradlew compileKotlin` + debug-trace 프로필 없이 기존 테스트 통과 확인

#### Python / TypeScript 등 (패턴 기반 생성)

Kotlin 템플릿이 없는 언어는 아래 **참조 아키텍처**를 기반으로 대상 언어에 맞는 코드를 직접 생성한다.
Kotlin 템플릿 코드(`templates/interceptors/kotlin-spring/`)를 참조 구현으로 열어보고, 동일한 패턴을 대상 언어/프레임워크에 맞게 변환한다.

## 참조 아키텍처 (언어 무관)

모든 언어에서 동일한 5개 컴포넌트를 구현해야 한다:

### 1. TraceIdFilter — 트레이스 진입점

| 역할 | HTTP 요청에서 `X-Trace-Id` 헤더를 읽어 요청 컨텍스트에 설정 |
|------|-----|
| 헤더 없으면 | 트레이싱 스킵 (pass-through) |
| IO 데이터 캡처 | 하지 않음 (경량) |

| 언어 | 구현 방식 |
|------|----------|
| Python/FastAPI | ASGI Middleware |
| TypeScript/Express | Express Middleware |
| TypeScript/NestJS | NestJS Middleware 또는 Guard |

```python
# Python/FastAPI 예시 패턴
class TraceIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        trace_id = request.headers.get("X-Trace-Id")
        if not trace_id:
            return await call_next(request)
        token = trace_id_var.set(trace_id)  # contextvars
        try:
            return await call_next(request)
        finally:
            trace_id_var.reset(token)
            IOTraceContext.cleanup(trace_id)
```

### 2. IOSnapshotCapture — IO 캡처 (통합)

| 역할 | 모든 외부 IO 호출을 감싸서 req/res를 스냅샷 |
|------|-----|
| 캡처 시점 | 호출 완료(결과 물리화) 시 1회 |
| sequence | 호출 진입 시 채번 (순서 보존) |

AOP가 없는 언어에서는 **데코레이터/래퍼 패턴**으로 동일한 효과를 낸다:

| 언어 | 구현 방식 | 타겟 식별 |
|------|----------|----------|
| Python | `@io_traceable(IOType.DB)` 데코레이터 | 데코레이터 부착으로 명시적 opt-in |
| TypeScript | 데코레이터 또는 Proxy 패턴 | 데코레이터 부착 또는 클래스명 컨벤션 |

```python
# Python 데코레이터 예시 패턴
def io_traceable(io_type: IOType = IOType.EXTERNAL_API):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            trace_id = trace_id_var.get(None)
            if not trace_id:
                return await func(*args, **kwargs)
            seq = IOTraceContext.next_sequence(trace_id)
            invoked_at = datetime.now(UTC)
            try:
                result = await func(*args, **kwargs)
                log_store.store(IOEvent(
                    trace_id=trace_id, sequence=seq,
                    invoked_at=invoked_at, completed_at=datetime.now(UTC),
                    io_type=io_type, method=func.__qualname__,
                    request=str(args)[:2000], response=str(result)[:2000],
                ))
                return result
            except Exception as e:
                log_store.store(IOEvent(..., error=str(e)))
                raise
        return wrapper
    return decorator

# 사용
@io_traceable(IOType.DB)
async def find_order(order_id: int) -> Order: ...

@io_traceable(IOType.EXTERNAL_API)
async def charge_payment(request: ChargeRequest) -> Payment: ...
```

```typescript
// TypeScript 데코레이터 예시 패턴
function IOTraceable(ioType: IOType = IOType.EXTERNAL_API) {
  return function (target: any, key: string, descriptor: PropertyDescriptor) {
    const original = descriptor.value;
    descriptor.value = async function (...args: any[]) {
      const traceId = getTraceId(); // AsyncLocalStorage
      if (!traceId) return original.apply(this, args);
      const seq = IOTraceContext.nextSequence(traceId);
      const invokedAt = Date.now();
      try {
        const result = await original.apply(this, args);
        logStore.store({ traceId, sequence: seq, invokedAt,
          completedAt: Date.now(), type: ioType,
          method: `${target.constructor.name}.${key}`,
          request: JSON.stringify(args).slice(0, 2000),
          response: JSON.stringify(result).slice(0, 2000) });
        return result;
      } catch (e) {
        logStore.store({ ...event, error: String(e) });
        throw e;
      }
    };
  };
}

// 사용
class PaymentClient {
  @IOTraceable(IOType.EXTERNAL_API)
  async charge(request: ChargeRequest): Promise<Payment> { ... }
}
```

### 3. IOTraceLogCapture — 애플리케이션 로그 캡처

| 언어 | 구현 방식 |
|------|----------|
| Python | `logging.Handler` 서브클래스 |
| TypeScript | winston/pino custom transport |

traceId가 있는 요청 컨텍스트에서 발생한 WARN 이상 로그를 같은 traceId로 Redis에 적재.

### 4. IOTraceContext — sequence 채번

| 언어 | 구현 방식 |
|------|----------|
| Python | `dict[str, itertools.count]` + `contextvars.ContextVar` |
| TypeScript | `Map<string, number>` + `AsyncLocalStorage` |

### 5. RedisLogStore — 저장/조회

Redis 연동은 언어 무관하게 동일한 구조:
- **저장**: `HSET io:{traceId}:{type}:{method}:{seq}` + `SADD io:index:{traceId}`
- **조회**: `SMEMBERS io:index:{traceId}` → `HGETALL io:{traceId}:...`
- **TTL**: Hash 키와 인덱스 Set 모두에 동일 TTL 적용

## 활성화 방식 (비Spring)

| 방식 | 설명 |
|------|------|
| 헤더 기반 | `X-Debug-Trace: true` 헤더가 있는 요청만 캡처 |
| 환경변수 | `IO_DEBUG_ENABLED=true`로 전체 활성화 |
| 설정 파일 | `.env` 또는 config에서 on/off |

TraceIdFilter에서 활성화 체크를 추가하여, 비활성 시 pass-through.

## 순서 보장

- sequence: 호출 진입 시 AtomicLong 채번 (AOP proceed 전)
- 데이터 쓰기: proceed() 반환 시점에 1회만 (blocking/suspend 모두 동일)

## Integration

- **Called by:** ai-debugger:debug-agent (미설치 감지 시)
- **Standalone:** `/io-setup`으로 직접 호출
