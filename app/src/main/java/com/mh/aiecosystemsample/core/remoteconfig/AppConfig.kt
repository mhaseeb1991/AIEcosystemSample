package com.mh.aiecosystemsample.core.remoteconfig

/**
 * Data class representing the application configuration fetched from Remote Config.
 */
data class AppConfig(
    val newHomeUiEnabled: Boolean = false,
    val searchFeatureVariant: String = "default",
    val maxRetryCount: Long = 3L
)
