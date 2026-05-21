package com.kgd.example.product

/**
 * Domain service — cross-aggregate operation that doesn't naturally belong to Product or Order alone.
 * Reserves stock for a sku and returns whether reservation succeeded.
 */
class InventoryService(private val warehouse: WarehousePort) {
    fun reserve(sku: Sku, quantity: Int): Boolean {
        val available = warehouse.availableQuantity(sku)
        if (available < quantity) return false
        warehouse.decrement(sku, quantity)
        return true
    }
}

/**
 * Port — outbound interface to the warehouse bounded context (implemented in infrastructure).
 */
interface WarehousePort {
    fun availableQuantity(sku: Sku): Int
    fun decrement(sku: Sku, quantity: Int)
}
