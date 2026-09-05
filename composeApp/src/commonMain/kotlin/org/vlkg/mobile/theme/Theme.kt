package org.vlkg.mobile.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

val VlkgPrimary = Color(0xFF6366F1) // Electric Indigo
val VlkgSecondary = Color(0xFF06B6D4) // Radiant Cyan
val VlkgTertiary = Color(0xFF10B981) // Emerald Evidence
val VlkgAccent = Color(0xFFF59E0B) // Amber Milestone

val DarkBackground = Color(0xFF090D16)
val DarkSurface = Color(0xFF131926)
val DarkSurfaceVariant = Color(0xFF1E293B)
val DarkOnBackground = Color(0xFFF8FAFC)
val DarkOnSurface = Color(0xFFE2E8F0)
val DarkOutline = Color(0xFF334155)

private val DarkColorScheme = darkColorScheme(
    primary = VlkgPrimary,
    secondary = VlkgSecondary,
    tertiary = VlkgTertiary,
    background = DarkBackground,
    surface = DarkSurface,
    surfaceVariant = DarkSurfaceVariant,
    onBackground = DarkOnBackground,
    onSurface = DarkOnSurface,
    outline = DarkOutline
)

private val LightColorScheme = lightColorScheme(
    primary = Color(0xFF4F46E5),
    secondary = Color(0xFF0891B2),
    tertiary = Color(0xFF059669),
    background = Color(0xFFF8FAFC),
    surface = Color(0xFFFFFFFF),
    surfaceVariant = Color(0xFFF1F5F9),
    onBackground = Color(0xFF0F172A),
    onSurface = Color(0xFF1E293B),
    outline = Color(0xFFCBD5E1)
)

fun parseHexColor(hex: String, defaultColor: Color = VlkgPrimary): Color {
    return try {
        val clean = hex.removePrefix("#")
        val colorInt = clean.toLong(16)
        if (clean.length == 6) {
            Color(0xFF000000 or colorInt)
        } else if (clean.length == 8) {
            Color(colorInt)
        } else {
            defaultColor
        }
    } catch (_: Exception) {
        defaultColor
    }
}

@Composable
fun VlkgTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    val colorScheme = if (darkTheme) DarkColorScheme else LightColorScheme

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography(),
        content = content
    )
}