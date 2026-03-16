package com.debugtrace

import org.aspectj.lang.ProceedingJoinPoint
import org.aspectj.lang.annotation.Around
import org.aspectj.lang.annotation.Aspect
import org.slf4j.MDC
import org.springframework.beans.factory.annotation.Value
import org.springframework.context.annotation.Profile
import org.springframework.data.repository.Repository
import org.springframework.stereotype.Component
import java.time.Duration
import java.time.Instant

// io-snapshot-aspect.kt
// 모든 IO를 하나의 Aspect로 캡처.
//
// 타겟 식별 3단계:
// 1. Spring Data Repository+ (JPA, ES, Redis 등) → 자동
// 2. @IOTraceable 어노테이션 → 명시적 opt-in
// 3. *Adapter suffix → 컨벤션 기반 폴백

@Profile("debug-trace")
@Aspect
@Component
class IOSnapshotAspect(
    private val logStore: RedisIOLogStore,
    @Value("\${spring.application.name}") private val serviceName: String
) {

    @Around("""
        execution(* org.springframework.data.repository.Repository+.*(..))
        || @within(com.debugtrace.IOTraceable)
        || execution(* *..*Adapter.*(..))
    """)
    fun captureIO(joinPoint: ProceedingJoinPoint): Any? {
        val traceId = MDC.get("traceId") ?: return joinPoint.proceed()
        val sequence = IOTraceContext.nextSequence(traceId)
        val invokedAt = Instant.now()
        val method = "${joinPoint.target.javaClass.simpleName}.${joinPoint.signature.name}"
        val ioType = detectIOType(joinPoint)

        return try {
            val result = joinPoint.proceed()
            logStore.store(IOEvent(
                traceId = traceId,
                sequence = sequence,
                invokedAt = invokedAt,
                completedAt = Instant.now(),
                service = serviceName,
                type = ioType,
                direction = IODirection.OUTBOUND,
                method = method,
                request = joinPoint.args.contentToString().take(2000),
                response = result?.toString()?.take(2000) ?: "null",
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
                type = ioType,
                direction = IODirection.OUTBOUND,
                method = method,
                request = joinPoint.args.contentToString().take(2000),
                duration = Duration.between(invokedAt, Instant.now()).toMillis(),
                error = "${e.javaClass.simpleName}: ${e.message}"
            ))
            throw e
        }
    }

    private fun detectIOType(joinPoint: ProceedingJoinPoint): IOType {
        // 1. @IOTraceable 어노테이션 우선
        val annotation = joinPoint.target.javaClass.getAnnotation(IOTraceable::class.java)
        if (annotation != null) return annotation.type

        // 2. Spring Data Repository
        if (Repository::class.java.isAssignableFrom(joinPoint.target.javaClass))
            return IOType.DB

        // 3. 클래스명 기반 폴백
        val className = joinPoint.target.javaClass.simpleName
        return when {
            className.contains("Client")   -> IOType.EXTERNAL_API
            className.contains("Producer") -> IOType.KAFKA
            className.contains("Consumer") -> IOType.KAFKA
            className.contains("Cache")    -> IOType.REDIS
            else -> IOType.EXTERNAL_API
        }
    }
}
