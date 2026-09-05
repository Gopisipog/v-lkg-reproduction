package org.vlkg.mobile.ui.player

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
import org.vlkg.mobile.model.TranscriptSegment
import org.vlkg.mobile.model.VideoMetadata
import org.vlkg.mobile.network.VlkgApiClient
import org.vlkg.mobile.platform.HapticFeedbackHelper
import org.vlkg.mobile.platform.PlatformUriLauncher
import org.vlkg.mobile.theme.*

@Composable
fun VideoPlayerScreen(
    activeApp: ChildApp?,
    allVideos: List<VideoMetadata>,
    initialVideoId: String? = null,
    initialTimestamp: String? = null,
    modifier: Modifier = Modifier
) {
    val uriLauncher = remember { PlatformUriLauncher() }
    val haptic = remember { HapticFeedbackHelper() }
    val apiClient = remember { VlkgApiClient() }

    // Filter videos assigned to this child app
    val appVideos = remember(activeApp, allVideos) {
        val assignedIds = activeApp?.video_ids ?: emptyList()
        val filtered = allVideos.filter { assignedIds.contains(it.video_id) }
        if (filtered.isNotEmpty()) filtered else allVideos
    }

    var selectedVideo by remember(appVideos, initialVideoId) {
        mutableStateOf(appVideos.firstOrNull { it.video_id == initialVideoId } ?: appVideos.firstOrNull())
    }

    var activeTimestamp by remember(initialTimestamp) {
        mutableStateOf(initialTimestamp ?: "00:00")
    }

    var transcriptSegments by remember { mutableStateOf<List<TranscriptSegment>>(emptyList()) }
    var semanticsData by remember { mutableStateOf<org.vlkg.mobile.model.VideoSemanticsResponse?>(null) }
    var selectedTab by remember { mutableStateOf("transcript") } // "transcript" | "semantics" | "triplets"
    var searchQuery by remember { mutableStateOf("") }
    var isLoadingSemantics by remember { mutableStateOf(false) }

    LaunchedEffect(selectedVideo) {
        selectedVideo?.let { v ->
            isLoadingSemantics = true
            transcriptSegments = apiClient.getVideoTranscript(v.video_id)
            semanticsData = apiClient.getVideoSemantics(v.video_id)
            isLoadingSemantics = false
        }
    }

    LazyColumn(
        modifier = modifier
            .fillMaxSize()
            .background(DarkBackground)
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(14.dp)
    ) {
        // Video Switcher Carousel
        item {
            Text("Videos in this App", color = Color.Gray, fontSize = 12.sp, fontWeight = FontWeight.SemiBold)
            Spacer(modifier = Modifier.height(6.dp))
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                appVideos.take(4).forEach { video ->
                    val isSelected = video.video_id == selectedVideo?.video_id
                    FilterChip(
                        selected = isSelected,
                        onClick = {
                            haptic.triggerClick()
                            selectedVideo = video
                        },
                        label = {
                            Text(
                                text = video.title.take(18) + "...",
                                fontSize = 11.sp
                            )
                        },
                        colors = FilterChipDefaults.filterChipColors(
                            selectedContainerColor = VlkgPrimary,
                            selectedLabelColor = Color.White,
                            containerColor = DarkSurfaceVariant,
                            labelColor = Color.LightGray
                        )
                    )
                }
            }
        }

        // Active Video Header Card
        item {
            Card(
                colors = CardDefaults.cardColors(containerColor = DarkSurface),
                shape = RoundedCornerShape(16.dp),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Surface(
                            color = VlkgSecondary.copy(alpha = 0.2f),
                            shape = RoundedCornerShape(8.dp)
                        ) {
                            Text(
                                text = selectedVideo?.channel ?: "Leadership Talk",
                                color = VlkgSecondary,
                                fontSize = 11.sp,
                                fontWeight = FontWeight.Bold,
                                modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                            )
                        }

                        Surface(
                            color = VlkgAccent.copy(alpha = 0.2f),
                            shape = RoundedCornerShape(8.dp)
                        ) {
                            Text(
                                text = "⏱ $activeTimestamp",
                                color = VlkgAccent,
                                fontSize = 12.sp,
                                fontWeight = FontWeight.Bold,
                                modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                            )
                        }
                    }

                    Spacer(modifier = Modifier.height(10.dp))

                    Text(
                        text = selectedVideo?.title ?: "Video Evidence",
                        color = DarkOnBackground,
                        fontSize = 17.sp,
                        fontWeight = FontWeight.Bold
                    )

                    Spacer(modifier = Modifier.height(6.dp))

                    Text(
                        text = selectedVideo?.summary ?: "Video summary and core takeaways...",
                        color = Color.LightGray,
                        fontSize = 12.sp,
                        maxLines = 3
                    )

                    Spacer(modifier = Modifier.height(12.dp))

                    Button(
                        onClick = {
                            haptic.triggerClick()
                            val vid = selectedVideo?.video_id ?: ""
                            val cleanSec = activeTimestamp.split(":").let { parts ->
                                if (parts.size == 2) (parts[0].toIntOrNull() ?: 0) * 60 + (parts[1].toIntOrNull() ?: 0) else 0
                            }
                            val url = "https://www.youtube.com/watch?v=$vid&t=${cleanSec}s"
                            uriLauncher.openUri(url)
                        },
                        colors = ButtonDefaults.buttonColors(containerColor = VlkgPrimary),
                        shape = RoundedCornerShape(8.dp),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text("▶ Watch on YouTube at $activeTimestamp", fontSize = 13.sp, fontWeight = FontWeight.SemiBold)
                    }
                }
            }
        }

        // View Mode Selector Tabs
        item {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                listOf(
                    "transcript" to "📜 Transcript",
                    "semantics" to "🏷️ Semantic Pills (${semanticsData?.extracted_pills?.sumOf { it.entities.size } ?: 0})",
                    "triplets" to "🕸️ Triplets (${semanticsData?.relationship_count ?: 0})"
                ).forEach { (tabId, tabLabel) ->
                    val isSelected = selectedTab == tabId
                    FilterChip(
                        selected = isSelected,
                        onClick = {
                            haptic.triggerClick()
                            selectedTab = tabId
                        },
                        label = { Text(tabLabel, fontSize = 11.sp, fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Normal) },
                        colors = FilterChipDefaults.filterChipColors(
                            selectedContainerColor = VlkgPrimary,
                            selectedLabelColor = Color.White,
                            containerColor = DarkSurfaceVariant,
                            labelColor = Color.LightGray
                        )
                    )
                }
            }
        }

        if (selectedTab == "semantics") {
            // Semantic Pills Display (Extracted, Enriched, Intelligences)
            val allPills = (semanticsData?.extracted_pills ?: emptyList()) + 
                           (semanticsData?.enriched_pills ?: emptyList()) + 
                           (semanticsData?.intel_pills ?: emptyList())

            if (allPills.isEmpty()) {
                item {
                    Text("No semantic pills found for this video.", color = Color.Gray, fontSize = 12.sp)
                }
            } else {
                items(allPills) { pillGroup ->
                    Card(
                        colors = CardDefaults.cardColors(containerColor = DarkSurface),
                        shape = RoundedCornerShape(12.dp),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Column(modifier = Modifier.padding(12.dp)) {
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Text(
                                    text = pillGroup.type,
                                    color = VlkgPrimary,
                                    fontSize = 12.sp,
                                    fontWeight = FontWeight.Bold
                                )
                                Text(
                                    text = "${pillGroup.entities.size} concepts",
                                    color = Color.Gray,
                                    fontSize = 10.sp
                                )
                            }
                            Spacer(modifier = Modifier.height(8.dp))
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.spacedBy(6.dp)
                            ) {
                                pillGroup.entities.take(8).forEach { ent ->
                                    Surface(
                                        color = DarkSurfaceVariant,
                                        shape = RoundedCornerShape(6.dp)
                                    ) {
                                        Text(
                                            text = ent,
                                            color = Color.LightGray,
                                            fontSize = 11.sp,
                                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                                        )
                                    }
                                }
                            }
                        }
                    }
                }
            }
        } else if (selectedTab == "triplets") {
            // Relationships / Triplets Display
            val rels = semanticsData?.relationships ?: emptyList()
            if (rels.isEmpty()) {
                item {
                    Text("No knowledge triplets found for this video.", color = Color.Gray, fontSize = 12.sp)
                }
            } else {
                items(rels) { rel ->
                    Card(
                        colors = CardDefaults.cardColors(containerColor = DarkSurface),
                        shape = RoundedCornerShape(10.dp),
                        modifier = Modifier.fillMaxWidth().clickable {
                            if (rel.source_time.isNotBlank()) {
                                haptic.triggerClick()
                                activeTimestamp = rel.source_time
                            }
                        }
                    ) {
                        Row(
                            modifier = Modifier.padding(12.dp),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Column(modifier = Modifier.weight(1f)) {
                                Row(verticalAlignment = Alignment.CenterVertically) {
                                    Text(rel.subject, color = Color.White, fontSize = 12.sp, fontWeight = FontWeight.Bold)
                                    Spacer(modifier = Modifier.width(6.dp))
                                    Surface(
                                        color = VlkgPrimary.copy(alpha = 0.2f),
                                        shape = RoundedCornerShape(4.dp)
                                    ) {
                                        Text(
                                            text = rel.relation,
                                            color = VlkgPrimary,
                                            fontSize = 9.sp,
                                            fontWeight = FontWeight.Bold,
                                            modifier = Modifier.padding(horizontal = 4.dp, vertical = 2.dp)
                                        )
                                    }
                                    Spacer(modifier = Modifier.width(6.dp))
                                    Text(rel.`object`, color = Color.White, fontSize = 12.sp, fontWeight = FontWeight.Bold)
                                }
                                if (rel.intelligences.isNotEmpty()) {
                                    Spacer(modifier = Modifier.height(4.dp))
                                    Text(
                                        text = rel.intelligences.joinToString(", "),
                                        color = Color.Gray,
                                        fontSize = 10.sp
                                    )
                                }
                            }

                            if (rel.source_time.isNotBlank()) {
                                Surface(
                                    color = VlkgAccent.copy(alpha = 0.2f),
                                    shape = RoundedCornerShape(6.dp)
                                ) {
                                    Text(
                                        text = "[${rel.source_time}]",
                                        color = VlkgAccent,
                                        fontSize = 11.sp,
                                        fontWeight = FontWeight.Bold,
                                        modifier = Modifier.padding(horizontal = 6.dp, vertical = 3.dp)
                                    )
                                }
                            }
                        }
                    }
                }
            }
        } else {
            // Search Transcripts Field
            item {
                OutlinedTextField(
                    value = searchQuery,
                    onValueChange = { searchQuery = it },
                    label = { Text("Search video transcripts...", color = Color.Gray) },
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

        // Transcript Segments Timeline
        val filteredSegments = transcriptSegments.filter {
            searchQuery.isBlank() || it.text.contains(searchQuery, ignoreCase = true)
        }

        items(filteredSegments) { seg ->
            val isCurrent = seg.timestamp == activeTimestamp

            Card(
                colors = CardDefaults.cardColors(
                    containerColor = if (isCurrent) DarkSurfaceVariant else DarkSurface
                ),
                shape = RoundedCornerShape(10.dp),
                modifier = Modifier
                    .fillMaxWidth()
                    .clickable {
                        haptic.triggerClick()
                        activeTimestamp = seg.timestamp
                    }
            ) {
                Row(
                    modifier = Modifier.padding(12.dp),
                    verticalAlignment = Alignment.Top
                ) {
                    Surface(
                        color = if (isCurrent) VlkgPrimary else DarkSurfaceVariant,
                        shape = RoundedCornerShape(6.dp),
                        modifier = Modifier.padding(top = 2.dp)
                    ) {
                        Text(
                            text = seg.timestamp,
                            color = if (isCurrent) Color.White else Color.Gray,
                            fontSize = 11.sp,
                            fontWeight = FontWeight.Bold,
                            modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                        )
                    }

                    Spacer(modifier = Modifier.width(10.dp))

                    Text(
                        text = seg.text,
                        color = if (isCurrent) DarkOnBackground else Color.LightGray,
                        fontSize = 13.sp,
                        lineHeight = 18.sp,
                        modifier = Modifier.weight(1f)
                    )
                }
            }
        }
        }
    }
}