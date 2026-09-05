package org.vlkg.mobile.ui.words

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.itemsIndexed
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
import org.vlkg.mobile.model.ConceptCategory
import org.vlkg.mobile.model.ConceptNode
import org.vlkg.mobile.platform.HapticFeedbackHelper
import org.vlkg.mobile.theme.*

@Composable
fun LinearWordsScreen(
    activeApp: ChildApp?,
    viewMode: String, // "ladder" | "pathways" | "categories"
    onSetViewMode: (String) -> Unit,
    selectedLens: String,
    onSelectLens: (String) -> Unit,
    onTogglePriority: (String) -> Unit,
    onJumpToVideo: (videoId: String, timestamp: String) -> Unit,
    entities: List<ConceptNode> = emptyList(),
    modifier: Modifier = Modifier
) {
    val haptic = remember { HapticFeedbackHelper() }
    var searchQuery by remember { mutableStateOf("") }

    val lenses = listOf(
        "all" to "All Words",
        "executive" to "Executive",
        "sales" to "Sales & Revenue",
        "learning" to "Learning & Mastery",
        "engineering" to "R&D / AI Tools",
        "compliance" to "Governance",
        "thought_leadership" to "Leadership"
    )

    // Master list of concepts: use real entities loaded from repository or fallback to base defaults
    val baseNodes = remember(entities, activeApp) {
        if (entities.isNotEmpty()) {
            entities
        } else {
            listOf(
                ConceptNode("1", "First-Principles Thinking", ConceptCategory.DECISION_MAKING, 0.95, "Boiling problems down to fundamentals.", 4, listOf("Mental Models", "Strategy")),
                ConceptNode("2", "Transformational Leadership", ConceptCategory.CORE_LEADERSHIP, 0.90, "Inspiring teams to achieve extraordinary outcomes.", 6, listOf("Inspiration", "Vision")),
                ConceptNode("3", "Autonomous AI Agents", ConceptCategory.AI_INNOVATION, 0.88, "Self-directed AI architectures with planning.", 5, listOf("Automation", "Agentic")),
                ConceptNode("4", "Radical Candor", ConceptCategory.COMMUNICATION, 0.78, "Caring personally while challenging directly.", 3, listOf("Feedback", "Trust")),
                ConceptNode("5", "Systems Dynamics", ConceptCategory.SYSTEMS_THINKING, 0.85, "Understanding non-linear causal loops.", 4, listOf("Causal Loops", "Leverage")),
                ConceptNode("6", "High-Output Execution", ConceptCategory.EXECUTION, 0.82, "Aligning teams with ambitious Objectives.", 5, listOf("OKRs", "Focus"))
            )
        }
    }

    val prioritizedSet = (activeApp?.prioritized_entities ?: emptyList()).toSet()

    // Filter & Sort
    val filteredNodes = baseNodes.filter {
        searchQuery.isBlank() ||
                it.name.contains(searchQuery, ignoreCase = true) ||
                it.category.name.contains(searchQuery, ignoreCase = true)
    }.sortedWith(
        compareByDescending<ConceptNode> { prioritizedSet.contains(it.name) }
            .thenByDescending { it.centrality }
    )

    LazyColumn(
        modifier = modifier
            .fillMaxSize()
            .background(DarkBackground)
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(14.dp)
    ) {
        // Banner Header
        item {
            Card(
                colors = CardDefaults.cardColors(containerColor = DarkSurface),
                shape = RoundedCornerShape(18.dp),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Text("🏷️", fontSize = 16.sp)
                            Spacer(modifier = Modifier.width(8.dp))
                            Text(
                                text = "Linear Word & Concept Registry",
                                color = DarkOnBackground,
                                fontSize = 14.sp,
                                fontWeight = FontWeight.Bold
                            )
                        }
                        Surface(
                            color = VlkgPrimary.copy(alpha = 0.2f),
                            shape = RoundedCornerShape(8.dp)
                        ) {
                            Text(
                                text = "${filteredNodes.size} Words in Scope",
                                color = VlkgPrimary,
                                fontSize = 11.sp,
                                fontWeight = FontWeight.Bold,
                                modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                            )
                        }
                    }

                    Spacer(modifier = Modifier.height(10.dp))

                    // View Mode Switcher
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(6.dp)
                    ) {
                        listOf(
                            "ladder" to "Ranked Ladder",
                            "pathways" to "Linear Pathways",
                            "categories" to "By Category"
                        ).forEach { (modeKey, modeLabel) ->
                            val active = viewMode == modeKey
                            FilterChip(
                                selected = active,
                                onClick = {
                                    haptic.triggerClick()
                                    onSetViewMode(modeKey)
                                },
                                label = { Text(modeLabel, fontSize = 11.sp, fontWeight = if (active) FontWeight.Bold else FontWeight.Normal) },
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
            }
        }

        // Search Bar
        item {
            OutlinedTextField(
                value = searchQuery,
                onValueChange = { searchQuery = it },
                placeholder = { Text("Search linear words (e.g. Active Listening, GTM)...", color = Color.Gray) },
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
        }

        // Intelligence Lens Filter Chips Row
        item {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(6.dp)
            ) {
                lenses.take(4).forEach { (key, label) ->
                    val active = selectedLens == key
                    FilterChip(
                        selected = active,
                        onClick = {
                            haptic.triggerClick()
                            onSelectLens(key)
                        },
                        label = { Text(label, fontSize = 10.sp) },
                        colors = FilterChipDefaults.filterChipColors(
                            selectedContainerColor = VlkgSecondary.copy(alpha = 0.2f),
                            selectedLabelColor = VlkgSecondary,
                            containerColor = DarkSurfaceVariant,
                            labelColor = Color.LightGray
                        )
                    )
                }
            }
        }

        // ── View Mode 1: Ranked Ladder ──────────────────────────────────
        if (viewMode == "ladder") {
            itemsIndexed(filteredNodes) { index, node ->
                val isPri = prioritizedSet.contains(node.name)

                Card(
                    colors = CardDefaults.cardColors(
                        containerColor = if (isPri) DarkSurfaceVariant else DarkSurface
                    ),
                    shape = RoundedCornerShape(14.dp),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(modifier = Modifier.padding(14.dp)) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Surface(
                                    color = if (isPri) VlkgAccent.copy(alpha = 0.2f) else VlkgPrimary.copy(alpha = 0.2f),
                                    shape = RoundedCornerShape(6.dp),
                                    modifier = Modifier.size(26.dp)
                                ) {
                                    Box(contentAlignment = Alignment.Center) {
                                        Text("#${index + 1}", color = if (isPri) VlkgAccent else VlkgPrimary, fontSize = 11.sp, fontWeight = FontWeight.Bold)
                                    }
                                }
                                Spacer(modifier = Modifier.width(10.dp))
                                Column {
                                    Text(
                                        text = node.name,
                                        color = DarkOnBackground,
                                        fontSize = 15.sp,
                                        fontWeight = FontWeight.Bold
                                    )
                                    Text(
                                        text = node.category.name.replace("_", " "),
                                        color = VlkgSecondary,
                                        fontSize = 11.sp
                                    )
                                }
                            }

                            // Star Prioritize Button
                            IconButton(
                                onClick = {
                                    haptic.triggerSuccess()
                                    onTogglePriority(node.name)
                                }
                            ) {
                                Text(
                                    text = if (isPri) "⭐" else "☆",
                                    fontSize = 18.sp
                                )
                            }
                        }

                        Spacer(modifier = Modifier.height(8.dp))

                        // Centrality Progress Bar
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            LinearProgressIndicator(
                                progress = { node.centrality.toFloat() },
                                modifier = Modifier.weight(1f).height(4.dp),
                                color = if (isPri) VlkgAccent else VlkgPrimary,
                                trackColor = DarkBackground
                            )
                            Text(
                                text = "${(node.centrality * 100).toInt()}%",
                                color = Color.Gray,
                                fontSize = 10.sp,
                                fontWeight = FontWeight.Bold
                            )
                        }

                        Spacer(modifier = Modifier.height(8.dp))

                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(
                                text = "${node.videoCount} Ingested Video Mentions",
                                color = Color.Gray,
                                fontSize = 11.sp
                            )

                            Button(
                                onClick = {
                                    haptic.triggerClick()
                                    onJumpToVideo("dF3GFpIKPlE", "01:24")
                                },
                                colors = ButtonDefaults.buttonColors(containerColor = VlkgPrimary),
                                shape = RoundedCornerShape(6.dp),
                                contentPadding = PaddingValues(horizontal = 8.dp, vertical = 2.dp)
                            ) {
                                Text("▶ Video", fontSize = 11.sp)
                            }
                        }
                    }
                }
            }
        }

        // ── View Mode 2: Linear Pathways ─────────────────────────────────
        if (viewMode == "pathways") {
            item {
                Card(
                    colors = CardDefaults.cardColors(containerColor = DarkSurface),
                    shape = RoundedCornerShape(14.dp),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Text("Executive Strategy Pathway", color = VlkgAccent, fontSize = 13.sp, fontWeight = FontWeight.Bold)
                        Spacer(modifier = Modifier.height(8.dp))
                        Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                            Surface(color = DarkSurfaceVariant, shape = RoundedCornerShape(6.dp)) {
                                Text("First-Principles", color = Color.White, fontSize = 11.sp, modifier = Modifier.padding(6.dp))
                            }
                            Text("➔", color = VlkgPrimary, fontWeight = FontWeight.Bold)
                            Surface(color = DarkSurfaceVariant, shape = RoundedCornerShape(6.dp)) {
                                Text("Leadership", color = Color.White, fontSize = 11.sp, modifier = Modifier.padding(6.dp))
                            }
                            Text("➔", color = VlkgPrimary, fontWeight = FontWeight.Bold)
                            Surface(color = DarkSurfaceVariant, shape = RoundedCornerShape(6.dp)) {
                                Text("Radical Candor", color = Color.White, fontSize = 11.sp, modifier = Modifier.padding(6.dp))
                            }
                        }
                    }
                }
            }
            item {
                Card(
                    colors = CardDefaults.cardColors(containerColor = DarkSurface),
                    shape = RoundedCornerShape(14.dp),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Text("AI Engineering & Systems Pathway", color = VlkgSecondary, fontSize = 13.sp, fontWeight = FontWeight.Bold)
                        Spacer(modifier = Modifier.height(8.dp))
                        Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                            Surface(color = DarkSurfaceVariant, shape = RoundedCornerShape(6.dp)) {
                                Text("Autonomous Agents", color = Color.White, fontSize = 11.sp, modifier = Modifier.padding(6.dp))
                            }
                            Text("➔", color = VlkgSecondary, fontWeight = FontWeight.Bold)
                            Surface(color = DarkSurfaceVariant, shape = RoundedCornerShape(6.dp)) {
                                Text("Systems Dynamics", color = Color.White, fontSize = 11.sp, modifier = Modifier.padding(6.dp))
                            }
                            Text("➔", color = VlkgSecondary, fontWeight = FontWeight.Bold)
                            Surface(color = DarkSurfaceVariant, shape = RoundedCornerShape(6.dp)) {
                                Text("Execution", color = Color.White, fontSize = 11.sp, modifier = Modifier.padding(6.dp))
                            }
                        }
                    }
                }
            }
        }

        // ── View Mode 3: By Category ─────────────────────────────────────
        if (viewMode == "categories") {
            val grouped = filteredNodes.groupBy { it.category }
            grouped.forEach { (cat, nodesInCat) ->
                item {
                    Text(
                        text = "📁 ${cat.name.replace("_", " ")} (${nodesInCat.size})",
                        color = VlkgSecondary,
                        fontSize = 13.sp,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.padding(top = 6.dp)
                    )
                }

                items(nodesInCat) { node ->
                    Surface(
                        color = DarkSurface,
                        shape = RoundedCornerShape(10.dp),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Row(
                            modifier = Modifier.padding(12.dp),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Column {
                                Text(node.name, color = DarkOnBackground, fontSize = 13.sp, fontWeight = FontWeight.SemiBold)
                                Text(node.description, color = Color.Gray, fontSize = 11.sp)
                            }
                            Text("${(node.centrality * 100).toInt()}%", color = VlkgPrimary, fontSize = 11.sp, fontWeight = FontWeight.Bold)
                        }
                    }
                }
            }
        }
    }
}