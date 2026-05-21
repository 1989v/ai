package com.kgd.example.order

import java.time.Instant

/**
 * Domain event — emitted when an Order transitions from CREATED to PLACED.
 * Subscribed by inventory, payment, and notification bounded contexts.
 */
data class OrderPlaced(
    val orderId: OrderId,
    val customerId: String,
    val itemCount: Int,
    val occurredAt: Instant
)
