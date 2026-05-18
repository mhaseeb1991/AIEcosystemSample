package com.mh.aiecosystemsample.core.logger

import android.util.Log

object AppLogger {

    fun ai(agent: String, message: String) {
        Log.d("AI-$agent", message)
    }

    fun app(tag: String, message: String) {
        Log.d(tag, message)
    }
}