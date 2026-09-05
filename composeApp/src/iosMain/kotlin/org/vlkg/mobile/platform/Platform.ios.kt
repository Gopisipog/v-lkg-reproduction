package org.vlkg.mobile.platform

import platform.Foundation.NSURL
import platform.UIKit.UIApplication
import platform.UIKit.UIDevice
import platform.UIKit.UIImpactFeedbackGenerator
import platform.UIKit.UIImpactFeedbackStyle
import platform.UIKit.UINotificationFeedbackGenerator
import platform.UIKit.UINotificationFeedbackType

class IOSPlatform : Platform {
    override val name: String = UIDevice.currentDevice.systemName() + " " + UIDevice.currentDevice.systemVersion
    override val isIos: Boolean = true
    override val isAndroid: Boolean = false
}

actual fun getPlatform(): Platform = IOSPlatform()

actual class PlatformUriLauncher {
    actual fun openUri(uriString: String) {
        val nsUrl = NSURL.URLWithString(uriString) ?: return
        UIApplication.sharedApplication.openURL(nsUrl)
    }
}

actual class HapticFeedbackHelper {
    actual fun triggerClick() {
        val generator = UIImpactFeedbackGenerator(UIImpactFeedbackStyle.UIImpactFeedbackStyleMedium)
        generator.prepare()
        generator.impactOccurred()
    }

    actual fun triggerSuccess() {
        val generator = UINotificationFeedbackGenerator()
        generator.prepare()
        generator.notificationOccurred(UINotificationFeedbackType.UINotificationFeedbackTypeSuccess)
    }
}
