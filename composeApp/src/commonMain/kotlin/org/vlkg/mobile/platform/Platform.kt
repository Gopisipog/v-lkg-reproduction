package org.vlkg.mobile.platform

interface Platform {
    val name: String
    val isIos: Boolean
    val isAndroid: Boolean
}

expect fun getPlatform(): Platform

expect class PlatformUriLauncher() {
    fun openUri(uriString: String)
}

expect class HapticFeedbackHelper() {
    fun triggerClick()
    fun triggerSuccess()
}
