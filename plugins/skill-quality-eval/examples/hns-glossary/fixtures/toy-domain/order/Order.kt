package com.kgd.example.order

import java.time.Instant

/**
 * Aggregate root for an order. Owns OrderItem entities and emits OrderPlaced events
 * when transitioning from CREATED to PLACED.
 */
class Order(
    val id: OrderId,
    val customerId: String,
    private val items: MutableList<OrderItem>,
    private var status: OrderStatus = OrderStatus.CREATED,
    val createdAt: Instant = Instant.now()
) {
    fun place(): OrderPlaced {
        require(status == OrderStatus.CREATED) { "only CREATED orders can be placed" }
        status = OrderStatus.PLACED
        return OrderPlaced(id, customerId, items.size, Instant.now())
    }
}

enum class OrderStatus { CREATED, PLACED, CONFIRMED, CANCELLED }
