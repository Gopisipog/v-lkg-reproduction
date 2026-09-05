package org.vlkg.mobile.platform

import java.awt.Desktop
import java.net.URI

class DesktopPlatform : Platform {
    override val name: String = "Desktop JVM (${System.getProperty("os.name")})"
    override val isIos: Boolean = false
    override val isAndroid: Boolean = false
}

actual fun getPlatform(): Platform = DesktopPlatform()

actual class PlatformUriLauncher {
    actual fun openUri(uriString: String) {
        try {
            if (Desktop.isDesktopSupported() && Desktop.getDesktop().isSupported(Desktop.Action.BROWSE)) {
                Desktop.getDesktop().browse(URI(uriString))
            }
        } catch (_: Exception) {}
    }
}

actual class HapticFeedbackHelper {
    actual fun triggerClick() {}
    actual fun triggerSuccess() {}
}