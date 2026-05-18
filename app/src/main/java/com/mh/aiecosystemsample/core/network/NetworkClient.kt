package com.mh.aiecosystemsample.core.network

import com.mh.aiecosystemsample.core.logger.AppLogger
import kotlinx.coroutines.delay
import kotlin.random.Random

/**
 * Dummy Network Client for API calls.
 * This simulates a network layer as per the architecture's core infrastructure.
 */
object NetworkClient {

    private const val TAG = "Network"

    /**
     * Simulates a generic GET request with random success/failure.
     */
    suspend fun <T> get(endpoint: String, params: Map<String, String>? = null): NetworkResponse<T> {
        AppLogger.app(TAG, "GET request to: $endpoint with params: $params")
        
        // Simulate network latency
        delay(1500)
        
        // Simulate random failure (20% chance) to test error states
        return if (Random.nextInt(100) > 20) {
            AppLogger.app(TAG, "API called: $endpoint - Success")
            @Suppress("UNCHECKED_CAST")
            NetworkResponse.Success(Unit as T)
        } else {
            AppLogger.app(TAG, "API called: $endpoint - Failed (Simulated)")
            NetworkResponse.Error("Simulated network error for $endpoint", 500)
        }
    }

    /**
     * Simulates a generic POST request.
     */
    suspend fun <T> post(endpoint: String, body: Any? = null): NetworkResponse<T> {
        AppLogger.app(TAG, "POST request to: $endpoint with body: $body")
        delay(1200)
        AppLogger.app(TAG, "API called: $endpoint - Success")
        @Suppress("UNCHECKED_CAST")
        return NetworkResponse.Success(Unit as T)
    }
}

/**
 * Simple wrapper for network responses.
 */
sealed class NetworkResponse<out T> {
    data class Success<out T>(val data: T) : NetworkResponse<T>()
    data class Error(val message: String, val code: Int = -1) : NetworkResponse<Nothing>()
}
