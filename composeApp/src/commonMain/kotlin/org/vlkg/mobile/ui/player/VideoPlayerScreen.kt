package org.vlkg.mobile.ui.player

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.vlkg.mobile.model.ChildApp
import org.vlkg.mobile.model.RawTriplet
import org.vlkg.mobile.model.SemanticPillGroup
import org.vlkg.mobile.model.TranscriptSegment
import org.vlkg.mobile.model.VideoMetadata
import org.vlkg.mobile.network.VlkgApiClient
import org.vlkg.mobile.platform.HapticFeedbackHelper
import org.vlkg.mobile.platform.PlatformUriLauncher
import org.vlkg.mobile.theme.*

@OptIn(ExperimentalLayoutApi::class)
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
    var selectedTab by remember { mutableStateOf("split") } // "split" | "relationships" | "transcript"
    var searchQuery by remember { mutableStateOf("") }
    var selectedEntityFilter by remember { mutableStateOf<String?>(null) }
    var showPillsSection by remember { mutableStateOf(true) }
    var isLoadingSemantics by remember { mutableStateOf(false) }

    LaunchedEffect(selectedVideo) {
        selectedVideo?.let { v ->
            isLoadingSemantics = true
            selectedEntityFilter = null
            transcriptSegments = apiClient.getVideoTranscript(v.video_id)
            semanticsData = apiClient.getVideoSemantics(v.video_id)
            isLoadingSemantics = false
        }
    }

    val extractedPills = semanticsData?.extracted_pills ?: emptyList()
    val enrichedPills = semanticsData?.enriched_pills ?: emptyList()
    val intelPills = semanticsData?.intel_pills ?: emptyList()
    val totalPillCategories = extractedPills.size + enrichedPills.size + intelPills.size

    val relationships = semanticsData?.relationships ?: emptyList()

    // Filtered relationships matching selectedEntityFilter and searchQuery
    val filteredRelationships = remember(relationships, selectedEntityFilter, searchQuery) {
        relationships.filter { r ->
            val matchesFilter = selectedEntityFilter?.let { filter ->
                val fl = filter.lowercase()
                r.subject.lowercase().contains(fl) || r.`object`.lowercase().contains(fl)
            } ?: true

            val matchesSearch = if (searchQuery.isNotBlank()) {
                val q = searchQuery.lowercase()
                r.subject.lowercase().contains(q) ||
                    r.`object`.lowercase().contains(q) ||
                    r.relation.lowercase().contains(q)
            } else true

            matchesFilter && matchesSearch
        }
    }

    // Filtered transcript segments matching selectedEntityFilter and searchQuery
    val filteredSegments = remember(transcriptSegments, selectedEntityFilter, searchQuery) {
        transcriptSegments.filter { seg ->
            val matchesFilter = selectedEntityFilter?.let { filter ->
                seg.text.contains(filter, ignoreCase = true)
            } ?: true

            val matchesSearch = if (searchQuery.isNotBlank()) {
                seg.text.contains(searchQuery, ignoreCase = true)
            } else true

            matchesFilter && matchesSearch
        }
    }

    val durationMin = remember(selectedVideo, transcriptSegments) {
        val durSec = selectedVideo?.duration_sec ?: 0
        if (durSec > 0) durSec / 60 else (transcriptSegments.size * 5) / 60
    }

    LazyColumn(
        modifier = modifier
            .fillMaxSize()
            .background(DarkBackground)
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(14.dp)
    ) {
        // ── 1. Video Carousel Switcher ──
        item {
            Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                Text(
                    text = "Videos in this App",
                    color = Color.Gray,
                    fontSize = 11.sp,
                    fontWeight = FontWeight.SemiBold
                )
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    appVideos.take(6).forEach { video ->
                        val isSelected = video.video_id == selectedVideo?.video_id
                        val isVoice = video.is_voice_recording || video.video_id.startsWith("voice_")

                        Surface(
                            onClick = {
                                haptic.triggerClick()
                                selectedVideo = video
                            },
                            shape = RoundedCornerShape(14.dp),
                            color = if (isSelected) VlkgPrimary else DarkSurface,
                            border = BorderStroke(
                                1.dp,
                                if (isSelected) VlkgPrimary.copy(alpha = 0.8f) else DarkOutline
                            ),
                            modifier = Modifier.height(34.dp)
                        ) {
                            Row(
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.spacedBy(6.dp),
                                modifier = Modifier.padding(horizontal = 10.dp)
                            ) {
                                Text(
                                    text = if (isVoice) "🎙️" else "🎬",
                                    fontSize = 11.sp
                                )
                                Text(
                                    text = video.title.take(16) + if (video.title.length > 16) "..." else "",
                                    color = if (isSelected) Color.White else Color.LightGray,
                                    fontSize = 11.sp,
                                    fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Medium
                                )
                            }
                        }
                    }
                }
            }
        }

        // ── 2. Main Video Semantics & Knowledge Header (like vlkg-mobile VideoPlayerView) ──
        item {
            Card(
                shape = RoundedCornerShape(20.dp),
                border = BorderStroke(1.dp, Color(0xFF1E293B)),
                colors = CardDefaults.cardColors(containerColor = Color.Transparent),
                modifier = Modifier.fillMaxWidth()
            ) {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .background(
                            brush = Brush.verticalGradient(
                                colors = listOf(
                                    Color(0xFF0F172A),
                                    Color(0xFF111827),
                                    Color(0xFF1E1B4B).copy(alpha = 0.4f)
                                )
                            )
                        )
                        .padding(16.dp)
                ) {
                    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                        // Top Meta Tag & Video ID
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Surface(
                                shape = RoundedCornerShape(50),
                                color = VlkgPrimary.copy(alpha = 0.15f),
                                border = BorderStroke(1.dp, VlkgPrimary.copy(alpha = 0.35f))
                            ) {
                                Row(
                                    verticalAlignment = Alignment.CenterVertically,
                                    horizontalArrangement = Arrangement.spacedBy(4.dp),
                                    modifier = Modifier.padding(horizontal = 8.dp, vertical = 3.dp)
                                ) {
                                    Text("⚡", fontSize = 10.sp)
                                    Text(
                                        "Recorded VLKG Knowledge & Transcript Semantics",
                                        color = Color(0xFFA5B4FC),
                                        fontSize = 10.sp,
                                        fontWeight = FontWeight.Bold
                                    )
                                }
                            }

                            Text(
                                text = "ID: ${selectedVideo?.video_id ?: ""}",
                                color = Color(0xFF64748B),
                                fontSize = 10.sp,
                                fontWeight = FontWeight.Medium
                            )
                        }

                        // Title
                        Text(
                            text = selectedVideo?.title ?: "Video Archive [${selectedVideo?.video_id}]",
                            color = Color.White,
                            fontSize = 17.sp,
                            fontWeight = FontWeight.Black,
                            lineHeight = 22.sp
                        )

                        // Channel, duration, and link
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(6.dp)
                        ) {
                            Text(
                                text = selectedVideo?.channel ?: "Leadership Series",
                                color = Color(0xFF94A3B8),
                                fontSize = 11.sp
                            )
                            Text("·", color = Color(0xFF64748B), fontSize = 11.sp)
                            Text(
                                text = if (durationMin > 0) "$durationMin mins duration" else "Ingested Recording",
                                color = Color(0xFF94A3B8),
                                fontSize = 11.sp
                            )
                            val videoUrl = selectedVideo?.url ?: ""
                            if (videoUrl.isNotBlank()) {
                                Text("·", color = Color(0xFF64748B), fontSize = 11.sp)
                                Text(
                                    text = "YouTube ↗",
                                    color = Color(0xFF818CF8),
                                    fontSize = 11.sp,
                                    fontWeight = FontWeight.SemiBold,
                                    modifier = Modifier.clickable {
                                        uriLauncher.openUri(videoUrl)
                                    }
                                )
                            }
                        }

                        // Quick Metrics Row (Relationships, Segments, Lenses)
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            MetricBox(
                                label = "Relationships",
                                value = "${relationships.size}",
                                valueColor = Color(0xFF818CF8),
                                modifier = Modifier.weight(1f)
                            )
                            MetricBox(
                                label = "Segments",
                                value = "${transcriptSegments.size}",
                                valueColor = Color(0xFFC084FC),
                                modifier = Modifier.weight(1f)
                            )
                            MetricBox(
                                label = "Lenses",
                                value = "${intelPills.size}",
                                valueColor = Color(0xFF34D399),
                                modifier = Modifier.weight(1f)
                            )
                        }

                        // Video Summary
                        selectedVideo?.summary?.takeIf { it.isNotBlank() }?.let { summary ->
                            Surface(
                                shape = RoundedCornerShape(12.dp),
                                color = Color(0xFF090D16).copy(alpha = 0.6f),
                                border = BorderStroke(1.dp, Color(0xFF1E293B)),
                                modifier = Modifier.fillMaxWidth()
                            ) {
                                Text(
                                    text = summary,
                                    color = Color(0xFFCBD5E1),
                                    fontSize = 11.sp,
                                    lineHeight = 16.sp,
                                    modifier = Modifier.padding(10.dp)
                                )
                            }
                        }

                        // ── Expandable Semantic Pills Interface ──
                        HorizontalDivider(color = Color(0xFF1E293B), thickness = 1.dp)

                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clickable { showPillsSection = !showPillsSection }
                                .padding(vertical = 4.dp),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Row(
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.spacedBy(6.dp)
                            ) {
                                Text("✨", fontSize = 12.sp)
                                Text(
                                    text = "Explore Recorded Entity & Intelligence Pills ($totalPillCategories Categories)",
                                    color = Color(0xFFE2E8F0),
                                    fontSize = 12.sp,
                                    fontWeight = FontWeight.Bold
                                )
                            }
                            Text(
                                text = if (showPillsSection) "▲" else "▼",
                                color = Color(0xFF94A3B8),
                                fontSize = 11.sp
                            )
                        }

                        if (showPillsSection) {
                            Column(
                                verticalArrangement = Arrangement.spacedBy(10.dp),
                                modifier = Modifier.fillMaxWidth().padding(top = 2.dp)
                            ) {
                                // 1. Extracted from Video
                                if (extractedPills.isNotEmpty()) {
                                    SemanticPillCategorySection(
                                        title = "Extracted from Video",
                                        titleColor = Color(0xFF94A3B8),
                                        groups = extractedPills,
                                        selectedFilter = selectedEntityFilter,
                                        onSelectFilter = { clicked ->
                                            haptic.triggerClick()
                                            selectedEntityFilter = if (selectedEntityFilter == clicked) null else clicked
                                        }
                                    )
                                }

                                // 2. Enriched Pathways
                                if (enrichedPills.isNotEmpty()) {
                                    SemanticPillCategorySection(
                                        title = "Enriched Pathways",
                                        titleColor = Color(0xFF94A3B8),
                                        groups = enrichedPills,
                                        selectedFilter = selectedEntityFilter,
                                        onSelectFilter = { clicked ->
                                            haptic.triggerClick()
                                            selectedEntityFilter = if (selectedEntityFilter == clicked) null else clicked
                                        }
                                    )
                                }

                                // 3. Intelligence Lenses
                                if (intelPills.isNotEmpty()) {
                                    SemanticPillCategorySection(
                                        title = "Intelligence Lenses",
                                        titleColor = Color(0xFFC084FC),
                                        groups = intelPills,
                                        isPurpleLens = true,
                                        selectedFilter = selectedEntityFilter,
                                        onSelectFilter = { clicked ->
                                            haptic.triggerClick()
                                            selectedEntityFilter = if (selectedEntityFilter == clicked) null else clicked
                                        }
                                    )
                                }
                            }
                        }

                        // YouTube Jump-to-Timestamp Button
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
                            shape = RoundedCornerShape(10.dp),
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Text("▶ Watch on YouTube at $activeTimestamp", fontSize = 12.sp, fontWeight = FontWeight.Bold)
                        }
                    }
                }
            }
        }


        // ── 3. Control Bar: View Mode Switcher, Filter Badge, and Search Bar ──
        item {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    // View Mode Switcher
                    Surface(
                        shape = RoundedCornerShape(14.dp),
                        color = Color(0xFF0F172A),
                        border = BorderStroke(1.dp, Color(0xFF1E293B)),
                        modifier = Modifier.padding(2.dp)
                    ) {
                        Row(modifier = Modifier.padding(3.dp), horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                            listOf(
                                "split" to "Split View",
                                "relationships" to "Relationships (${filteredRelationships.size})",
                                "transcript" to "Transcript (${filteredSegments.size})"
                            ).forEach { (mode, title) ->
                                val isSelected = selectedTab == mode
                                Surface(
                                    onClick = {
                                        haptic.triggerClick()
                                        selectedTab = mode
                                    },
                                    shape = RoundedCornerShape(10.dp),
                                    color = if (isSelected) VlkgPrimary else Color.Transparent
                                ) {
                                    Text(
                                        text = title,
                                        color = if (isSelected) Color.White else Color(0xFF94A3B8),
                                        fontSize = 11.sp,
                                        fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Medium,
                                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                                    )
                                }
                            }
                        }
                    }

                    // Active Entity Filter Pill
                    if (selectedEntityFilter != null) {
                        Surface(
                            onClick = { selectedEntityFilter = null },
                            shape = RoundedCornerShape(10.dp),
                            color = VlkgPrimary.copy(alpha = 0.2f),
                            border = BorderStroke(1.dp, VlkgPrimary.copy(alpha = 0.4f))
                        ) {
                            Row(
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.spacedBy(4.dp),
                                modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                            ) {
                                Text(
                                    text = "Filtered: ${selectedEntityFilter?.take(14)}",
                                    color = Color(0xFFA5B4FC),
                                    fontSize = 11.sp,
                                    fontWeight = FontWeight.Bold
                                )
                                Text("✕", color = Color.White, fontSize = 10.sp)
                            }
                        }
                    }
                }

                // Search Bar
                OutlinedTextField(
                    value = searchQuery,
                    onValueChange = { searchQuery = it },
                    placeholder = { Text("Search video transcripts and relationships...", color = Color.Gray, fontSize = 12.sp) },
                    singleLine = true,
                    shape = RoundedCornerShape(12.dp),
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedTextColor = DarkOnBackground,
                        unfocusedTextColor = DarkOnBackground,
                        focusedBorderColor = VlkgPrimary,
                        unfocusedBorderColor = DarkOutline,
                        focusedContainerColor = DarkSurface,
                        unfocusedContainerColor = DarkSurface
                    ),
                    modifier = Modifier.fillMaxWidth()
                )
            }
        }

        // ── 4. Main Content: Split View / Relationships / Transcript ──
        if (selectedTab == "split" || selectedTab == "relationships") {
            item {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "🕸️ Knowledge Triplets (${filteredRelationships.size})",
                        color = Color.White,
                        fontSize = 13.sp,
                        fontWeight = FontWeight.Bold
                    )
                    if (filteredRelationships.size > 8 && selectedTab == "split") {
                        Text(
                            text = "Showing top 8",
                            color = Color.Gray,
                            fontSize = 11.sp
                        )
                    }
                }
            }

            val tripletsToShow = if (selectedTab == "split") filteredRelationships.take(8) else filteredRelationships
            if (tripletsToShow.isEmpty()) {
                item {
                    Text(
                        text = "No relationships match the selected filter.",
                        color = Color.Gray,
                        fontSize = 12.sp,
                        modifier = Modifier.padding(vertical = 4.dp)
                    )
                }
            } else {
                items(tripletsToShow) { rel ->
                    TripletCard(
                        rel = rel,
                        onTimeClick = { time ->
                            haptic.triggerClick()
                            activeTimestamp = time
                        }
                    )
                }
            }
        }

        if (selectedTab == "split" || selectedTab == "transcript") {
            item {
                Spacer(modifier = Modifier.height(6.dp))
                Text(
                    text = "📜 Transcript Timeline (${filteredSegments.size} segments)",
                    color = Color.White,
                    fontSize = 13.sp,
                    fontWeight = FontWeight.Bold
                )
            }

            if (filteredSegments.isEmpty()) {
                item {
                    Text(
                        text = "No transcript segments match the query.",
                        color = Color.Gray,
                        fontSize = 12.sp,
                        modifier = Modifier.padding(vertical = 4.dp)
                    )
                }
            } else {
                items(filteredSegments) { seg ->
                    val isCurrent = seg.timestamp == activeTimestamp

                    Card(
                        colors = CardDefaults.cardColors(
                            containerColor = if (isCurrent) Color(0xFF1E293B) else DarkSurface
                        ),
                        shape = RoundedCornerShape(10.dp),
                        border = if (isCurrent) BorderStroke(1.dp, VlkgPrimary) else null,
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
}

@Composable
private fun MetricBox(
    label: String,
    value: String,
    valueColor: Color,
    modifier: Modifier = Modifier
) {
    Surface(
        shape = RoundedCornerShape(14.dp),
        color = Color(0xFF090D16).copy(alpha = 0.7f),
        border = BorderStroke(1.dp, Color(0xFF1E293B)),
        modifier = modifier
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            modifier = Modifier.padding(vertical = 8.dp)
        ) {
            Text(
                text = value,
                color = valueColor,
                fontSize = 15.sp,
                fontWeight = FontWeight.Black
            )
            Text(
                text = label,
                color = Color(0xFF94A3B8),
                fontSize = 10.sp,
                fontWeight = FontWeight.Medium
            )
        }
    }
}

@OptIn(ExperimentalLayoutApi::class)
@Composable
private fun SemanticPillCategorySection(
    title: String,
    titleColor: Color,
    groups: List<SemanticPillGroup>,
    isPurpleLens: Boolean = false,
    selectedFilter: String?,
    onSelectFilter: (String) -> Unit
) {
    Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
        Text(
            text = title.uppercase(),
            color = titleColor,
            fontSize = 10.sp,
            fontWeight = FontWeight.Bold,
            letterSpacing = 0.8.sp
        )

        FlowRow(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(6.dp),
            verticalArrangement = Arrangement.spacedBy(6.dp)
        ) {
            groups.forEach { group ->
                val baseColor = if (isPurpleLens) Color(0xFFA855F7) else parseHexColor(group.color, VlkgPrimary)

                group.entities.take(15).forEach { name ->
                    val isSelected = selectedFilter == name
                    val bgTint = if (isSelected) baseColor else baseColor.copy(alpha = 0.15f)
                    val borderColor = if (isSelected) Color.White else baseColor.copy(alpha = 0.5f)
                    val textColor = if (isSelected) Color.White else Color(0xFFE2E8F0)

                    Surface(
                        onClick = { onSelectFilter(name) },
                        shape = CircleShape,
                        color = bgTint,
                        border = BorderStroke(
                            width = if (isSelected) 2.dp else 1.dp,
                            color = borderColor
                        )
                    ) {
                        Text(
                            text = name,
                            color = textColor,
                            fontSize = 11.sp,
                            fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Medium,
                            modifier = Modifier.padding(horizontal = 9.dp, vertical = 3.dp)
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun TripletCard(
    rel: RawTriplet,
    onTimeClick: (String) -> Unit
) {
    Card(
        colors = CardDefaults.cardColors(containerColor = DarkSurface),
        shape = RoundedCornerShape(10.dp),
        border = BorderStroke(1.dp, Color(0xFF1E293B)),
        modifier = Modifier.fillMaxWidth()
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
                    onClick = { onTimeClick(rel.source_time) },
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