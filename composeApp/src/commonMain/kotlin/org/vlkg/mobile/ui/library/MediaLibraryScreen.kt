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
import org.vlkg.mobile.network.VlkgApiClient
import org.vlkg.mobile.platform.HapticFeedbackHelper
import org.vlkg.mobile.theme.*
import kotlinx.coroutines.launch

@Composable
fun MediaLibraryScreen(
    allVideos: List<VideoMetadata>,
    activeApp: ChildApp?,
    onJumpToVideo: (videoId: String, timestamp: String) -> Unit,
    modifier: Modifier = Modifier
) {
    var searchQuery by remember { mutableStateOf("") }
    var searchMode by remember { mutableStateOf("videos") } // "videos" | "transcripts"
    var transcriptResults by remember { mutableStateOf<List<org.vlkg.mobile.model.TranscriptSearchResultItem>>(emptyList()) }
    var isSearchingTranscripts by remember { mutableStateOf(false) }

    var ingestDialogOpen by remember { mutableStateOf(false) }
    var ingestUrl by remember { mutableStateOf("") }
    var ingestSuccessMsg by remember { mutableStateOf<String?>(null) }
    var isIngesting by remember { mutableStateOf(false) }

    val haptic = remember { HapticFeedbackHelper() }
    val apiClient = remember { VlkgApiClient() }
    val scope = rememberCoroutineScope()

    LaunchedEffect(searchQuery, searchMode) {
        if (searchMode == "transcripts" && searchQuery.trim().length >= 2) {
            isSearchingTranscripts = true
            transcriptResults = apiClient.searchTranscripts(searchQuery.trim())
            isSearchingTranscripts = false
        } else if (searchMode == "transcripts") {
            transcriptResults = emptyList()
        }
    }

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

        // Search Mode Selector (Videos vs Deep Transcripts)
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            FilterChip(
                selected = searchMode == "videos",
                onClick = { searchMode = "videos" },
                label = { Text("📹 Video Catalog (${filteredVideos.size})", fontSize = 11.sp) },
                colors = FilterChipDefaults.filterChipColors(selectedContainerColor = VlkgPrimary, selectedLabelColor = Color.White)
            )
            FilterChip(
                selected = searchMode == "transcripts",
                onClick = { searchMode = "transcripts" },
                label = { Text("📜 Deep Transcript Search", fontSize = 11.sp, fontWeight = FontWeight.Bold) },
                colors = FilterChipDefaults.filterChipColors(selectedContainerColor = VlkgAccent, selectedLabelColor = Color.Black)
            )
        }

        Spacer(modifier = Modifier.height(10.dp))

        // Search Bar
        OutlinedTextField(
            value = searchQuery,
            onValueChange = { searchQuery = it },
            placeholder = { Text(if (searchMode == "videos") "Search by title, topic, or speaker..." else "Search spoken transcript keywords across all 3,184 segments...", color = Color.Gray, fontSize = 12.sp) },
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

        Spacer(modifier = Modifier.height(12.dp))

        if (searchMode == "transcripts") {
            // Transcript Search Results
            if (isSearchingTranscripts) {
                Row(
                    modifier = Modifier.padding(12.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    CircularProgressIndicator(modifier = Modifier.size(16.dp), color = VlkgPrimary, strokeWidth = 2.dp)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Searching across all 3,184 corpus segments...", color = Color.Gray, fontSize = 12.sp)
                }
            } else if (transcriptResults.isEmpty() && searchQuery.trim().length >= 2) {
                Text("No transcript matches found for \"$searchQuery\".", color = Color.Gray, fontSize = 12.sp)
            } else {
                LazyColumn(
                    modifier = Modifier.weight(1f),
                    verticalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    items(transcriptResults) { item ->
                        Card(
                            colors = CardDefaults.cardColors(containerColor = DarkSurface),
                            shape = RoundedCornerShape(12.dp),
                            modifier = Modifier.fillMaxWidth().clickable {
                                haptic.triggerClick()
                                onJumpToVideo(item.video_id, item.timestamp)
                            }
                        ) {
                            Column(modifier = Modifier.padding(12.dp)) {
                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.SpaceBetween,
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Text(item.video_title, color = Color.White, fontSize = 12.sp, fontWeight = FontWeight.Bold, maxLines = 1)
                                    Surface(
                                        color = VlkgAccent.copy(alpha = 0.2f),
                                        shape = RoundedCornerShape(6.dp)
                                    ) {
                                        Text(
                                            text = "[${item.timestamp}]",
                                            color = VlkgAccent,
                                            fontSize = 11.sp,
                                            fontWeight = FontWeight.Bold,
                                            modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                                        )
                                    }
                                }
                                Spacer(modifier = Modifier.height(6.dp))
                                Text(
                                    text = item.text,
                                    color = Color.LightGray,
                                    fontSize = 12.sp,
                                    lineHeight = 16.sp
                                )
                            }
                        }
                    }
                }
            }
        } else {
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
                        val urlToIngest = ingestUrl.trim()
                        ingestDialogOpen = false
                        isIngesting = true
                        scope.launch {
                            val success = apiClient.ingestVideo(urlToIngest, activeApp?.id)
                            isIngesting = false
                            ingestSuccessMsg = if (success) "Video ingested and queued for transcription!" else "Ingestion request failed."
                            ingestUrl = ""
                        }
                    },
                    enabled = ingestUrl.isNotBlank() && !isIngesting,
                    colors = ButtonDefaults.buttonColors(containerColor = VlkgPrimary),
                    shape = RoundedCornerShape(8.dp)
                ) {
                    Text(if (isIngesting) "Ingesting..." else "Ingest Video")
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