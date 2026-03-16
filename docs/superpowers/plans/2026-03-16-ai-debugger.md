# ai-debugger Plugin Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** API 요청을 디버깅하고 이슈를 해결하는 Claude Code 플러그인 구현. Full IO 캡처 + 코드/데이터 분석 기반.

**Architecture:** Claude Code 플러그인 (`skills/` + `agents/` + `templates/`). 스킬은 마크다운 프롬프트, IO 인터셉터 템플릿은 언어별 실제 코드.

**Tech Stack:** Claude Code Plugin System, Kotlin/Spring (주력), Redis (IO 로그 저장)

**Spec:** `docs/superpowers/specs/2026-03-16-ai-common-plugins-design.md` Section 4

**Scope:** v1은 Kotlin/Spring 인터셉터 템플릿만 구현. Python/FastAPI, TypeScript/Express 템플릿은 향후 별도 플랜으로 추가.

**Note:** plugin.json은 doc-scaffolding 플랜의 Task 1에서 레포 스캐폴딩 시 이미 생성됨.

---

## Chunk 1: IO 인터셉터 템플릿 (Kotlin/Spring)

### Task 1: IO 로그 스키마 및 공통 인프라 (Kotlin)

**Files:**
- Create: `plugins/ai-debugger/templates/interceptors/kotlin-spring/io-log-schema.kt`
- Create: `plugins/ai-debugger/templates/interceptors/kotlin-spring/io-log-store.kt`
- Create: `plugins/ai-debugger/templates/interceptors/kotlin-spring/io-trace-context.kt`

- [ ] **Step 1: IO 로그 데이터 클래스 작성**

```kotlin
// io-log-schema.kt
// IO 이벤트를 표현하는 데이터 클래스. 인터셉터들이 이 형식으로 로그를 생성한다.
//
// Note: method, codeLine은 스펙의 JSON 스키마에는 없지만 Redis Hash 키에 포함되는 값.
//       데이터 클래스에 포함하여 키 생성 시 활용한다.
// Note: invokedAt/completedAt은 스펙의 timestamp 필드를 세분화한 의도적 확장.

data class IOEvent(
    val schemaVersion: Int = 1,
    val traceId: String,
    val sequence: Long,
    val invokedAt: Instant,
    var completedAt: Instant? = null,
    val service: String,
    val type: IOType,
    val direction: IODirection,
    val method: String,        // Redis 키용: 클래스명.메서드명 (정적 매핑)
    val codeLine: Int = 0,     // Redis 키용: 프레임워크 인터셉터는 0, AOP는 대상 메서드 라인
    var request: String = "",  // JSON serialized
    var response: String = "", // JSON serialized
    var duration: Long = 0,
    var error: String? = null
)

enum class IOType { HTTP, DB, EXTERNAL_API, KAFKA, REDIS }
enum class IODirection { INBOUND, OUTBOUND }
```

- [ ] **Step 2: TraceContext 작성**

```kotlin
// io-trace-context.kt
// traceId별 sequence 채번 및 코루틴 컨텍스트 전파

object IOTraceContext {
    private val sequenceMap = ConcurrentHashMap<String, AtomicLong>()

    fun nextSequence(traceId: String): Long =
        sequenceMap.computeIfAbsent(traceId) { AtomicLong(0) }
            .incrementAndGet()

    fun cleanup(traceId: String) {
        sequenceMap.remove(traceId)
    }
}

// 코루틴 컨텍스트 요소 — MDC 유실 방지
class TraceContextElement(
    val traceId: String
) : AbstractCoroutineContextElement(Key) {
    companion object Key : CoroutineContext.Key<TraceContextElement>
}
```

- [ ] **Step 3: Redis LogStore 구현 작성**

```kotlin
// io-log-store.kt
// Redis Hash + Set 인덱스 기반 LogStore

@Profile("debug-trace")
@Component
class RedisIOLogStore(
    private val redisTemplate: StringRedisTemplate,
    @Value("\${io-debug.ttl-hours:24}") private val ttlHours: Long
) {
    fun store(event: IOEvent) {
        val key = "io:${event.traceId}:${event.type}:${event.method}:${event.codeLine}"
        val indexKey = "io:index:${event.traceId}"
        val ttl = Duration.ofHours(ttlHours)

        // Hash에 이벤트 저장
        redisTemplate.opsForHash<String, String>().putAll(key, mapOf(
            "schemaVersion" to event.schemaVersion.toString(),
            "sequence" to event.sequence.toString(),
            "invokedAt" to event.invokedAt.toString(),
            "completedAt" to (event.completedAt?.toString() ?: ""),
            "service" to event.service,
            "direction" to event.direction.name,
            "request" to event.request,
            "response" to event.response,
            "duration" to event.duration.toString(),
            "error" to (event.error ?: "")
        ))
        redisTemplate.expire(key, ttl)

        // 인덱스 Set에 키 추가
        redisTemplate.opsForSet().add(indexKey, key)
        redisTemplate.expire(indexKey, ttl)
    }

    fun listKeys(traceId: String): Set<String> =
        redisTemplate.opsForSet().members("io:index:$traceId") ?: emptySet()

    fun getDetail(key: String): Map<String, String> =
        redisTemplate.opsForHash<String, String>().entries(key)
}
```

- [ ] **Step 4: 커밋**

```bash
git add plugins/ai-debugger/templates/interceptors/kotlin-spring/
git commit -m "feat: add IO log schema, trace context, and Redis log store (Kotlin)"
```

---

### Task 2: HTTP 인터셉터 (Kotlin/Spring)

**Files:**
- Create: `plugins/ai-debugger/templates/interceptors/kotlin-spring/http-filter.kt`

- [ ] **Step 1: Servlet Filter 작성**

```kotlin
// http-filter.kt
// HTTP 요청/응답 캡처 Servlet Filter
// @Profile("debug-trace")로 프로필 미활성 시 빈 등록 안됨

@Profile("debug-trace")
@Component
@Order(Ordered.HIGHEST_PRECEDENCE)
class IOHttpFilter(
    private val logStore: RedisIOLogStore,
    @Value("\${spring.application.name}") private val serviceName: String
) : OncePerRequestFilter() {

    override fun doFilterInternal(
        request: HttpServletRequest,
        response: HttpServletResponse,
        filterChain: FilterChain
    ) {
        val traceId = request.getHeader("X-Trace-Id")
            ?: UUID.randomUUID().toString()
        val sequence = IOTraceContext.nextSequence(traceId)
        val invokedAt = Instant.now()

        // MDC에 traceId 설정 — 하위 인터셉터(DB AOP 등)에서 참조
        MDC.put("traceId", traceId)

        // 요청 래핑 (body 읽기 위해)
        val wrappedRequest = ContentCachingRequestWrapper(request)
        val wrappedResponse = ContentCachingResponseWrapper(response)

        try {
            filterChain.doFilter(wrappedRequest, wrappedResponse)
        } finally {
            val event = IOEvent(
                traceId = traceId,
                sequence = sequence,
                invokedAt = invokedAt,
                completedAt = Instant.now(),
                service = serviceName,
                type = IOType.HTTP,
                direction = IODirection.INBOUND,
                method = "${request.method} ${request.requestURI}",
                codeLine = 0, // HTTP 필터는 코드 라인 해당 없음
                request = String(wrappedRequest.contentAsByteArray),
                response = String(wrappedResponse.contentAsByteArray),
                duration = Duration.between(invokedAt, Instant.now()).toMillis(),
                error = if (wrappedResponse.status >= 400)
                    "HTTP ${wrappedResponse.status}" else null
            )
            logStore.store(event)
            wrappedResponse.copyBodyToResponse()
            MDC.remove("traceId")
            IOTraceContext.cleanup(traceId)
        }
    }
}
```

- [ ] **Step 2: 커밋**

```bash
git add plugins/ai-debugger/templates/interceptors/kotlin-spring/http-filter.kt
git commit -m "feat: add HTTP servlet filter for IO capture (Kotlin/Spring)"
```

---

### Task 3: DB 인터셉터 (Kotlin/Spring AOP)

**Files:**
- Create: `plugins/ai-debugger/templates/interceptors/kotlin-spring/db-interceptor.kt`

- [ ] **Step 1: JPA Repository AOP 인터셉터 작성**

```kotlin
// db-interceptor.kt
// JPA Repository 메서드 호출을 AOP로 캡처
// suspend 함수가 아닌 blocking JPA이므로 AOP proceed()로 안전하게 캡처 가능

@Profile("debug-trace")
@Aspect
@Component
class IODbInterceptor(
    private val logStore: RedisIOLogStore,
    @Value("\${spring.application.name}") private val serviceName: String
) {

    @Around("execution(* org.springframework.data.repository.Repository+.*(..))")
    fun interceptRepository(joinPoint: ProceedingJoinPoint): Any? {
        val traceId = MDC.get("traceId") ?: return joinPoint.proceed()
        val sequence = IOTraceContext.nextSequence(traceId)
        val invokedAt = Instant.now()
        val method = "${joinPoint.target.javaClass.simpleName}.${joinPoint.signature.name}"

        return try {
            val result = joinPoint.proceed()
            logStore.store(IOEvent(
                traceId = traceId,
                sequence = sequence,
                invokedAt = invokedAt,
                completedAt = Instant.now(),
                service = serviceName,
                type = IOType.DB,
                direction = IODirection.OUTBOUND,
                method = method,
                codeLine = 0,
                request = joinPoint.args.contentToString(),
                response = result?.toString()?.take(1000) ?: "null",
                duration = Duration.between(invokedAt, Instant.now()).toMillis()
            ))
            result
        } catch (e: Exception) {
            logStore.store(IOEvent(
                traceId = traceId,
                sequence = sequence,
                invokedAt = invokedAt,
                completedAt = Instant.now(),
                service = serviceName,
                type = IOType.DB,
                direction = IODirection.OUTBOUND,
                method = method,
                codeLine = 0,
                request = joinPoint.args.contentToString(),
                duration = Duration.between(invokedAt, Instant.now()).toMillis(),
                error = "${e.javaClass.simpleName}: ${e.message}"
            ))
            throw e
        }
    }
}
```

- [ ] **Step 2: 커밋**

```bash
git add plugins/ai-debugger/templates/interceptors/kotlin-spring/db-interceptor.kt
git commit -m "feat: add DB AOP interceptor for JPA repository capture (Kotlin)"
```

---

### Task 4: WebClient 인터셉터 (논블러킹 외부 API)

**Files:**
- Create: `plugins/ai-debugger/templates/interceptors/kotlin-spring/webclient-filter.kt`

- [ ] **Step 1: ExchangeFilterFunction 작성**

```kotlin
// webclient-filter.kt
// WebClient 외부 API 호출 캡처
// 리액티브 체인 내에서 동작, 응답 수신 완료 시점에 스냅샷
// MDC의 traceId를 outbound 요청 헤더에 자동 전파

@Profile("debug-trace")
@Component
class IOWebClientFilter(
    private val logStore: RedisIOLogStore,
    @Value("\${spring.application.name}") private val serviceName: String
) {

    fun filter(): ExchangeFilterFunction = ExchangeFilterFunction { request, next ->
        // MDC에서 traceId 가져와서 outbound 헤더에 주입
        val traceId = MDC.get("traceId") ?: return@ExchangeFilterFunction next.exchange(request)
        val sequence = IOTraceContext.nextSequence(traceId)
        val invokedAt = Instant.now()
        val method = "${request.method()} ${request.url().path}"

        val mutatedRequest = ClientRequest.from(request)
            .header("X-Trace-Id", traceId)
            .build()

        next.exchange(mutatedRequest)
            .flatMap { response ->
                // 응답 바디를 버퍼링하여 캡처
                response.bodyToMono(String::class.java)
                    .defaultIfEmpty("")
                    .map { body ->
                        logStore.store(IOEvent(
                            traceId = traceId,
                            sequence = sequence,
                            invokedAt = invokedAt,
                            completedAt = Instant.now(),
                            service = serviceName,
                            type = IOType.EXTERNAL_API,
                            direction = IODirection.OUTBOUND,
                            method = method,
                            request = mutatedRequest.url().toString(),
                            response = body.take(2000), // 응답 바디 (최대 2KB)
                            duration = Duration.between(invokedAt, Instant.now()).toMillis(),
                            error = if (response.statusCode().isError)
                                "HTTP ${response.statusCode().value()}" else null
                        ))
                        // 바디를 다시 ClientResponse로 래핑하여 반환
                        response.mutate().body(body).build()
                    }
            }
    }
}
```

- [ ] **Step 2: 커밋**

```bash
git add plugins/ai-debugger/templates/interceptors/kotlin-spring/webclient-filter.kt
git commit -m "feat: add WebClient ExchangeFilterFunction for external API capture"
```

---

### Task 5: Kafka + Redis 인터셉터 (Kotlin/Spring)

**Files:**
- Create: `plugins/ai-debugger/templates/interceptors/kotlin-spring/kafka-interceptor.kt`
- Create: `plugins/ai-debugger/templates/interceptors/kotlin-spring/redis-listener.kt`

- [ ] **Step 1: Kafka ProducerInterceptor 작성**

Kafka 메시지 발행 캡처. `onAcknowledgement`에서 스냅샷.

- [ ] **Step 2: Kafka ConsumerInterceptor 작성**

Kafka 메시지 수신 캡처. `onConsume`에서 스냅샷.

- [ ] **Step 3: Lettuce CommandListener 작성**

Redis 커맨드 캡처. `commandCompleted`에서 스냅샷.

- [ ] **Step 4: 커밋**

```bash
git add plugins/ai-debugger/templates/interceptors/kotlin-spring/
git commit -m "feat: add Kafka and Redis interceptors for IO capture (Kotlin)"
```

---

### Task 6: Spring 설정 템플릿

**Files:**
- Create: `plugins/ai-debugger/templates/interceptors/kotlin-spring/debug-trace-config.kt`
- Create: `plugins/ai-debugger/templates/interceptors/kotlin-spring/application-debug-trace.yml`

- [ ] **Step 1: @Profile 기반 설정 클래스 작성**

```kotlin
// debug-trace-config.kt
// debug-trace 프로필에서만 활성화되는 설정

@Profile("debug-trace")
@Configuration
@EnableAspectJAutoProxy
class DebugTraceConfig {

    @Bean
    fun debugTraceWebClient(
        builder: WebClient.Builder,
        filter: IOWebClientFilter
    ): WebClient = builder
        .filter(filter.filter())
        .build()
}
```

- [ ] **Step 2: application-debug-trace.yml 작성**

```yaml
# application-debug-trace.yml
# SPRING_PROFILES_ACTIVE=debug-trace 로 활성화

io-debug:
  ttl-hours: 24
  enabled: true

spring:
  data:
    redis:
      host: ${IO_DEBUG_REDIS_HOST:localhost}
      port: ${IO_DEBUG_REDIS_PORT:6379}
```

- [ ] **Step 3: 커밋**

```bash
git add plugins/ai-debugger/templates/interceptors/kotlin-spring/
git commit -m "feat: add debug-trace Spring profile config and application yml"
```

---

## Chunk 2: ai-debugger 스킬 구현

### Task 7: io-interceptor 스킬

**Files:**
- Create: `plugins/ai-debugger/skills/io-interceptor/SKILL.md`

- [ ] **Step 1: io-interceptor SKILL.md 작성**

```markdown
---
name: io-interceptor
description: Use when setting up IO capture in a target service - injects interceptors for HTTP, DB, external API, Kafka, Redis with profile-based activation
---

# IO Interceptor Setup

## Overview

대상 서비스에 IO 인터셉터를 주입한다. 서비스의 코드 컨벤션을 준수하며,
프로필/헤더 기반으로 활성화하여 평상시 성능 영향 없음.

## 활성화 전략

- **Spring**: `@Profile("debug-trace")` — `SPRING_PROFILES_ACTIVE=debug-trace`로 활성화
- **비Spring**: 헤더 기반 `X-Debug-Trace: true`

## 주입 프로세스

### 1. 프로젝트 분석
- 언어/프레임워크 감지
- 기존 인터셉터/필터 구조 확인 (충돌 방지)
- Redis 의존성 존재 여부 확인

### 2. 의존성 추가
- Redis 클라이언트 (없으면 추가)
- Spring AOP (없으면 추가)

### 3. 코드 주입
`templates/interceptors/{lang}/` 의 템플릿을 대상 프로젝트 컨벤션에 맞게 조정 후 주입:
- 패키지명을 프로젝트 컨벤션에 맞게 변경
- infrastructure/config/ 또는 프로젝트의 설정 패키지에 배치
- application-debug-trace.yml 추가

### 4. 검증
- 컴파일 확인 (`./gradlew compileKotlin`)
- debug-trace 프로필 없이 기존 테스트 통과 확인

## 캡처 대상

| 구간 | Kotlin/Spring | 스냅샷 시점 |
|------|---------------|------------|
| HTTP req/res | Servlet Filter | 필터 체인 완료 |
| DB (JPA) | AOP @Around | proceed() 반환 |
| 외부 API | ExchangeFilterFunction | 응답 수신 완료 |
| Kafka | Producer/ConsumerInterceptor | ACK/consume 시점 |
| Redis | Lettuce CommandListener | commandCompleted |

## 순서 보장

- sequence: 호출 진입 시 AtomicLong 채번
- 데이터 쓰기: 결과 물리화 시점에 1회만

## Integration

- **Called by:** ai-debugger:debug-agent (미설치 감지 시)
- **Standalone:** `/io-setup`으로 직접 호출
```

- [ ] **Step 2: 커밋**

```bash
git add plugins/ai-debugger/skills/io-interceptor/
git commit -m "feat: add io-interceptor skill - IO capture setup guide"
```

---

### Task 8: curl-gen 스킬

**Files:**
- Create: `plugins/ai-debugger/skills/curl-gen/SKILL.md`

- [ ] **Step 1: curl-gen SKILL.md 작성**

```markdown
---
name: curl-gen
description: Use when generating curl commands from natural language or API specs - parses user intent, finds matching API endpoints, collects parameters, and builds executable curl
---

# curl Command Generator

## Overview

사용자의 자연어 설명을 파싱하여 대상 API의 curl 명령을 생성한다.

## 프로세스

### 1. API 식별
사용자 설명에서 대상 API를 식별:
- 코드베이스의 Controller/Router 탐색
- OpenAPI spec 파일 존재 시 참조
- docs/에 API 문서가 있으면 참조

### 2. 파라미터 수집
- Path variable, Query parameter, Request body 식별
- 필수/선택 구분
- 사용자에게 누락된 필수 파라미터 질문

### 3. 인증 처리
- 환경변수에서 토큰 조회 (예: `$API_TOKEN`, `$AUTH_HEADER`)
- 없으면 사용자에게 입력 요청
- 로그에는 마스킹 처리 (`Authorization: Bearer ***`)

### 4. curl 생성 + 실행
```bash
curl -X POST http://localhost:8080/api/orders \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "X-Trace-Id: debug-$(date +%s)" \
  -d '{"productId": 1, "quantity": 2}'
```

- X-Trace-Id 헤더 자동 추가 (IO 인터셉터 연동)
- 사용자 확인 후 실행
- 응답 출력

## Integration

- **Called by:** ai-debugger:debug-agent
- **Standalone:** `/curl-gen`으로 직접 호출
```

- [ ] **Step 2: 커밋**

```bash
git add plugins/ai-debugger/skills/curl-gen/
git commit -m "feat: add curl-gen skill - natural language to curl command"
```

---

### Task 9: log-query 스킬

**Files:**
- Create: `plugins/ai-debugger/skills/log-query/SKILL.md`

- [ ] **Step 1: log-query SKILL.md 작성**

```markdown
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
```

- [ ] **Step 2: 커밋**

```bash
git add plugins/ai-debugger/skills/log-query/
git commit -m "feat: add log-query skill - 2-phase IO log retrieval"
```

---

### Task 10: code-explore 스킬

**Files:**
- Create: `plugins/ai-debugger/skills/code-explore/SKILL.md`

- [ ] **Step 1: code-explore SKILL.md 작성**

```markdown
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

📍 Entry: OrderController.createOrder (order/app/.../controller/OrderController.kt:45)
📍 Flow: CreateOrderUseCase → OrderService.create → OrderRepository.save
📍 Suspect: OrderService.kt:89 - 재고 차감 로직에서 동시성 미처리

📄 docs/policies/inventory-rules.md:
   "재고 차감은 비관적 락으로 처리해야 함" — 코드에 락 미적용

🔍 Verdict: 코드 이슈 (동시성 처리 누락)
```

## Integration

- **Called by:** ai-debugger:debug-agent
- **Not standalone** — debug-agent 플로우 내에서만 호출
```

- [ ] **Step 2: 커밋**

```bash
git add plugins/ai-debugger/skills/code-explore/
git commit -m "feat: add code-explore skill - codebase + docs analysis"
```

---

### Task 11: data-analyze 스킬

**Files:**
- Create: `plugins/ai-debugger/skills/data-analyze/SKILL.md`

- [ ] **Step 1: data-analyze SKILL.md 작성**

```markdown
---
name: data-analyze
description: Use when code analysis alone cannot explain an issue - analyzes IO log data patterns to find anomalies in request flows, response times, error patterns
---

# IO Data Analyzer

## Overview

수집된 IO 데이터에서 패턴을 분석하여 코드만으로 설명되지 않는 이슈의 원인을 찾는다.

## 분석 패턴

### 1. 에러 패턴
- 특정 IO 구간에서 반복적 에러 발생
- 에러 메시지 내용 분석

### 2. 지연 패턴
- invokedAt ~ completedAt 간격으로 병목 구간 식별
- sequence 순서와 시간 간격으로 비동기 대기 구간 파악

### 3. 데이터 불일치
- 요청 파라미터와 응답 데이터 간 불일치
- DB 쿼리 결과와 API 응답 간 변환 오류

### 4. 호출 패턴 이상
- 예상보다 많은 DB 호출 (N+1 문제)
- 불필요한 외부 API 중복 호출
- 누락된 캐시 히트 (Redis GET이 항상 miss)

## Integration

- **Called by:** ai-debugger:debug-agent (code-explore 후 추가 분석 필요 시)
- **Requires:** log-query로 데이터 먼저 조회
```

- [ ] **Step 2: 커밋**

```bash
git add plugins/ai-debugger/skills/data-analyze/
git commit -m "feat: add data-analyze skill - IO data pattern analysis"
```

---

### Task 12: answer-gen 스킬

**Files:**
- Create: `plugins/ai-debugger/skills/answer-gen/SKILL.md`

- [ ] **Step 1: answer-gen SKILL.md 작성**

```markdown
---
name: answer-gen
description: Use when generating a comprehensive debug answer for the user - synthesizes code analysis, IO log evidence, and docs references into actionable response
---

# Debug Answer Generator

## Overview

분석 결과를 종합하여 사용자에게 구조화된 답변을 생성한다.

## 답변 구조

```
## 원인 분석

{이슈의 근본 원인 설명}

## 관련 코드

- `{파일경로}:{라인}` — {해당 코드의 역할과 문제점}

## IO 로그 근거 (조회한 경우)

- `{IO키}` — {데이터가 보여주는 증거}

## 문서 참조

- `docs/policies/{파일}` — {관련 비즈니스 규칙}

## 해결 방안

1. {구체적 수정 방안}
2. {대안이 있으면 제시}

## 재발 방지

- {근본적 해결을 위한 제안}
```

## 원칙

- 추측이 아닌 코드/데이터 근거 기반
- 코드 위치를 정확히 명시 (파일:라인)
- 해결 방안은 구체적이고 실행 가능하게
- 불확실한 부분은 명시적으로 "확인 필요" 표시

## Integration

- **Called by:** ai-debugger:debug-agent (최종 단계)
```

- [ ] **Step 2: 커밋**

```bash
git add plugins/ai-debugger/skills/answer-gen/
git commit -m "feat: add answer-gen skill - structured debug response"
```

---

## Chunk 3: 오케스트레이터 에이전트 + 검증

### Task 13: debug-agent 오케스트레이터

**Files:**
- Create: `plugins/ai-debugger/agents/debug-agent.md`

- [ ] **Step 1: debug-agent.md 작성**

```markdown
---
name: debug-agent
description: |
  Use this agent when debugging API issues - orchestrates curl generation,
  code exploration with docs reference, selective IO log query, data analysis,
  and answer generation. Prioritizes code analysis over log fetching.
model: inherit
---

# Debug Agent

당신은 API 디버깅 에이전트입니다.
사용자의 이슈를 코드와 데이터 기반으로 분석하여 해결합니다.

## 핵심 원칙

1. **코드 분석이 우선**. IO 로그는 보조 근거로 필요할 때만 조회
2. **docs/도 코드와 함께 참조**. 비즈니스 규칙, 설계 의도를 함께 확인
3. **컨텍스트 비용 최소화**. IO 로그 키 스캔으로 필요 여부 먼저 판단

## 실행 순서

### 1. 질의 파싱

사용자 질의에서 파악:
- 대상 API (엔드포인트, 메서드)
- 증상 (에러 메시지, 예상과 다른 동작, 성능 문제)
- 컨텍스트 (특정 데이터, 환경, 재현 조건)

### 2. IO 인터셉터 확인

대상 프로젝트에 인터셉터가 주입되어 있는지 확인:
- `@Profile("debug-trace")` 어노테이션이 있는 클래스 탐색
- 없으면 사용자에게 ai-debugger:io-interceptor 스킬로 설치 제안
- 설치만 제안하고, 사용자 동의 시에만 진행

### 3. curl 생성 + 실행

ai-debugger:curl-gen 스킬의 지침을 따라:
- 대상 API의 curl 명령 생성
- X-Trace-Id 헤더 자동 추가
- 사용자 확인 후 실행

### 4. 코드 분석

ai-debugger:code-explore 스킬의 지침을 따라:
- API 엔드포인트 → 비즈니스 로직 → 데이터 접근 순으로 추적
- docs/policies, docs/architecture 함께 참조
- **원인 발견 시** → 6단계로 이동
- **코드만으로 불충분** → 5단계로 이동

### 5. IO 로그 조회 + 분석

ai-debugger:log-query 스킬로 2단계 조회:
1. 키 스캔: `SMEMBERS io:index:{traceId}` → 관련 키 필터링
2. 값 조회: 의심 키만 `HGETALL`

ai-debugger:data-analyze 스킬로 패턴 분석:
- 에러, 지연, 데이터 불일치, 호출 패턴 이상 확인

### 6. 답변 생성

ai-debugger:answer-gen 스킬의 지침을 따라 구조화된 답변 생성.
```

- [ ] **Step 2: 커밋**

```bash
git add plugins/ai-debugger/agents/
git commit -m "feat: add debug-agent orchestrator"
```

---

### Task 14: MSA 프로젝트 대상 검증

**Files:**
- 없음 (수동 검증)

- [ ] **Step 1: ai-debugger 플러그인을 MSA 프로젝트에 등록**

`/Users/gideok-kwon/IdeaProjects/msa/.claude/settings.json`에 추가:

```json
{
  "plugins": [
    "/Users/gideok-kwon/IdeaProjects/ai/plugins/doc-scaffolding",
    "/Users/gideok-kwon/IdeaProjects/ai/plugins/ai-debugger"
  ]
}
```

- [ ] **Step 2: `/io-setup` 호출하여 인터셉터 주입 검증**

검증 항목:
- Spring Boot + Kotlin 프로젝트를 올바르게 감지하는지
- 인터셉터 코드가 프로젝트 패키지 컨벤션에 맞게 주입되는지
- `@Profile("debug-trace")` 없이 기존 테스트 통과하는지
- debug-trace 프로필로 실행 시 IO 캡처가 정상 동작하는지

- [ ] **Step 3: 디버그 시나리오 테스트**

1. debug-trace 프로필로 서비스 기동
2. `/curl-gen`으로 테스트 API 호출
3. Redis에 IO 로그 적재 확인
4. debug-agent로 모의 이슈 디버깅

- [ ] **Step 4: 발견된 문제 수정 후 커밋**

```bash
git add plugins/ai-debugger/
git commit -m "fix: address issues found during MSA project validation"
```
