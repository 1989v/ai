package com.debugtrace

// io-traceable.kt
// Spring Data Repository가 아닌 IO 클래스에 명시적으로 부착하여 AOP 캡처 대상 지정

@Target(AnnotationTarget.CLASS)
@Retention(AnnotationRetention.RUNTIME)
annotation class IOTraceable(val type: IOType = IOType.EXTERNAL_API)

// 사용 예:
// @IOTraceable(IOType.EXTERNAL_API)
// class PaymentClient(private val webClient: WebClient) { ... }
//
// @IOTraceable(IOType.KAFKA)
// class OrderEventProducer(private val kafkaTemplate: KafkaTemplate<String, String>) { ... }
