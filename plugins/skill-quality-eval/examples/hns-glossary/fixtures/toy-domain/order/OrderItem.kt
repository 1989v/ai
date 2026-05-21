package com.kgd.example.order

import com.kgd.example.product.Sku

/**
 * Entity inside the Order aggregate. Has identity (line-item position) but no independent lifecycle.
 */
class OrderItem(
    val lineNo: Int,
    val sku: Sku,
    var quantity: Int
)
