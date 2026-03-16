package com.debugtrace

import ch.qos.logback.classic.Level
import ch.qos.logback.classic.Logger
import ch.qos.logback.classic.LoggerContext
import ch.qos.logback.classic.spi.ILoggingEvent
import ch.qos.logback.classic.spi.ThrowableProxyUtil
import ch.qos.logback.core.AppenderBase
import org.slf4j.LoggerFactory
import org.springframework.beans.factory.annotation.Value
import org.springframework.context.annotation.Profile
import org.springframework.context.SmartLifecycle
import org.springframework.stereotype.Component
import java.time.Instant

// io-trace-log-appender.kt
// 요청 처리 중 발생한 애플리케이션 로그를 같은 traceId로 적재.
// 기본 레벨: WARN (application-debug-trace.yml에서 변경 가능)

@Profile("debug-trace")
@Component
class IOTraceLogAppender(
    private val logStore: RedisIOLogStore,
    @Value("\${spring.application.name}") private val serviceName: String,
    @Value("\${io-debug.log-level:WARN}") private val minLevel: String
) : AppenderBase<ILoggingEvent>(), SmartLifecycle {

    override fun append(event: ILoggingEvent) {
        val traceId = event.mdcPropertyMap["traceId"] ?: return
        if (event.level.toInt() < Level.toLevel(minLevel).toInt()) return

        logStore.store(IOEvent(
            traceId = traceId,
            sequence = IOTraceContext.nextSequence(traceId),
            invokedAt = Instant.ofEpochMilli(event.timeStamp),
            completedAt = Instant.ofEpochMilli(event.timeStamp),
            service = serviceName,
            type = IOType.LOG,
            direction = IODirection.INBOUND,
            method = event.loggerName.substringAfterLast('.'),
            request = "${event.level}: ${event.formattedMessage}",
            response = event.throwableProxy?.let {
                ThrowableProxyUtil.asString(it).take(2000)
            } ?: "",
            duration = 0
        ))
    }

    // SmartLifecycle: 앱 시작 시 Logback에 자동 등록
    override fun start() {
        val loggerContext = LoggerFactory.getILoggerFactory() as LoggerContext
        this.context = loggerContext
        super.start()
        loggerContext.getLogger(Logger.ROOT_LOGGER_NAME).addAppender(this)
    }
}
