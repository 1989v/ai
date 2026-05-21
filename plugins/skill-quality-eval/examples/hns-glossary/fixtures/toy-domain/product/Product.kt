package com.kgd.example.product

/**
 * Aggregate root for the product catalog. Owns its Sku VO and pricing snapshot.
 */
class Product(
    val sku: Sku,
    val name: String,
    val priceKrw: Long,
    val active: Boolean
)
