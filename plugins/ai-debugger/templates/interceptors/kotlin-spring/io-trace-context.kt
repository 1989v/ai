package com.debugtrace

import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicLong

// io-trace-context.kt
// traceId별 sequence 채번

object IOTraceContext {
    private val sequenceMap = ConcurrentHashMap<String, AtomicLong>()

    fun nextSequence(traceId: String): Long =
        sequenceMap.computeIfAbsent(traceId) { AtomicLong(0) }
            .incrementAndGet()

    fun cleanup(traceId: String) {
        sequenceMap.remove(traceId)
    }
}
