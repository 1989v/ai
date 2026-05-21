package com.kgd.example.product

/**
 * Value object representing a stock-keeping unit. Immutable string identifier.
 */
@JvmInline
value class Sku(val code: String) {
    init {
        require(code.matches(Regex("[A-Z0-9-]{4,32}"))) { "invalid sku: $code" }
    }
}
