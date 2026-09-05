package org.vlkg.mobile.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.vlkg.mobile.model.ChildApp
import org.vlkg.mobile.theme.*

@Composable
fun EnrichmentsDialog(
    isOpen: Boolean,
    onClose: () -> Unit,
    activeApp: ChildApp?
) {
    if (!isOpen || activeApp == null) return

    val themeColor = parseHexColor(activeApp.theme_color)

    val topCentralEntities = listOf(
        "First-Principles Thinking" to 95,
        "Transformational Leadership" to 90,
        "Autonomous AI Agents" to 88,
        "Systems Dynamics" to 85,
        "High-Output Execution" to 82,
        "Radical Candor" to 78
    )

    val sequentialPathways = listOf(
        "First-Principles Thinking ➔ Transformational Leadership ➔ Radical Candor",
        "Autonomous AI Agents ➔ Systems Dynamics ➔ High-Output Execution"
    )

    AlertDialog(
        onDismissRequest = onClose,
        containerColor = DarkSurface,
        title = {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Surface(
                    color = themeColor.copy(alpha = 0.2f),
                    shape = RoundedCornerShape(8.dp),
                    modifier = Modifier.size(32.dp)
                ) {
                    Box(contentAlignment = Alignment.Center) {
                        Text("✨", fontSize = 16.sp)
                    }
                }
                Spacer(modifier = Modifier.width(10.dp))
                Column {
                    Text("Intelligence Dossier & Enrichments", color = DarkOnBackground, fontSize = 15.sp, fontWeight = FontWeight.Bold)
                    Text("Grounded in ${activeApp.name}", color = Color.Gray, fontSize = 11.sp)
                }
            }
        },
        text = {
            LazyColumn(
                modifier = Modifier.fillMaxWidth().heightIn(max = 420.dp),
                verticalArrangement = Arrangement.spacedBy(14.dp)
            ) {
                // Brief Card
                item {
                    Card(
                        colors = CardDefaults.cardColors(containerColor = DarkSurfaceVariant),
                        shape = RoundedCornerShape(12.dp),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Column(modifier = Modifier.padding(12.dp)) {
                            Text(
                                text = "EXECUTIVE BRIEF & OBJECTIVE",
                                color = VlkgPrimary,
                                fontSize = 10.sp,
                                fontWeight = FontWeight.Bold
                            )
                            Spacer(modifier = Modifier.height(4.dp))
                            Text(
                                text = activeApp.description,
                                color = DarkOnBackground,
                                fontSize = 12.sp,
                                lineHeight = 16.sp
                            )
                            Spacer(modifier = Modifier.height(8.dp))
                            Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                                Text("● 6 Linear Words", color = Color.Gray, fontSize = 11.sp)
                                Text("● 6 Pathways", color = Color.Gray, fontSize = 11.sp)
                                Text("● ${activeApp.video_ids.size} Videos", color = Color.Gray, fontSize = 11.sp)
                            }
                        }
                    }
                }

                // Top Central Entities Grid
                item {
                    Text(
                        text = "📈 Top Central Entities (Influence Ranking)",
                        color = DarkOnBackground,
                        fontSize = 13.sp,
                        fontWeight = FontWeight.Bold
                    )
                }

                item {
                    Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                        topCentralEntities.chunked(2).forEach { row ->
                            Row(horizontalArrangement = Arrangement.spacedBy(6.dp), modifier = Modifier.fillMaxWidth()) {
                                row.forEach { (label, centrality) ->
                                    Surface(
                                        color = DarkSurfaceVariant,
                                        shape = RoundedCornerShape(8.dp),
                                        modifier = Modifier.weight(1f)
                                    ) {
                                        Row(
                                            modifier = Modifier.padding(8.dp),
                                            horizontalArrangement = Arrangement.SpaceBetween,
                                            verticalAlignment = Alignment.CenterVertically
                                        ) {
                                            Text(text = label, color = DarkOnBackground, fontSize = 11.sp, maxLines = 1, modifier = Modifier.weight(1f))
                                            Surface(
                                                color = VlkgPrimary.copy(alpha = 0.2f),
                                                shape = RoundedCornerShape(4.dp)
                                            ) {
                                                Text(text = "$centrality%", color = VlkgPrimary, fontSize = 9.sp, fontWeight = FontWeight.Bold, modifier = Modifier.padding(horizontal = 4.dp, vertical = 2.dp))
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                // Dependency Chains
                item {
                    Text(
                        text = "⛓️ Sequential Prerequisite Chains",
                        color = DarkOnBackground,
                        fontSize = 13.sp,
                        fontWeight = FontWeight.Bold
                    )
                }

                items(sequentialPathways) { pathway ->
                    Surface(
                        color = DarkSurfaceVariant,
                        shape = RoundedCornerShape(8.dp),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text(
                            text = pathway,
                            color = VlkgSecondary,
                            fontSize = 11.sp,
                            fontWeight = FontWeight.Medium,
                            modifier = Modifier.padding(10.dp)
                        )
                    }
                }
            }
        },
        confirmButton = {
            Button(
                onClick = onClose,
                colors = ButtonDefaults.buttonColors(containerColor = VlkgPrimary),
                shape = RoundedCornerShape(8.dp)
            ) {
                Text("Done")
            }
        }
    )
}