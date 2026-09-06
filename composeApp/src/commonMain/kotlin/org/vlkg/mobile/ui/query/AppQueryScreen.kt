package org.vlkg.mobile.ui.query

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.vlkg.mobile.model.ChildApp
import org.vlkg.mobile.platform.HapticFeedbackHelper
import org.vlkg.mobile.theme.*
import org.vlkg.mobile.viewmodel.QueryViewModel

@Composable
fun AppQueryScreen(
    activeApp: ChildApp?,
    apps: List<ChildApp> = emptyList(),
    selectedLens: String,
    onJumpToVideo: (videoId: String, timestamp: String) -> Unit,
    queryViewModel: QueryViewModel = remember { QueryViewModel() },
    modifier: Modifier = Modifier
) {
    val queryState by queryViewModel.uiState.collectAsState()
    val haptic = remember { HapticFeedbackHelper() }

    LaunchedEffect(apps) {
        if (queryState.selectedAppIds.isEmpty() && apps.isNotEmpty()) {
            apps.take(2).forEach { queryViewModel.toggleAppSelection(it.id) }
        }
    }

    val suggestedQuestions = listOf(
        "How do leaders set boundaries and protect high-leverage time?",
        "What are the core engineering workflows using AI?",
        "What is the foundational discipline required to scale execution?",
        "Explain First-Principles Thinking in leadership."
    )

    Column(
        modifier = modifier
            .fillMaxSize()
            .background(DarkBackground)
            .padding(16.dp)
    ) {
        // Query Mode Toggle (Single App vs Multi-App "Twice Answered")
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.Center
        ) {
            Surface(
                color = DarkSurface,
                shape = RoundedCornerShape(8.dp),
                border = androidx.compose.foundation.BorderStroke(1.dp, DarkOutline)
            ) {
                Row(modifier = Modifier.padding(4.dp)) {
                    FilterChip(
                        selected = queryState.queryMode == "single",
                        onClick = { queryViewModel.setQueryMode("single") },
                        label = { Text("SINGLE: ${activeApp?.name?.take(10)?.uppercase() ?: "ACTIVE"}...", fontFamily = FontFamily.Monospace, fontSize = 10.sp, fontWeight = FontWeight.Bold) },
                        colors = FilterChipDefaults.filterChipColors(
                            selectedContainerColor = VlkgPrimary,
                            selectedLabelColor = Color.White
                        )
                    )
                    Spacer(modifier = Modifier.width(6.dp))
                    FilterChip(
                        selected = queryState.queryMode == "multi",
                        onClick = { queryViewModel.setQueryMode("multi") },
                        label = { Text("COMPARE WORKSPACES", fontFamily = FontFamily.Monospace, fontSize = 10.sp, fontWeight = FontWeight.Bold) },
                        colors = FilterChipDefaults.filterChipColors(
                            selectedContainerColor = VlkgAccent,
                            selectedLabelColor = Color.Black
                        )
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(8.dp))

        if (queryState.queryMode == "multi") {
            // App Selector Chips for Multi-App comparison
            Text("Select Workspaces to Compare:", color = Color(0xFF64748B), fontFamily = FontFamily.Monospace, fontSize = 10.sp, fontWeight = FontWeight.Bold)
            Spacer(modifier = Modifier.height(4.dp))
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(6.dp)
            ) {
                apps.forEach { app ->
                    val isChecked = queryState.selectedAppIds.contains(app.id)
                    FilterChip(
                        selected = isChecked,
                        onClick = {
                            haptic.triggerClick()
                            queryViewModel.toggleAppSelection(app.id)
                        },
                        label = { Text(app.name.take(14) + "...", fontFamily = FontFamily.Monospace, fontSize = 10.sp) },
                        colors = FilterChipDefaults.filterChipColors(
                            selectedContainerColor = VlkgSecondary,
                            selectedLabelColor = Color.White,
                            containerColor = DarkSurfaceVariant,
                            labelColor = Color.LightGray
                        )
                    )
                }
            }
        } else {
            // Single App Context Header
            Surface(
                color = DarkSurface,
                shape = RoundedCornerShape(8.dp),
                border = androidx.compose.foundation.BorderStroke(1.dp, DarkOutline),
                modifier = Modifier.fillMaxWidth()
            ) {
                Row(
                    modifier = Modifier.padding(horizontal = 12.dp, vertical = 8.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Box(
                        modifier = Modifier
                            .size(6.dp)
                            .background(VlkgPrimary, RoundedCornerShape(2.dp))
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Column {
                        Text(
                            text = "SCOPE: ${activeApp?.name?.uppercase() ?: "ALL KNOWLEDGE"}",
                            color = DarkOnBackground,
                            fontFamily = FontFamily.Monospace,
                            fontSize = 11.sp,
                            fontWeight = FontWeight.Bold
                        )
                        Text(
                            text = "${activeApp?.video_ids?.size ?: 0} STREAMS / LENS: ${selectedLens.uppercase()}",
                            color = Color(0xFF64748B),
                            fontFamily = FontFamily.Monospace,
                            fontSize = 9.sp
                        )
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(10.dp))

        // Suggested Questions - ONE QUESTION PER ROW
        Text(
            text = "SUGGESTED QUESTIONS",
            color = Color(0xFF64748B),
            fontFamily = FontFamily.Monospace,
            fontSize = 9.sp,
            fontWeight = FontWeight.Bold,
            letterSpacing = 0.5.sp
        )
        Spacer(modifier = Modifier.height(4.dp))
        Column(
            modifier = Modifier.fillMaxWidth(),
            verticalArrangement = Arrangement.spacedBy(5.dp)
        ) {
            suggestedQuestions.forEach { q ->
                Surface(
                    onClick = {
                        haptic.triggerClick()
                        queryViewModel.askQuestion(activeApp?.id ?: "app_executive", q, selectedLens)
                    },
                    shape = RoundedCornerShape(6.dp),
                    color = DarkSurface,
                    border = androidx.compose.foundation.BorderStroke(1.dp, DarkOutline),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(horizontal = 12.dp, vertical = 8.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = q,
                            color = Color(0xFFCBD5E1),
                            fontFamily = FontFamily.Monospace,
                            fontSize = 10.sp,
                            maxLines = 1,
                            overflow = TextOverflow.Ellipsis,
                            modifier = Modifier.weight(1f)
                        )
                        Text(
                            text = "[->]",
                            color = VlkgPrimary,
                            fontFamily = FontFamily.Monospace,
                            fontSize = 9.sp,
                            fontWeight = FontWeight.Bold,
                            modifier = Modifier.padding(start = 8.dp)
                        )
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(10.dp))

        // Message History
        LazyColumn(
            modifier = Modifier.weight(1f),
            verticalArrangement = Arrangement.spacedBy(14.dp)
        ) {
            items(queryState.messages) { msg ->
                val isUser = msg.sender == "user"

                Column(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalAlignment = if (isUser) Alignment.End else Alignment.Start
                ) {
                    Surface(
                        color = if (isUser) VlkgPrimary else DarkSurface,
                        shape = RoundedCornerShape(16.dp),
                        modifier = Modifier.widthIn(max = 320.dp)
                    ) {
                        Column(modifier = Modifier.padding(14.dp)) {
                            if (!isUser) {
                                Row(
                                    verticalAlignment = Alignment.CenterVertically, 
                                    modifier = Modifier.padding(bottom = 10.dp)
                                ) {
                                    Text("✨", fontSize = 14.sp)
                                    Spacer(modifier = Modifier.width(6.dp))
                                    Text(
                                        text = "Synthesized Intelligence", 
                                        color = VlkgAccent, 
                                        fontSize = 11.sp, 
                                        fontWeight = FontWeight.Bold
                                    )
                                }
                            }
                            Text(
                                text = msg.text,
                                color = DarkOnBackground,
                                fontSize = 14.sp,
                                lineHeight = 20.sp
                            )

                            // Cited Triplets & Groundings
                            msg.result?.let { res ->
                                if (res.triplets.isNotEmpty()) {
                                    Spacer(modifier = Modifier.height(12.dp))
                                    Text(
                                        text = "📌 Cited Video Triplet Evidence:",
                                        color = VlkgSecondary,
                                        fontSize = 11.sp,
                                        fontWeight = FontWeight.Bold
                                    )
                                    Spacer(modifier = Modifier.height(6.dp))

                                    res.triplets.forEach { triplet ->
                                        Surface(
                                            color = DarkSurfaceVariant,
                                            shape = RoundedCornerShape(8.dp),
                                            modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp)
                                        ) {
                                            Column(modifier = Modifier.padding(8.dp)) {
                                                @OptIn(androidx.compose.foundation.layout.ExperimentalLayoutApi::class)
                                                androidx.compose.foundation.layout.FlowRow(
                                                    verticalArrangement = Arrangement.Center
                                                ) {
                                                    Text(
                                                        text = triplet.subject,
                                                        color = DarkOnBackground,
                                                        fontWeight = FontWeight.Bold,
                                                        fontSize = 11.sp,
                                                        modifier = Modifier.align(Alignment.CenterVertically)
                                                    )
                                                    Text(
                                                        text = " —[${triplet.predicate}]→ ",
                                                        color = VlkgAccent,
                                                        fontSize = 10.sp,
                                                        fontWeight = FontWeight.SemiBold,
                                                        modifier = Modifier.align(Alignment.CenterVertically)
                                                    )
                                                    Text(
                                                        text = triplet.`object`,
                                                        color = VlkgTertiary,
                                                        fontWeight = FontWeight.Bold,
                                                        fontSize = 11.sp,
                                                        modifier = Modifier.align(Alignment.CenterVertically)
                                                    )
                                                }
                                                Spacer(modifier = Modifier.height(4.dp))
                                                Text(
                                                    text = "\"${triplet.transcriptSnippet}\"",
                                                    color = Color.LightGray,
                                                    fontSize = 11.sp,
                                                    fontStyle = androidx.compose.ui.text.font.FontStyle.Italic
                                                )
                                                Spacer(modifier = Modifier.height(6.dp))
                                                Button(
                                                    onClick = {
                                                        haptic.triggerClick()
                                                        onJumpToVideo(triplet.videoId, triplet.timestampFormatted)
                                                    },
                                                    colors = ButtonDefaults.buttonColors(containerColor = VlkgPrimary),
                                                    contentPadding = PaddingValues(horizontal = 8.dp, vertical = 2.dp),
                                                    shape = RoundedCornerShape(6.dp)
                                                ) {
                                                    Text("▶ Jump to ${triplet.timestampFormatted}", fontSize = 10.sp)
                                                }
                                            }
                                        }
                                    }
                                }
                            }

                            // Multi-App Comparison Results
                            msg.multiResult?.let { multi ->
                                if (multi.app_comparisons.isNotEmpty()) {
                                    Spacer(modifier = Modifier.height(10.dp))
                                    Text(
                                        text = "⚖️ App Comparison Breakdown:",
                                        color = VlkgAccent,
                                        fontSize = 11.sp,
                                        fontWeight = FontWeight.Bold
                                    )
                                    Spacer(modifier = Modifier.height(6.dp))

                                    multi.app_comparisons.forEach { comp ->
                                        Surface(
                                            color = DarkSurfaceVariant,
                                            shape = RoundedCornerShape(8.dp),
                                            modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp)
                                        ) {
                                            Column(modifier = Modifier.padding(10.dp)) {
                                                Text(
                                                    text = comp.app_name.ifBlank { comp.app_id },
                                                    color = Color.White,
                                                    fontSize = 11.sp,
                                                    fontWeight = FontWeight.Bold
                                                )
                                                Spacer(modifier = Modifier.height(4.dp))
                                                Text(
                                                    text = comp.answer,
                                                    color = Color.LightGray,
                                                    fontSize = 11.sp,
                                                    lineHeight = 15.sp
                                                )
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }

            if (queryState.isLoading) {
                item {
                    Row(
                        modifier = Modifier.padding(8.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        CircularProgressIndicator(modifier = Modifier.size(16.dp), color = VlkgPrimary, strokeWidth = 2.dp)
                        Spacer(modifier = Modifier.width(8.dp))
                        Text("Reasoning over knowledge graph...", color = Color.Gray, fontSize = 12.sp)
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(10.dp))

        // Input Bar
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            OutlinedTextField(
                value = queryState.currentQuestion,
                onValueChange = { queryViewModel.updateQuestion(it) },
                placeholder = { Text("Ask anything about this child app...", color = Color.Gray, fontSize = 13.sp) },
                colors = OutlinedTextFieldDefaults.colors(
                    focusedTextColor = DarkOnBackground,
                    unfocusedTextColor = DarkOnBackground,
                    focusedBorderColor = VlkgPrimary,
                    unfocusedBorderColor = DarkOutline
                ),
                shape = RoundedCornerShape(14.dp),
                modifier = Modifier.weight(1f)
            )

            Button(
                onClick = {
                    haptic.triggerClick()
                    if (queryState.queryMode == "multi") {
                        val ids = if (queryState.selectedAppIds.isNotEmpty()) queryState.selectedAppIds else apps.take(2).map { it.id }
                        queryViewModel.askMultiAppQuestion(ids, queryState.currentQuestion)
                    } else {
                        queryViewModel.askQuestion(
                            activeApp?.id ?: "app_executive",
                            queryState.currentQuestion,
                            selectedLens
                        )
                    }
                },
                enabled = queryState.currentQuestion.isNotBlank() && !queryState.isLoading,
                colors = ButtonDefaults.buttonColors(containerColor = if (queryState.queryMode == "multi") VlkgAccent else VlkgPrimary),
                shape = RoundedCornerShape(14.dp),
                contentPadding = PaddingValues(horizontal = 16.dp, vertical = 14.dp)
            ) {
                Text(if (queryState.queryMode == "multi") "Compare" else "Ask", color = if (queryState.queryMode == "multi") Color.Black else Color.White, fontWeight = FontWeight.Bold)
            }
        }
    }
}