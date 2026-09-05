package org.vlkg.mobile

import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Window
import androidx.compose.ui.window.WindowState
import androidx.compose.ui.window.application

fun main() = application {
    Window(
        onCloseRequest = ::exitApplication,
        title = "V-LKG Mobile - Knowledge Graph Navigator",
        state = WindowState(width = 440.dp, height = 900.dp)
    ) {
        App()
    }
}