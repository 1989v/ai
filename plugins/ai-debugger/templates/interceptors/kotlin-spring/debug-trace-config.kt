package com.debugtrace

import org.springframework.context.annotation.Configuration
import org.springframework.context.annotation.EnableAspectJAutoProxy
import org.springframework.context.annotation.Profile

// debug-trace-config.kt
// debug-trace 프로필에서만 활성화되는 설정

@Profile("debug-trace")
@Configuration
@EnableAspectJAutoProxy
class DebugTraceConfig
