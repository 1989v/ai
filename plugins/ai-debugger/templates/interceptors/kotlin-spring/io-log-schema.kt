package com.debugtrace

import java.time.Instant

// io-log-schema.kt
//
// Note: method는 Redis Hash 키에 포함되는 값. 데이터 클래스에 포함하여 키 생성 시 활용.
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
    val method: String,        // Redis 키용: 클래스명.메서드명
    var request: String = "",  // JSON serialized
    var response: String = "", // JSON serialized
    var duration: Long = 0,
    var error: String? = null
)

enum class IOType { DB, EXTERNAL_API, KAFKA, REDIS, LOG }
enum class IODirection { INBOUND, OUTBOUND }
