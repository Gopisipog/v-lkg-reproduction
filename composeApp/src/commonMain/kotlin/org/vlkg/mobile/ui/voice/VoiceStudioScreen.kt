package org.vlkg.mobile.ui.voice

import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.vlkg.mobile.model.ChildApp
import org.vlkg.mobile.platform.HapticFeedbackHelper
import org.vlkg.mobile.theme.*
import org.vlkg.mobile.viewmodel.VoiceStudioViewModel

@Composable
fun VoiceStudioScreen(
    activeApp: ChildApp?,
    onRecordingSaved: () -> Unit,
    voiceViewModel: VoiceStudioViewModel = remember { VoiceStudioViewModel() },
    modifier: Modifier = Modifier
) {
    val voiceState by voiceViewModel.uiState.collectAsState()
    val haptic = remember { HapticFeedbackHelper() }
    var noteTitle by remember { mutableStateOf("Leadership Field Note") }

    val infiniteTransition = rememberInfiniteTransition(label = "micPulse")
    val pulseSize by infiniteTransition.animateFloat(
        initialValue = 72f,
        targetValue = 96f,
        animationSpec = infiniteRepeatable(
            animation = tween(900, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "pulseSize"
    )

    LazyColumn(
        modifier = modifier
            .fillMaxSize()
            .background(DarkBackground)
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(18.dp)
    ) {
        item {
            Text(
                text = "Live Voice Studio",
                color = DarkOnBackground,
                fontSize = 20.sp,
                fontWeight = FontWeight.Bold
            )
            Text(
                text = "Capture executive thoughts with real-time semantic entity extraction",
                color = Color.Gray,
                fontSize = 12.sp
            )
        }

        // Active Target App Banner
        item {
            Surface(
                color = DarkSurface,
                shape = RoundedCornerShape(12.dp),
                modifier = Modifier.fillMaxWidth()
            ) {
                Row(
                    modifier = Modifier.padding(12.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(text = "🎯", fontSize = 16.sp)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = "Recording directly into: ${activeApp?.name ?: "Executive Leadership"}",
                        color = VlkgSecondary,
                        fontSize = 12.sp,
                        fontWeight = FontWeight.SemiBold
                    )
                }
            }
        }

        // Animated Microphone & Waveform Section
        item {
            Card(
                colors = CardDefaults.cardColors(containerColor = DarkSurface),
                shape = RoundedCornerShape(24.dp),
                modifier = Modifier.fillMaxWidth().height(220.dp)
            ) {
                Column(
                    modifier = Modifier.fillMaxSize().padding(16.dp),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.Center
                ) {
                    // Pulsing Record Button
                    Box(
                        modifier = Modifier
                            .size(if (voiceState.isRecording) pulseSize.dp else 72.dp)
                            .clip(CircleShape)
                            .background(
                                if (voiceState.isRecording) Color(0xFFEF4444).copy(alpha = 0.25f)
                                else VlkgPrimary.copy(alpha = 0.2f)
                            ),
                        contentAlignment = Alignment.Center
                    ) {
                        FloatingActionButton(
                            onClick = {
                                haptic.triggerClick()
                                voiceViewModel.toggleRecording()
                            },
                            containerColor = if (voiceState.isRecording) Color(0xFFEF4444) else VlkgPrimary,
                            contentColor = Color.White,
                            shape = CircleShape,
                            modifier = Modifier.size(60.dp)
                        ) {
                            Text(text = if (voiceState.isRecording) "⏹" else "🎙️", fontSize = 24.sp)
                        }
                    }

                    Spacer(modifier = Modifier.height(14.dp))

                    Text(
                        text = if (voiceState.isRecording) "Recording (${voiceState.durationSeconds}s)..." else "Tap to Record Thought",
                        color = if (voiceState.isRecording) Color(0xFFEF4444) else Color.LightGray,
                        fontSize = 13.sp,
                        fontWeight = FontWeight.Bold
                    )

                    // Audio Waveform Visualizer Bars
                    if (voiceState.isRecording) {
                        Spacer(modifier = Modifier.height(10.dp))
                        Row(
                            horizontalArrangement = Arrangement.spacedBy(4.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            voiceState.waveforms.forEach { wave ->
                                Box(
                                    modifier = Modifier
                                        .width(4.dp)
                                        .height((wave * 32).dp.coerceAtLeast(6.dp))
                                        .clip(RoundedCornerShape(2.dp))
                                        .background(VlkgSecondary)
                                )
                            }
                        }
                    }
                }
            }
        }

        // Live Real-Time Transcript Stream
        if (voiceState.liveTranscript.isNotBlank()) {
            item {
                Card(
                    colors = CardDefaults.cardColors(containerColor = DarkSurfaceVariant),
                    shape = RoundedCornerShape(14.dp),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(modifier = Modifier.padding(14.dp)) {
                        Text(
                            text = "Live Transcription:",
                            color = VlkgSecondary,
                            fontSize = 11.sp,
                            fontWeight = FontWeight.Bold
                        )
                        Spacer(modifier = Modifier.height(6.dp))
                        Text(
                            text = "\"${voiceState.liveTranscript}\"",
                            color = DarkOnBackground,
                            fontSize = 13.sp,
                            lineHeight = 18.sp
                        )
                    }
                }
            }
        }

        // Live Extracted Entities
        if (voiceState.suggestedEntities.isNotEmpty()) {
            item {
                Card(
                    colors = CardDefaults.cardColors(containerColor = DarkSurface),
                    shape = RoundedCornerShape(14.dp),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(modifier = Modifier.padding(14.dp)) {
                        Text(
                            text = "⚡ Real-Time Mined Entities:",
                            color = VlkgAccent,
                            fontSize = 11.sp,
                            fontWeight = FontWeight.Bold
                        )
                        Spacer(modifier = Modifier.height(8.dp))
                        Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                            voiceState.suggestedEntities.forEach { ent ->
                                Surface(
                                    color = VlkgPrimary.copy(alpha = 0.2f),
                                    shape = RoundedCornerShape(6.dp)
                                ) {
                                    Text(
                                        text = "+ $ent",
                                        color = VlkgPrimary,
                                        fontSize = 11.sp,
                                        fontWeight = FontWeight.SemiBold,
                                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                                    )
                                }
                            }
                        }
                    }
                }
            }
        }

        // Save Recording Button
        if (!voiceState.isRecording && voiceState.liveTranscript.isNotBlank()) {
            item {
                Button(
                    onClick = {
                        haptic.triggerSuccess()
                        voiceViewModel.saveRecording(noteTitle, activeApp?.id) {
                            onRecordingSaved()
                        }
                    },
                    colors = ButtonDefaults.buttonColors(containerColor = VlkgTertiary),
                    shape = RoundedCornerShape(12.dp),
                    modifier = Modifier.fillMaxWidth().height(48.dp)
                ) {
                    Text("Save Voice Note to ${activeApp?.name ?: "App"}", fontWeight = FontWeight.Bold)
                }
            }
        }
    }
}