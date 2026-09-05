package org.vlkg.mobile.ui.graph

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
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
import org.vlkg.mobile.model.ConceptNode
import org.vlkg.mobile.theme.*
import org.vlkg.mobile.viewmodel.GraphViewModel

@Composable
fun KnowledgeGraphScreen(
    activeApp: ChildApp?,
    selectedLens: String,
    onSelectLens: (String) -> Unit,
    onJumpToVideo: (videoId: String, timestamp: String) -> Unit,
    graphViewModel: GraphViewModel = remember { GraphViewModel() },
    modifier: Modifier = Modifier
) {
    val graphState by graphViewModel.uiState.collectAsState()

    LaunchedEffect(activeApp?.id, selectedLens) {
        graphViewModel.loadGraph(activeApp?.id, selectedLens)
    }

    val lenses = listOf(
        "all" to "All Lenses",
        "executive" to "Executive",
        "learning" to "Learning",
        "thought_leadership" to "Leadership",
        "engineering" to "Engineering",
        "sales" to "Sales"
    )

    Column(modifier = modifier.fillMaxSize().background(DarkBackground)) {
        // Intelligence Domain Chips Row
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 16.dp, vertical = 8.dp),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            lenses.take(4).forEach { (key, label) ->
                val active = selectedLens == key
                FilterChip(
                    selected = active,
                    onClick = { onSelectLens(key) },
                    label = { Text(label, fontSize = 11.sp) },
                    colors = FilterChipDefaults.filterChipColors(
                        selectedContainerColor = VlkgPrimary,
                        selectedLabelColor = Color.White,
                        containerColor = DarkSurfaceVariant,
                        labelColor = Color.LightGray
                    )
                )
            }
        }

        // Graph Canvas with Gestures & Touch Hit Testing
        Box(modifier = Modifier.weight(1f)) {
            GraphCanvas(
                nodes = graphState.nodes,
                edges = graphState.edges,
                selectedNode = graphState.selectedNode,
                scale = graphState.scale,
                offsetX = graphState.offsetX,
                offsetY = graphState.offsetY,
                onNodeSelected = { graphViewModel.selectNode(it) },
                onTransform = { panX, panY, zoom ->
                    graphViewModel.pan(panX, panY)
                    if (zoom != 1f) graphViewModel.zoom(zoom)
                },
                onResetView = { graphViewModel.resetView() }
            )

            // Bottom Selected Node Inspector Card
            graphState.selectedNode?.let { node ->
                Surface(
                    modifier = Modifier
                        .align(Alignment.BottomCenter)
                        .padding(16.dp)
                        .fillMaxWidth(),
                    color = DarkSurface.copy(alpha = 0.95f),
                    shape = RoundedCornerShape(16.dp),
                    border = androidx.compose.foundation.BorderStroke(1.dp, DarkOutline)
                ) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(
                                text = node.category.name.replace("_", " "),
                                color = VlkgSecondary,
                                fontSize = 11.sp,
                                fontWeight = FontWeight.Bold
                            )
                            Text(
                                text = "Centrality ${(node.centrality * 100).toInt()}%",
                                color = VlkgAccent,
                                fontSize = 11.sp,
                                fontWeight = FontWeight.Bold
                            )
                        }

                        Spacer(modifier = Modifier.height(6.dp))

                        Text(
                            text = node.name,
                            color = DarkOnBackground,
                            fontSize = 17.sp,
                            fontWeight = FontWeight.Bold
                        )

                        Spacer(modifier = Modifier.height(4.dp))

                        Text(
                            text = node.description,
                            color = Color.LightGray,
                            fontSize = 12.sp,
                            lineHeight = 16.sp
                        )

                        Spacer(modifier = Modifier.height(10.dp))

                        // Grounding Evidence Jump
                        val evidence = graphState.selectedNodeEvidence.firstOrNull()
                        if (evidence != null) {
                            Button(
                                onClick = {
                                    onJumpToVideo(evidence.videoId, evidence.timestampFormatted)
                                },
                                colors = ButtonDefaults.buttonColors(containerColor = VlkgPrimary),
                                shape = RoundedCornerShape(8.dp),
                                modifier = Modifier.fillMaxWidth()
                            ) {
                                Text(
                                    text = "▶ Inspect Video Grounding (${evidence.timestampFormatted})",
                                    fontSize = 12.sp,
                                    fontWeight = FontWeight.SemiBold
                                )
                            }
                        }
                    }
                }
            }
        }
    }
}