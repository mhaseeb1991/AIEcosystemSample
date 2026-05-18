package com.mh.aiecosystemsample.core.ui.activity

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import com.mh.aiecosystemsample.core.navigation.AppNavHost
import com.mh.aiecosystemsample.core.theme.AIEcosystemPocTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            AIEcosystemPocTheme {
                AppNavHost()
            }
        }
    }
}