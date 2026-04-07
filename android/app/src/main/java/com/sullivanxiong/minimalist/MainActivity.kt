package com.sullivanxiong.minimalist

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import com.sullivanxiong.minimalist.ui.MinimalistApp
import com.sullivanxiong.minimalist.ui.theme.MinimalistTheme
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            MinimalistTheme {
                MinimalistApp()
            }
        }
    }
}
