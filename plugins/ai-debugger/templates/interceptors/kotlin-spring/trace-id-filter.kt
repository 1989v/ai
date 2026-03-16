package com.debugtrace

import jakarta.servlet.FilterChain
import jakarta.servlet.http.HttpServletRequest
import jakarta.servlet.http.HttpServletResponse
import org.slf4j.MDC
import org.springframework.context.annotation.Profile
import org.springframework.core.Ordered
import org.springframework.core.annotation.Order
import org.springframework.stereotype.Component
import org.springframework.web.filter.OncePerRequestFilter

// trace-id-filter.kt
// X-Trace-Id 헤더 → MDC 설정만 담당. IO 데이터 캡처 없음 (경량).
// curl-gen이 생성한 X-Trace-Id가 없으면 아무것도 하지 않음.

@Profile("debug-trace")
@Component
@Order(Ordered.HIGHEST_PRECEDENCE)
class TraceIdFilter : OncePerRequestFilter() {

    override fun doFilterInternal(
        request: HttpServletRequest,
        response: HttpServletResponse,
        filterChain: FilterChain
    ) {
        val traceId = request.getHeader("X-Trace-Id")
            ?: return filterChain.doFilter(request, response)

        MDC.put("traceId", traceId)
        try {
            filterChain.doFilter(request, response)
        } finally {
            MDC.remove("traceId")
            IOTraceContext.cleanup(traceId)
        }
    }
}
