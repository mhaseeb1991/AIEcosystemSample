package com.mh.aiecosystemsample.core.network

import com.mh.aiecosystemsample.core.logger.AppLogger

/**
 * Data model for User Profile.
 */
data class UserProfile(
    val id: String,
    val name: String,
    val email: String,
    val avatarUrl: String? = null
)

/**
 * Repository for User Profile feature.
 * Acts as a bridge between the ViewModel and the Network Layer.
 */
class Repository {

    /**
     * Simulates fetching user profile from a remote API.
     */
    suspend fun getApiCallSimulation(): NetworkResponse<UserProfile> {
        AppLogger.app("Repository", "Requesting user profile from NetworkClient")
        
        // Simulating the API endpoint call
        val response = NetworkClient.get<Unit>("/user/profile")
        
        return when (response) {
            is NetworkResponse.Success -> {
                AppLogger.app("Repository", "Network success, mapping to UserProfile model")
                // Return dummy data on success
                NetworkResponse.Success(
                    UserProfile(
                        id = "123",
                        name = "John Doe",
                        email = "john.doe@example.com",
                        avatarUrl = "https://example.com/avatar.png"
                    )
                )
            }
            is NetworkResponse.Error -> {
                AppLogger.app("Repository", "Network error: ${response.message}")
                NetworkResponse.Error(response.message, response.code)
            }
        }
    }
}
