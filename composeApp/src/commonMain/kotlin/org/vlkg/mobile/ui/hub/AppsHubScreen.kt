package org.vlkg.mobile.ui.hub

import androidx.compose.foundation.background
import androidx.compose.foundation.border
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
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.vlkg.mobile.model.ChildApp
import org.vlkg.mobile.platform.HapticFeedbackHelper
import org.vlkg.mobile.theme.*
import org.vlkg.mobile.viewmodel.AppNavigationTab

@Composable
fun AppsHubScreen(
    activeApp: ChildApp?,
    apps: List<ChildApp>,
    onSelectApp: (ChildApp) -> Unit,
    onNavigateTab: (AppNavigationTab) -> Unit,
    onTogglePriority: (String) -> Unit,
    onCreateAppClick: () -> Unit,
    onEditAppClick: (ChildApp) -> Unit = {},
    onDeleteApp: (String) -> Unit = {},
    onOpenVideoManager: () -> Unit = {},
    onOpenEnrichments: () -> Unit = {},
    databaseStatus: org.vlkg.mobile.model.DatabaseStatusResponse? = null,
    modifier: Modifier = Modifier
) {
    val haptic = remember { HapticFeedbackHelper() }
    var expandedApps by remember { mutableStateOf(setOf<String>()) }

    LazyColumn(
        modifier = modifier
            .fillMaxSize()
            .background(DarkBackground)
            .padding(14.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        // Cockpit Bento Hero Card (2fr / 1fr feel)
        item {
            Card(
                colors = CardDefaults.cardColors(containerColor = DarkSurface),
                shape = RoundedCornerShape(12.dp),
                border = androidx.compose.foundation.BorderStroke(1.dp, DarkOutline),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Surface(
                            color = VlkgPrimary.copy(alpha = 0.15f),
                            shape = RoundedCornerShape(6.dp),
                            border = androidx.compose.foundation.BorderStroke(1.dp, VlkgPrimary.copy(alpha = 0.35f))
                        ) {
                            Text(
                                text = "KNOWLEDGE WORKSPACE COCKPIT",
                                color = VlkgPrimary,
                                fontFamily = FontFamily.Monospace,
                                fontSize = 9.sp,
                                fontWeight = FontWeight.Bold,
                                modifier = Modifier.padding(horizontal = 8.dp, vertical = 3.dp)
                            )
                        }

                        OutlinedButton(
                            onClick = onCreateAppClick,
                            border = androidx.compose.foundation.BorderStroke(1.dp, VlkgPrimary.copy(alpha = 0.6f)),
                            colors = ButtonDefaults.outlinedButtonColors(
                                containerColor = VlkgPrimary.copy(alpha = 0.1f),
                                contentColor = VlkgPrimary
                            ),
                            shape = RoundedCornerShape(6.dp),
                            contentPadding = PaddingValues(horizontal = 10.dp, vertical = 4.dp)
                        ) {
                            Text("+ NEW WORKSPACE", fontSize = 10.sp, fontFamily = FontFamily.Monospace, fontWeight = FontWeight.Bold)
                        }
                    }

                    Spacer(modifier = Modifier.height(10.dp))

                    Text(
                        text = "V-LKG Leadership & Semantic Streams",
                        color = DarkOnBackground,
                        fontSize = 16.sp,
                        fontWeight = FontWeight.Bold,
                        letterSpacing = (-0.3).sp
                    )

                    Spacer(modifier = Modifier.height(4.dp))

                    Text(
                        text = "Modular multimodal knowledge spaces. Spoken video intelligence parsed into sequential linear words and causal pathways.",
                        color = Color(0xFF94A3B8),
                        fontSize = 11.sp,
                        lineHeight = 15.sp
                    )

                    Spacer(modifier = Modifier.height(10.dp))

                    // Telemetry Status Bar
                    Surface(
                        color = DarkBackground,
                        shape = RoundedCornerShape(6.dp),
                        border = androidx.compose.foundation.BorderStroke(1.dp, DarkOutline)
                    ) {
                        Row(
                            modifier = Modifier.padding(horizontal = 10.dp, vertical = 5.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Box(
                                modifier = Modifier
                                    .size(6.dp)
                                    .clip(CircleShape)
                                    .background(VlkgSecondary)
                            )
                            Spacer(modifier = Modifier.width(6.dp))
                            Text(
                                text = if (databaseStatus?.is_connected_to_aura == true) "AURA DB" else "LOCAL STORE",
                                color = VlkgSecondary,
                                fontFamily = FontFamily.Monospace,
                                fontSize = 10.sp,
                                fontWeight = FontWeight.Bold
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            Text(
                                text = "/ ${databaseStatus?.repository_stats?.entities_count ?: 252} ENTITIES / ${databaseStatus?.repository_stats?.triplets_count ?: 770} TRIPLETS",
                                color = Color(0xFF64748B),
                                fontFamily = FontFamily.Monospace,
                                fontSize = 10.sp
                            )
                        }
                    }
                }
            }
        }

        // Section Title & "Compare Apps" Button
        item {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "ACTIVE WORKSPACES (${apps.size})",
                    color = Color(0xFF64748B),
                    fontFamily = FontFamily.Monospace,
                    fontSize = 10.sp,
                    fontWeight = FontWeight.Bold,
                    letterSpacing = 0.5.sp
                )

                TextButton(
                    onClick = { onNavigateTab(AppNavigationTab.ASK) }
                ) {
                    Text("CROSS-QUERY WORKSPACES [->]", color = VlkgPrimary, fontFamily = FontFamily.Monospace, fontSize = 10.sp, fontWeight = FontWeight.Bold)
                }
            }
        }

        // Child App Cards
        items(apps) { app ->
            val isSelected = app.id == activeApp?.id
            val appColor = parseHexColor(app.theme_color)
            val isExpanded = expandedApps.contains(app.id)

            val defaultWords = listOf(
                "First-Principles Thinking",
                "Transformational Leadership",
                "Autonomous AI Agents",
                "Radical Candor",
                "Systems Dynamics",
                "High-Output Execution"
            )
            val displayWords = if (isExpanded) defaultWords else defaultWords.take(3)
            val prioritizedSet = app.prioritized_entities.toSet()

            Card(
                colors = CardDefaults.cardColors(
                    containerColor = if (isSelected) DarkSurfaceVariant.copy(alpha = 0.6f) else DarkSurface
                ),
                shape = RoundedCornerShape(10.dp),
                border = androidx.compose.foundation.BorderStroke(
                    width = 1.dp,
                    color = if (isSelected) VlkgPrimary.copy(alpha = 0.8f) else DarkOutline
                ),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(14.dp)) {
                    // Header
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            modifier = Modifier
                                .weight(1f)
                                .clickable { onSelectApp(app) }
                        ) {
                            Box(
                                modifier = Modifier
                                    .size(32.dp)
                                    .clip(RoundedCornerShape(8.dp))
                                    .background(appColor),
                                contentAlignment = Alignment.Center
                            ) {
                                Text(
                                    text = app.name.take(1).uppercase(),
                                    fontFamily = FontFamily.Monospace,
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 14.sp,
                                    color = Color.White
                                )
                            }

                            Spacer(modifier = Modifier.width(10.dp))

                            Column {
                                Row(verticalAlignment = Alignment.CenterVertically) {
                                    Text(
                                        text = app.name,
                                        color = DarkOnBackground,
                                        fontSize = 13.sp,
                                        fontWeight = FontWeight.SemiBold
                                    )
                                    if (isSelected) {
                                        Spacer(modifier = Modifier.width(6.dp))
                                        Surface(
                                            color = VlkgPrimary.copy(alpha = 0.15f),
                                            shape = RoundedCornerShape(4.dp),
                                            border = androidx.compose.foundation.BorderStroke(1.dp, VlkgPrimary.copy(alpha = 0.4f))
                                        ) {
                                            Text(
                                                text = "ACTIVE",
                                                color = VlkgPrimary,
                                                fontFamily = FontFamily.Monospace,
                                                fontSize = 8.sp,
                                                fontWeight = FontWeight.Bold,
                                                modifier = Modifier.padding(horizontal = 4.dp, vertical = 1.dp)
                                            )
                                        }
                                    }
                                }
                                Text(
                                    text = "${app.video_ids.size} STREAMS / ${defaultWords.size} WORDS",
                                    color = Color(0xFF64748B),
                                    fontFamily = FontFamily.Monospace,
                                    fontSize = 10.sp
                                )
                            }
                        }

                        // Edit / Delete Actions
                        Row {
                            TextButton(
                                onClick = { onEditAppClick(app) },
                                contentPadding = PaddingValues(horizontal = 6.dp, vertical = 2.dp)
                            ) {
                                Text("EDIT", color = Color(0xFF94A3B8), fontFamily = FontFamily.Monospace, fontSize = 10.sp)
                            }
                            TextButton(
                                onClick = { onDeleteApp(app.id) },
                                contentPadding = PaddingValues(horizontal = 6.dp, vertical = 2.dp)
                            ) {
                                Text("DEL", color = Color(0xFFEF4444), fontFamily = FontFamily.Monospace, fontSize = 10.sp)
                            }
                        }
                    }

                    Spacer(modifier = Modifier.height(6.dp))

                    Text(
                        text = app.description,
                        color = Color(0xFF94A3B8),
                        fontSize = 11.sp,
                        lineHeight = 15.sp
                    )

                    Spacer(modifier = Modifier.height(8.dp))

                    @OptIn(ExperimentalLayoutApi::class)
                    FlowRow(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(4.dp),
                        verticalArrangement = Arrangement.spacedBy(4.dp)
                    ) {
                        app.focus_domains.forEach { dom ->
                            Surface(
                                color = DarkBackground,
                                shape = RoundedCornerShape(4.dp),
                                border = androidx.compose.foundation.BorderStroke(1.dp, DarkOutline)
                            ) {
                                Text(
                                    text = dom.uppercase(),
                                    color = Color(0xFF64748B),
                                    fontFamily = FontFamily.Monospace,
                                    fontSize = 9.sp,
                                    fontWeight = FontWeight.SemiBold,
                                    modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                                )
                            }
                        }
                    }

                    Spacer(modifier = Modifier.height(10.dp))

                    // Linear Words section with priority indicator
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .background(DarkBackground.copy(alpha = 0.8f), RoundedCornerShape(8.dp))
                            .border(1.dp, DarkOutline, RoundedCornerShape(8.dp))
                            .padding(8.dp)
                    ) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text("PRIORITIZED CONCEPTS", color = Color(0xFF64748B), fontFamily = FontFamily.Monospace, fontSize = 9.sp, fontWeight = FontWeight.Bold)
                            Text("TAP TO PIN", color = Color(0xFF475569), fontFamily = FontFamily.Monospace, fontSize = 8.sp)
                        }

                        Spacer(modifier = Modifier.height(6.dp))

                        @OptIn(ExperimentalLayoutApi::class)
                        FlowRow(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(4.dp),
                            verticalArrangement = Arrangement.spacedBy(4.dp)
                        ) {
                            displayWords.forEach { word ->
                                val isPri = prioritizedSet.contains(word)
                                Surface(
                                    color = if (isPri) VlkgAccent.copy(alpha = 0.15f) else DarkSurfaceVariant,
                                    shape = RoundedCornerShape(6.dp),
                                    border = androidx.compose.foundation.BorderStroke(
                                        1.dp,
                                        if (isPri) VlkgAccent.copy(alpha = 0.5f) else DarkOutline
                                    ),
                                    modifier = Modifier.clickable {
                                        haptic.triggerSuccess()
                                        onTogglePriority(word)
                                    }
                                ) {
                                    Row(
                                        modifier = Modifier.padding(horizontal = 6.dp, vertical = 3.dp),
                                        verticalAlignment = Alignment.CenterVertically
                                    ) {
                                        Text(
                                            text = if (isPri) "[PIN] " else "",
                                            fontFamily = FontFamily.Monospace,
                                            fontSize = 8.sp,
                                            color = VlkgAccent,
                                            fontWeight = FontWeight.Bold
                                        )
                                        Text(
                                            text = word,
                                            color = if (isPri) VlkgAccent else DarkOnSurface,
                                            fontSize = 10.sp,
                                            fontWeight = FontWeight.Medium
                                        )
                                    }
                                }
                            }
                        }

                        Spacer(modifier = Modifier.height(4.dp))
                        Text(
                            text = if (isExpanded) "[-] SHOW LESS" else "[+] +${defaultWords.size - 3} MORE CONCEPTS",
                            color = VlkgPrimary,
                            fontFamily = FontFamily.Monospace,
                            fontSize = 9.sp,
                            fontWeight = FontWeight.Bold,
                            modifier = Modifier.clickable {
                                expandedApps = if (isExpanded) expandedApps - app.id else expandedApps + app.id
                            }
                        )
                    }

                    Spacer(modifier = Modifier.height(10.dp))

                    // Card Bottom Actions
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Row(horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                            OutlinedButton(
                                onClick = {
                                    onSelectApp(app)
                                    onOpenVideoManager()
                                },
                                shape = RoundedCornerShape(6.dp),
                                border = androidx.compose.foundation.BorderStroke(1.dp, DarkOutline),
                                contentPadding = PaddingValues(horizontal = 8.dp, vertical = 2.dp)
                            ) {
                                Text("VIDEOS", fontFamily = FontFamily.Monospace, fontSize = 9.sp, color = DarkOnSurface)
                            }

                            OutlinedButton(
                                onClick = {
                                    onSelectApp(app)
                                    onOpenEnrichments()
                                },
                                shape = RoundedCornerShape(6.dp),
                                border = androidx.compose.foundation.BorderStroke(1.dp, DarkOutline),
                                contentPadding = PaddingValues(horizontal = 8.dp, vertical = 2.dp)
                            ) {
                                Text("DOSSIER", fontFamily = FontFamily.Monospace, fontSize = 9.sp, color = DarkOnSurface)
                            }
                        }

                        Button(
                            onClick = {
                                onSelectApp(app)
                                onNavigateTab(AppNavigationTab.WORDS)
                            },
                            colors = ButtonDefaults.buttonColors(containerColor = VlkgPrimary),
                            shape = RoundedCornerShape(6.dp),
                            contentPadding = PaddingValues(horizontal = 10.dp, vertical = 4.dp)
                        ) {
                            Text("EXPLORE [->]", fontFamily = FontFamily.Monospace, fontSize = 10.sp, fontWeight = FontWeight.Bold)
                        }
                    }
                }
            }
        }
    }
}