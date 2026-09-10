package org.vlkg.mobile.ui.query

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
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

private val CURATED_QUERY_QUESTIONS = listOf(
    "How do recursive feedback loops accelerate executive learning curves?",
    "What heuristics distinguish high-agency operators from conventional managers?",
    "How can asynchronous knowledge triplets minimize meeting overhead?",
    "What are the critical inflection points when scaling an AI workflow from 1 to 10?",
    "How do leaders navigate asymmetric risk during high-stakes strategic negotiations?",
    "What telemetry metrics best indicate authentic audience resonance in presentations?",
    "How does radical candor prevent organizational debt in fast-moving teams?",
    "What mental models help executives de-risk aggressive product roadmap bets?",
    "How do top engineers leverage declarative knowledge graphs in real-time?",
    "What are the non-obvious trade-offs between execution speed and architectural purity?",
    "How can teams build antifragile systems that benefit from market volatility?",
    "How do first principles simplify complex multi-agent system design?",
    "What role does emotional regulation play during high-velocity crisis response?"
)

private fun generateNewComposeQuestion(
    answeredQuestion: String,
    usedQuestions: Set<String>,
    activeApp: ChildApp?
): String {
    if (activeApp != null && activeApp.prioritized_entities.isNotEmpty()) {
        val ent = activeApp.prioritized_entities.randomOrNull()
        if (ent != null) {
            val templates = listOf(
                "How does $ent directly drive execution velocity in this workspace?",
                "What are the core operational principles behind $ent?",
                "How can teams leverage $ent to de-risk high-stakes decisions?",
                "Where does $ent intersect with long-term strategy?"
            )
            for (t in templates) {
                if (!usedQuestions.contains(t) && t != answeredQuestion) {
                    return t
                }
            }
        }
    }
    
    val available = CURATED_QUERY_QUESTIONS.filter { !usedQuestions.contains(it) && it != answeredQuestion }
    if (available.isNotEmpty()) {
        return available.random()
    }
    return "How can teams apply dynamic knowledge graphs to accelerate strategic execution?"
}

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
    val primaryColor = MaterialTheme.colorScheme.primary
    val appTheme = LocalVlkgAppTheme.current

    LaunchedEffect(apps) {
        if (queryState.selectedAppIds.isEmpty() && apps.isNotEmpty()) {
            apps.take(2).forEach { queryViewModel.toggleAppSelection(it.id) }
        }
    }

    val initialQuestions = remember {
        listOf(
            "How do leaders set boundaries and protect high-leverage time?",
            "What are the core engineering workflows using AI?",
            "What is the foundational discipline required to scale execution?",
            "Explain First-Principles Thinking in leadership."
        )
    }
    var visibleQuestions by remember { mutableStateOf(initialQuestions) }
    var usedQuestions by remember { mutableStateOf(initialQuestions.toSet()) }

    Column(
        modifier = modifier
            .fillMaxSize()
            .background(DarkBackground)
            .padding(horizontal = 14.dp, vertical = 10.dp)
    ) {
        // Mode Selector: Single App vs Multi App
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.Center
        ) {
            Surface(
                color = DarkSurface,
                shape = RoundedCornerShape(8.dp),
                border = androidx.compose.foundation.BorderStroke(1.dp, DarkOutline)
            ) {
                Row(modifier = Modifier.padding(2.dp)) {
                    FilterChip(
                        selected = queryState.queryMode == "single",
                        onClick = {
                            haptic.triggerClick()
                            queryViewModel.setQueryMode("single")
                        },
                        label = { Text("SINGLE APP", fontFamily = FontFamily.Monospace, fontSize = 11.sp, fontWeight = FontWeight.Bold) },
                        colors = FilterChipDefaults.filterChipColors(
                            selectedContainerColor = primaryColor,
                            selectedLabelColor = Color.Black
                        )
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    FilterChip(
                        selected = queryState.queryMode == "multi",
                        onClick = {
                            haptic.triggerClick()
                            queryViewModel.setQueryMode("multi")
                        },
                        label = { Text("COMPARE APPS", fontFamily = FontFamily.Monospace, fontSize = 11.sp, fontWeight = FontWeight.Bold) },
                        colors = FilterChipDefaults.filterChipColors(
                            selectedContainerColor = primaryColor,
                            selectedLabelColor = Color.Black
                        )
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(8.dp))

        if (queryState.queryMode == "multi") {
            // App Selector List: Strictly One Workspace per Row
            Text(
                text = "SELECT WORKSPACES TO COMPARE (ONE WORKSPACE PER ROW):", 
                color = primaryColor, 
                fontFamily = FontFamily.Monospace, 
                fontSize = 10.sp, 
                fontWeight = FontWeight.Bold
            )
            Spacer(modifier = Modifier.height(4.dp))
            Column(
                modifier = Modifier.fillMaxWidth(),
                verticalArrangement = Arrangement.spacedBy(6.dp)
            ) {
                apps.forEach { app ->
                    val isChecked = queryState.selectedAppIds.contains(app.id)
                    Surface(
                        onClick = {
                            haptic.triggerClick()
                            queryViewModel.toggleAppSelection(app.id)
                        },
                        shape = RoundedCornerShape(8.dp),
                        color = if (isChecked) primaryColor.copy(alpha = 0.12f) else DarkSurface,
                        border = androidx.compose.foundation.BorderStroke(
                            1.dp,
                            if (isChecked) primaryColor.copy(alpha = 0.6f) else DarkOutline
                        ),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(horizontal = 10.dp, vertical = 7.dp),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Row(
                                verticalAlignment = Alignment.CenterVertically,
                                modifier = Modifier.weight(1f)
                            ) {
                                Box(
                                    modifier = Modifier
                                        .size(8.dp)
                                        .background(if (isChecked) primaryColor else Color(0xFF475569), CircleShape)
                                )
                                Spacer(modifier = Modifier.width(8.dp))
                                Column {
                                    Row(verticalAlignment = Alignment.CenterVertically) {
                                        Text(
                                            text = app.name,
                                            fontFamily = FontFamily.Monospace,
                                            fontSize = 12.sp,
                                            fontWeight = if (isChecked) FontWeight.Bold else FontWeight.Medium,
                                            color = if (isChecked) DarkOnBackground else Color(0xFFCBD5E1)
                                        )
                                        Spacer(modifier = Modifier.width(6.dp))
                                        Text(
                                            text = "DOMAIN IN A BOX",
                                            fontFamily = FontFamily.Monospace,
                                            fontSize = 8.sp,
                                            color = Color(0xFF64748B)
                                        )
                                    }
                                    Text(
                                        text = "${app.video_ids.size} streams · ${app.prioritized_entities.size} priority entities",
                                        fontFamily = FontFamily.Monospace,
                                        fontSize = 9.sp,
                                        color = Color(0xFF94A3B8)
                                    )
                                }
                            }
                            Checkbox(
                                checked = isChecked,
                                onCheckedChange = {
                                    haptic.triggerClick()
                                    queryViewModel.toggleAppSelection(app.id)
                                },
                                colors = CheckboxDefaults.colors(
                                    checkedColor = primaryColor,
                                    checkmarkColor = Color.Black
                                )
                            )
                        }
                    }
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
                            .background(primaryColor, RoundedCornerShape(2.dp))
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
            visibleQuestions.forEach { q ->
                Surface(
                    onClick = {
                        haptic.triggerClick()
                        queryViewModel.askQuestion(activeApp?.id ?: "app_executive", q, selectedLens)

                        // 1. Remove answered question from panel & generate replacement question
                        val remaining = visibleQuestions.filter { it != q }
                        val newQ = generateNewComposeQuestion(q, usedQuestions, activeApp)
                        usedQuestions = usedQuestions + q + newQ
                        visibleQuestions = remaining + newQ
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
                            color = primaryColor,
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
                                                    colors = ButtonDefaults.buttonColors(containerColor = primaryColor),
                                                    contentPadding = PaddingValues(horizontal = 8.dp, vertical = 2.dp),
                                                    shape = RoundedCornerShape(6.dp)
                                                ) {
                                                    Text("JUMP TO ${triplet.timestampFormatted} [->]", fontSize = 10.sp, fontFamily = FontFamily.Monospace, fontWeight = FontWeight.Bold)
                                                }
                                            }
                                        }
                                    }
                                }
                            }

                            // Multi-App Comparison Results (Strictly One Workspace Per Row)
                            msg.multiResult?.let { multi ->
                                if (multi.app_comparisons.isNotEmpty()) {
                                    Spacer(modifier = Modifier.height(10.dp))
                                    Text(
                                        text = "DOMAIN COMPARISON BREAKDOWN (ONE PER ROW):",
                                        color = VlkgAccent,
                                        fontSize = 10.sp,
                                        fontFamily = FontFamily.Monospace,
                                        fontWeight = FontWeight.Bold,
                                        letterSpacing = 0.5.sp
                                    )
                                    Spacer(modifier = Modifier.height(6.dp))

                                    multi.app_comparisons.forEach { comp ->
                                        Surface(
                                            color = DarkSurfaceVariant,
                                            shape = RoundedCornerShape(8.dp),
                                            border = androidx.compose.foundation.BorderStroke(1.dp, DarkOutline),
                                            modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp)
                                        ) {
                                            Column(modifier = Modifier.padding(10.dp)) {
                                                Row(
                                                    modifier = Modifier.fillMaxWidth(),
                                                    horizontalArrangement = Arrangement.SpaceBetween,
                                                    verticalAlignment = Alignment.CenterVertically
                                                ) {
                                                    Text(
                                                        text = comp.app_name.ifBlank { comp.app_id }.uppercase(),
                                                        color = Color.White,
                                                        fontFamily = FontFamily.Monospace,
                                                        fontSize = 11.sp,
                                                        fontWeight = FontWeight.Bold
                                                    )
                                                    Surface(
                                                        color = primaryColor.copy(alpha = 0.15f),
                                                        shape = RoundedCornerShape(4.dp),
                                                        border = androidx.compose.foundation.BorderStroke(1.dp, primaryColor.copy(alpha = 0.4f))
                                                    ) {
                                                        Text(
                                                            text = "DOMAIN IN A BOX",
                                                            color = primaryColor,
                                                            fontFamily = FontFamily.Monospace,
                                                            fontSize = 8.sp,
                                                            fontWeight = FontWeight.Bold,
                                                            modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                                                        )
                                                    }
                                                }
                                                Spacer(modifier = Modifier.height(6.dp))
                                                Text(
                                                    text = comp.answer,
                                                    color = Color.LightGray,
                                                    fontSize = 11.sp,
                                                    lineHeight = 16.sp
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
                        CircularProgressIndicator(modifier = Modifier.size(16.dp), color = primaryColor, strokeWidth = 2.dp)
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
                    focusedBorderColor = primaryColor,
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
                colors = ButtonDefaults.buttonColors(containerColor = if (queryState.queryMode == "multi") VlkgAccent else primaryColor),
                shape = RoundedCornerShape(14.dp),
                contentPadding = PaddingValues(horizontal = 16.dp, vertical = 14.dp)
            ) {
                Text(if (queryState.queryMode == "multi") "Compare" else "Ask", color = if (queryState.queryMode == "multi") Color.Black else Color.White, fontWeight = FontWeight.Bold)
            }
        }
    }
}