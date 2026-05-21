package com.kgd.example.order

import java.util.UUID

/**
 * Value object identifying an Order. Immutable, equality by value.
 */
@JvmInline
value class OrderId(val value: UUID) {
    companion object {
        fun new(): OrderId = OrderId(UUID.randomUUID())
        fun of(s: String): OrderId = OrderId(UUID.fromString(s))
    }
}
