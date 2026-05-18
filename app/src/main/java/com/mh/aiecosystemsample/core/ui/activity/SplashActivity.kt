package com.mh.aiecosystemsample.core.ui.activity

import android.content.Intent
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.lifecycle.lifecycleScope
import com.mh.aiecosystemsample.core.remoteconfig.RemoteConfigManager
import com.mh.aiecosystemsample.core.theme.AIEcosystemPocTheme
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

class SplashActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        
        // Initialize Remote Config
        RemoteConfigManager.init()

        setContent {
            AIEcosystemPocTheme {
                Scaffold(modifier = Modifier.Companion.fillMaxSize()) { innerPadding ->
                    Box(
                        modifier = Modifier.Companion
                            .fillMaxSize()
                            .padding(innerPadding),
                        contentAlignment = Alignment.Companion.Center
                    ) {
                        Text(
                            text = "AI Engineering Ecosystem"
                        )
                    }
                }
            }
        }

        lifecycleScope.launch {
            delay(2000)
            startActivity(Intent(this@SplashActivity, MainActivity::class.java))
            finish()
        }
    }
}
