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
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.vlkg.mobile.model.ChildApp
import org.vlkg.mobile.platform.HapticFeedbackHelper
import org.vlkg.mobile.theme.*
import org.vlkg.mobile.viewmodel.QueryViewModel

@Composable
fun AppQueryScreen(
    activeApp: ChildApp?,
    selectedLens: String,
    onJumpToVideo: (videoId: String, timestamp: String) -> Unit,
    queryViewModel: QueryViewModel = remember { QueryViewModel() },
    modifier: Modifier = Modifier
) {
    val queryState by queryViewModel.uiState.collectAsState()
    val haptic = remember { HapticFeedbackHelper() }

    val suggestedQuestions = listOf(
        "What are the core leadership habits?",
        "Explain First-Principles Thinking in AI.",
        "How do high-agency teams handle feedback?",
        "What is the role of psychological safety?"
    )

    Column(
        modifier = modifier
            .fillMaxSize()
            .background(DarkBackground)
            .padding(16.dp)
    ) {
        // App Context Header
        Surface(
            color = DarkSurface,
            shape = RoundedCornerShape(12.dp),
            modifier = Modifier.fillMaxWidth()
        ) {
            Row(
                modifier = Modifier.padding(horizontal = 14.dp, vertical = 10.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(text = "✨", fontSize = 16.sp)
                Spacer(modifier = Modifier.width(8.dp))
                Column {
                    Text(
                        text = "Querying: ${activeApp?.name ?: "All Knowledge"}",
                        color = DarkOnBackground,
                        fontSize = 13.sp,
                        fontWeight = FontWeight.Bold
                    )
                    Text(
                        text = "Grounded in ${activeApp?.video_ids?.size ?: 0} videos • Lens: ${selectedLens.uppercase()}",
                        color = Color.Gray,
                        fontSize = 10.sp
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(10.dp))

        // Suggested Questions Row
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(6.dp)
        ) {
            suggestedQuestions.take(2).forEach { q ->
                AssistChip(
                    onClick = {
                        haptic.triggerClick()
                        queryViewModel.askQuestion(activeApp?.id ?: "app_executive", q, selectedLens)
                    },
                    label = { Text(q, fontSize = 10.sp) },
                    colors = AssistChipDefaults.assistChipColors(
                        containerColor = DarkSurfaceVariant,
                        labelColor = Color.LightGray
                    )
                )
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
                                                Text(
                                                    text = "${triplet.subject} —[${triplet.predicate}]→ ${triplet.`object`}",
                                                    color = VlkgAccent,
                                                    fontSize = 11.sp,
                                                    fontWeight = FontWeight.Bold
                                                )
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
                    queryViewModel.askQuestion(
                        activeApp?.id ?: "app_executive",
                        queryState.currentQuestion,
                        selectedLens
                    )
                },
                enabled = queryState.currentQuestion.isNotBlank() && !queryState.isLoading,
                colors = ButtonDefaults.buttonColors(containerColor = VlkgPrimary),
                shape = RoundedCornerShape(14.dp),
                contentPadding = PaddingValues(horizontal = 16.dp, vertical = 14.dp)
            ) {
                Text("Ask", fontWeight = FontWeight.Bold)
            }
        }
    }
}