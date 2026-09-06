package org.vlkg.mobile.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

val VlkgPrimary = Color(0xFF0EA5E9) // Electric Cyan (Cockpit Focus)
val VlkgSecondary = Color(0xFF10B981) // Emerald Telemetry
val VlkgTertiary = Color(0xFF38BDF8) // Sky Accent
val VlkgAccent = Color(0xFFF59E0B) // Amber Milestone

val DarkBackground = Color(0xFF020617) // Slate 950
val DarkSurface = Color(0xFF0F172A) // Slate 900
val DarkSurfaceVariant = Color(0xFF1E293B) // Slate 800
val DarkOnBackground = Color(0xFFF8FAFC)
val DarkOnSurface = Color(0xFFE2E8F0)
val DarkOutline = Color(0xFF1E293B) // Hairline Divider Slate 800

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
    primary = Color(0xFF0284C7),
    secondary = Color(0xFF059669),
    tertiary = Color(0xFF0284C7),
    background = Color(0xFFF8FAFC),
    surface = Color(0xFFFFFFFF),
    surfaceVariant = Color(0xFFF1F5F9),
    onBackground = Color(0xFF0F172A),
    onSurface = Color(0xFF1E293B),
    outline = Color(0xFFE2E8F0)
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