package com.sullivanxiong.minimalist.ui.theme

import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

// Dark theme matching desktop client
val BgPrimary = Color(0xFF0D0D0D)
val BgSecondary = Color(0xFF141414)
val BgSurface = Color(0xFF1A1A1A)
val BgHover = Color(0xFF222222)
val TextPrimary = Color(0xFFEBEBEB)
val TextSecondary = Color(0xFF8A8A8A)
val TextMuted = Color(0xFF5C5C5C)
val AccentPurple = Color(0xFF7C5CFC)
val AccentBlue = Color(0xFF5E6AD2)
val AccentGreen = Color(0xFF10B981)
val AccentYellow = Color(0xFFF59E0B)
val AccentRed = Color(0xFFEF4444)

private val DarkColorScheme = darkColorScheme(
    primary = AccentPurple,
    secondary = AccentBlue,
    background = BgPrimary,
    surface = BgSurface,
    onPrimary = TextPrimary,
    onSecondary = TextPrimary,
    onBackground = TextPrimary,
    onSurface = TextPrimary,
    error = AccentRed,
)

@Composable
fun MinimalistTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = DarkColorScheme,
        content = content,
    )
}
