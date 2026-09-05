package org.vlkg.mobile.ui.library

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.vlkg.mobile.model.ChildApp
import org.vlkg.mobile.model.VideoMetadata
import org.vlkg.mobile.platform.HapticFeedbackHelper
import org.vlkg.mobile.theme.*

@Composable
fun MediaLibraryScreen(
    allVideos: List<VideoMetadata>,
    activeApp: ChildApp?,
    onJumpToVideo: (videoId: String, timestamp: String) -> Unit,
    modifier: Modifier = Modifier
) {
    var searchQuery by remember { mutableStateOf("") }
    var ingestDialogOpen by remember { mutableStateOf(false) }
    var ingestUrl by remember { mutableStateOf("") }
    var ingestSuccessMsg by remember { mutableStateOf<String?>(null) }
    val haptic = remember { HapticFeedbackHelper() }

    val filteredVideos = allVideos.filter {
        searchQuery.isBlank() ||
                it.title.contains(searchQuery, ignoreCase = true) ||
                it.channel.contains(searchQuery, ignoreCase = true) ||
                it.summary.contains(searchQuery, ignoreCase = true)
    }

    Column(
        modifier = modifier
            .fillMaxSize()
            .background(DarkBackground)
            .padding(16.dp)
    ) {
        // Header
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column {
                Text("Video Knowledge Library", color = DarkOnBackground, fontSize = 18.sp, fontWeight = FontWeight.Bold)
                Text("${allVideos.size} Ingested Talks & Transcripts", color = Color.Gray, fontSize = 11.sp)
            }

            Button(
                onClick = { ingestDialogOpen = true },
                colors = ButtonDefaults.buttonColors(containerColor = VlkgPrimary),
                shape = RoundedCornerShape(8.dp),
                contentPadding = PaddingValues(horizontal = 10.dp, vertical = 6.dp)
            ) {
                Text("+ Ingest Video", fontSize = 11.sp, fontWeight = FontWeight.Bold)
            }
        }

        Spacer(modifier = Modifier.height(12.dp))

        // Search Bar
        OutlinedTextField(
            value = searchQuery,
            onValueChange = { searchQuery = it },
            placeholder = { Text("Search by title, topic, or speaker...", color = Color.Gray) },
            singleLine = true,
            colors = OutlinedTextFieldDefaults.colors(
                focusedTextColor = DarkOnBackground,
                unfocusedTextColor = DarkOnBackground,
                focusedBorderColor = VlkgPrimary,
                unfocusedBorderColor = DarkOutline
            ),
            shape = RoundedCornerShape(12.dp),
            modifier = Modifier.fillMaxWidth()
        )

        Spacer(modifier = Modifier.height(14.dp))

        // Video Catalog List
        LazyColumn(
            modifier = Modifier.weight(1f),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            items(filteredVideos) { video ->
                val durationMin = video.duration_sec / 60
                val durationSec = video.duration_sec % 60

                Card(
                    colors = CardDefaults.cardColors(containerColor = DarkSurface),
                    shape = RoundedCornerShape(14.dp),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(modifier = Modifier.padding(14.dp)) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Surface(
                                color = VlkgSecondary.copy(alpha = 0.2f),
                                shape = RoundedCornerShape(6.dp)
                            ) {
                                Text(
                                    text = video.channel,
                                    color = VlkgSecondary,
                                    fontSize = 10.sp,
                                    fontWeight = FontWeight.Bold,
                                    modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                                )
                            }

                            Text(
                                text = "${durationMin}m ${durationSec}s",
                                color = Color.Gray,
                                fontSize = 11.sp
                            )
                        }

                        Spacer(modifier = Modifier.height(8.dp))

                        Text(
                            text = video.title,
                            color = DarkOnBackground,
                            fontSize = 15.sp,
                            fontWeight = FontWeight.Bold
                        )

                        Spacer(modifier = Modifier.height(4.dp))

                        Text(
                            text = video.summary,
                            color = Color.LightGray,
                            fontSize = 12.sp,
                            maxLines = 2,
                            lineHeight = 16.sp
                        )

                        Spacer(modifier = Modifier.height(10.dp))

                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(
                                text = "${video.segment_count} Time-Aligned Segments",
                                color = Color.Gray,
                                fontSize = 11.sp
                            )

                            Button(
                                onClick = {
                                    haptic.triggerClick()
                                    onJumpToVideo(video.video_id, "00:00")
                                },
                                colors = ButtonDefaults.buttonColors(containerColor = VlkgPrimary.copy(alpha = 0.85f)),
                                shape = RoundedCornerShape(6.dp),
                                contentPadding = PaddingValues(horizontal = 10.dp, vertical = 4.dp)
                            ) {
                                Text("Play & Transcripts ➔", fontSize = 11.sp)
                            }
                        }
                    }
                }
            }
        }
    }

    // Ingestion Dialog
    if (ingestDialogOpen) {
        AlertDialog(
            onDismissRequest = { ingestDialogOpen = false },
            containerColor = DarkSurface,
            title = {
                Text("Ingest YouTube Video", color = DarkOnBackground, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            },
            text = {
                Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    Text(
                        text = "Paste a YouTube link to transcribe via Whisper and extract semantic triplets into ${activeApp?.name ?: "Library"}.",
                        color = Color.LightGray,
                        fontSize = 12.sp
                    )
                    OutlinedTextField(
                        value = ingestUrl,
                        onValueChange = { ingestUrl = it },
                        placeholder = { Text("https://www.youtube.com/watch?v=...", color = Color.Gray) },
                        singleLine = true,
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedTextColor = DarkOnBackground,
                            unfocusedTextColor = DarkOnBackground,
                            focusedBorderColor = VlkgPrimary,
                            unfocusedBorderColor = DarkOutline
                        ),
                        modifier = Modifier.fillMaxWidth()
                    )
                }
            },
            confirmButton = {
                Button(
                    onClick = {
                        haptic.triggerSuccess()
                        ingestDialogOpen = false
                        ingestSuccessMsg = "Ingestion queued for processing!"
                    },
                    enabled = ingestUrl.isNotBlank(),
                    colors = ButtonDefaults.buttonColors(containerColor = VlkgPrimary),
                    shape = RoundedCornerShape(8.dp)
                ) {
                    Text("Ingest Video")
                }
            },
            dismissButton = {
                TextButton(onClick = { ingestDialogOpen = false }) {
                    Text("Cancel", color = Color.Gray)
                }
            }
        )
    }
}