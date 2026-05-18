package com.mh.aiecosystemsample.core.remoteconfig

import com.mh.aiecosystemsample.core.logger.AppLogger

/**
 * Remote Config Manager for A/B testing and Feature Flags.
 * This simulates Firebase Remote Config behavior.
 */
object RemoteConfigManager {

    private const val TAG = "RemoteConfig"

    // Simulating a fetch result using the defined keys
    private val configs = mutableMapOf<String, Any>(
        RemoteConfigKeys.NEW_HOME_UI_ENABLED to true,
        RemoteConfigKeys.SEARCH_FEATURE_VARIANT to "variant_b",
        RemoteConfigKeys.MAX_RETRY_COUNT to 5L
    )

    fun init() {
        AppLogger.app(TAG, "Initializing Simulated Remote Config")
        // In a real app, you would call FirebaseRemoteConfig.getInstance().fetchAndActivate()
    }

    /**
     * Maps the remote config values to the [AppConfig] POJO.
     */
    fun getAppConfig(): AppConfig {
        return AppConfig(
            newHomeUiEnabled = isFeatureEnabled(RemoteConfigKeys.NEW_HOME_UI_ENABLED),
            searchFeatureVariant = getString(RemoteConfigKeys.SEARCH_FEATURE_VARIANT),
            maxRetryCount = getLong(RemoteConfigKeys.MAX_RETRY_COUNT)
        )
    }

    /**
     * Gets a boolean feature flag.
     */
    fun isFeatureEnabled(key: String): Boolean {
        val value = configs[key] as? Boolean ?: false
        AppLogger.app(TAG, "Feature Flag: $key = $value")
        return value
    }

    /**
     * Gets a string value (e.g., for A/B test variants).
     */
    fun getString(key: String): String {
        val value = configs[key] as? String ?: ""
        AppLogger.app(TAG, "Config String: $key = $value")
        return value
    }

    /**
     * Gets a long value.
     */
    fun getLong(key: String): Long {
        val value = configs[key] as? Long ?: 0L
        AppLogger.app(TAG, "Config Long: $key = $value")
        return value
    }
}
