package com.mh.aiecosystemsample.core.analytics

import com.mh.aiecosystemsample.core.logger.AppLogger

/**
 * Dummy Analytics Manager.
 * Simulates Firebase Analytics behavior.
 */
object AnalyticsManager {

    private const val TAG = "Analytics"

    fun trackEvent(eventName: String, params: Map<String, Any>? = null) {
        val paramsString = params?.let { " with params: $it" } ?: ""
        AppLogger.app(TAG, "Event Tracked: $eventName$paramsString")
    }

    fun setUserProperty(name: String, value: String) {
        AppLogger.app(TAG, "User Property Set: $name = $value")
    }

    fun trackScreen(screenName: String) {
        AppLogger.app(TAG, "Screen Tracked: $screenName")
    }
}
