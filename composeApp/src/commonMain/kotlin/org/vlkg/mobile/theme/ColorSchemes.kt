package org.vlkg.mobile.theme

import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import org.vlkg.mobile.model.ChildApp

data class SchemePreset(
    val id: String,
    val name: String,
    val type: String, // "bi" | "tri"
    val colors: List<String>,
    val description: String
)

data class PatternMode(
    val id: String,
    val name: String,
    val type: String,
    val description: String
)

val BI_COLOR_PRESETS = listOf(
    SchemePreset("cyber-cyan", "Cyber Cyan & Emerald", "bi", listOf("#0EA5E9", "#10B981"), "High-contrast technical telemetry"),
    SchemePreset("solar-rose", "Solar Amber & Rose", "bi", listOf("#F59E0B", "#F43F5E"), "Vibrant executive urgency"),
    SchemePreset("ultraviolet", "Ultraviolet & Azure", "bi", listOf("#8B5CF6", "#3B82F6"), "Deep cognitive analytical focus"),
    SchemePreset("quantum-flux", "Quantum Flux & Indigo", "bi", listOf("#06B6D4", "#6366F1"), "Multi-agent systems synthesis"),
    SchemePreset("emerald-gold", "Emerald Gold & Lime", "bi", listOf("#10B981", "#EAB308"), "Growth & strategic capital expansion"),
    SchemePreset("hyper-plasma", "Hyper Plasma & Violet", "bi", listOf("#EC4899", "#8B5CF6"), "High-velocity product innovation")
)

val TRI_COLOR_PRESETS = listOf(
    SchemePreset("aurora-chromatic", "Aurora Chromatic", "tri", listOf("#0EA5E9", "#10B981", "#8B5CF6"), "Full-spectrum intelligence tri-band"),
    SchemePreset("solar-flare", "Solar Flare Dynamic", "tri", listOf("#F59E0B", "#EF4444", "#8B5CF6"), "High-energy executive strategic command"),
    SchemePreset("matrix-core", "Matrix Core Terminal", "tri", listOf("#10B981", "#06B6D4", "#3B82F6"), "Cybernetic graph density & telemetry"),
    SchemePreset("synthwave-pulse", "Synthwave Pulse", "tri", listOf("#EC4899", "#8B5CF6", "#06B6D4"), "Creative thought leadership spectrum"),
    SchemePreset("titanium-cockpit", "Titanium Cockpit", "tri", listOf("#64748B", "#0EA5E9", "#10B981"), "Precision aerospace telemetry aesthetic")
)

val PATTERN_MODES = listOf(
    PatternMode("gradient-bi", "Linear Bi-Gradient", "bi", "Smooth 2-color linear interpolation"),
    PatternMode("gradient-tri", "3-Stop Tri-Gradient", "tri", "Tri-point chromatic spectrum sweep"),
    PatternMode("duotone", "Split Duotone", "bi", "Sharp 50/50 dual contrast boundary"),
    PatternMode("stripe-tri", "Tri-Stripe Telemetry", "tri", "Three parallel energy tracks"),
    PatternMode("radial-mesh", "Ambient Radial Mesh", "all", "Atmospheric center-out radial bloom")
)

fun getColorsForApp(app: ChildApp?): List<Color> {
    if (app == null) return listOf(VlkgPrimary, VlkgSecondary)
    if (app.pattern_colors.isNotEmpty()) {
        return app.pattern_colors.map { parseHexColor(it) }
    }
    val matched = (BI_COLOR_PRESETS + TRI_COLOR_PRESETS).find { it.id == app.color_scheme }
    if (matched != null) {
        return matched.colors.map { parseHexColor(it) }
    }
    val base = parseHexColor(app.theme_color)
    return listOf(base, VlkgSecondary)
}

fun getPatternBrush(pattern: String?, colors: List<Color>): Brush {
    val effectiveColors = if (colors.size >= 2) colors else listOf(colors.firstOrNull() ?: VlkgPrimary, VlkgSecondary)
    return when (pattern) {
        "duotone" -> {
            val c1 = effectiveColors[0]
            val c2 = effectiveColors.getOrElse(1) { c1 }
            Brush.horizontalGradient(listOf(c1, c1, c2, c2))
        }
        "stripe-tri" -> {
            if (effectiveColors.size >= 3) {
                Brush.verticalGradient(effectiveColors.take(3))
            } else {
                Brush.verticalGradient(effectiveColors)
            }
        }
        "radial-mesh" -> {
            Brush.radialGradient(
                colors = effectiveColors,
                center = Offset.Unspecified,
                radius = Float.POSITIVE_INFINITY
            )
        }
        "gradient-tri" -> {
            Brush.linearGradient(effectiveColors)
        }
        else -> {
            Brush.linearGradient(effectiveColors)
        }
    }
}
