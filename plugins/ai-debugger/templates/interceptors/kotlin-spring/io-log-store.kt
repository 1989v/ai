package com.debugtrace

import org.springframework.beans.factory.annotation.Value
import org.springframework.context.annotation.Profile
import org.springframework.data.redis.core.StringRedisTemplate
import org.springframework.stereotype.Component
import java.time.Duration

// io-log-store.kt
// Redis Hash + Set 인덱스 기반 LogStore

@Profile("debug-trace")
@Component
class RedisIOLogStore(
    private val redisTemplate: StringRedisTemplate,
    @Value("\${io-debug.ttl-hours:24}") private val ttlHours: Long
) {
    fun store(event: IOEvent) {
        val key = "io:${event.traceId}:${event.type}:${event.method}:${event.sequence}"
        val indexKey = "io:index:${event.traceId}"
        val ttl = Duration.ofHours(ttlHours)

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

        redisTemplate.opsForSet().add(indexKey, key)
        redisTemplate.expire(indexKey, ttl)
    }

    fun listKeys(traceId: String): Set<String> =
        redisTemplate.opsForSet().members("io:index:$traceId") ?: emptySet()

    fun getDetail(key: String): Map<String, String> =
        redisTemplate.opsForHash<String, String>().entries(key)
}
