package org.vlkg.mobile.ui.hub

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
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
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
    modifier: Modifier = Modifier
) {
    val haptic = remember { HapticFeedbackHelper() }
    var expandedApps by remember { mutableStateOf(setOf<String>()) }

    LazyColumn(
        modifier = modifier
            .fillMaxSize()
            .background(DarkBackground)
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // Gradient Banner
        item {
            Card(
                colors = CardDefaults.cardColors(containerColor = DarkSurface),
                shape = RoundedCornerShape(22.dp),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(18.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Surface(
                            color = VlkgPrimary.copy(alpha = 0.2f),
                            shape = RoundedCornerShape(12.dp)
                        ) {
                            Text(
                                text = "✨ MULTI-CHILD-APP KNOWLEDGE HUB",
                                color = VlkgPrimary,
                                fontSize = 10.sp,
                                fontWeight = FontWeight.Bold,
                                modifier = Modifier.padding(horizontal = 10.dp, vertical = 4.dp)
                            )
                        }

                        Button(
                            onClick = onCreateAppClick,
                            colors = ButtonDefaults.buttonColors(containerColor = VlkgPrimary),
                            shape = RoundedCornerShape(10.dp),
                            contentPadding = PaddingValues(horizontal = 12.dp, vertical = 6.dp)
                        ) {
                            Text("+ New App", fontSize = 11.sp, fontWeight = FontWeight.Bold)
                        }
                    }

                    Spacer(modifier = Modifier.height(10.dp))

                    Text(
                        text = "Leadership & Linear Words Platform",
                        color = DarkOnBackground,
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Black
                    )

                    Spacer(modifier = Modifier.height(4.dp))

                    Text(
                        text = "Create isolated knowledge apps, assign YouTube videos, configure intelligence lenses, and explore linear word streams.",
                        color = Color.LightGray,
                        fontSize = 12.sp,
                        lineHeight = 16.sp
                    )
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
                    text = "Active Child Workspaces (${apps.size})",
                    color = Color.Gray,
                    fontSize = 12.sp,
                    fontWeight = FontWeight.Bold
                )

                TextButton(
                    onClick = { onNavigateTab(AppNavigationTab.ASK) }
                ) {
                    Text("Compare Apps (\"Twice Answered\") ➔", color = VlkgPrimary, fontSize = 11.sp, fontWeight = FontWeight.SemiBold)
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
                    containerColor = if (isSelected) DarkSurfaceVariant else DarkSurface
                ),
                shape = RoundedCornerShape(16.dp),
                border = if (isSelected) androidx.compose.foundation.BorderStroke(1.5.dp, VlkgPrimary) else null,
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    // Header
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            modifier = Modifier.clickable { onSelectApp(app) }
                        ) {
                            Box(
                                modifier = Modifier
                                    .size(38.dp)
                                    .clip(RoundedCornerShape(12.dp))
                                    .background(appColor),
                                contentAlignment = Alignment.Center
                            ) {
                                Text("📱", fontSize = 18.sp)
                            }

                            Spacer(modifier = Modifier.width(12.dp))

                            Column {
                                Row(verticalAlignment = Alignment.CenterVertically) {
                                    Text(
                                        text = app.name,
                                        color = DarkOnBackground,
                                        fontSize = 15.sp,
                                        fontWeight = FontWeight.Bold
                                    )
                                    if (isSelected) {
                                        Spacer(modifier = Modifier.width(6.dp))
                                        Surface(
                                            color = VlkgPrimary.copy(alpha = 0.2f),
                                            shape = RoundedCornerShape(4.dp)
                                        ) {
                                            Text(
                                                text = "ACTIVE",
                                                color = VlkgPrimary,
                                                fontSize = 9.sp,
                                                fontWeight = FontWeight.Bold,
                                                modifier = Modifier.padding(horizontal = 5.dp, vertical = 1.dp)
                                            )
                                        }
                                    }
                                }
                                Text(
                                    text = "${app.video_ids.size} Videos · ${defaultWords.size} Linear Words",
                                    color = Color.Gray,
                                    fontSize = 11.sp
                                )
                            }
                        }

                        // Edit / Delete Actions
                        Row {
                            IconButton(onClick = { onEditAppClick(app) }) {
                                Text("✏️", fontSize = 13.sp)
                            }
                            IconButton(onClick = { onDeleteApp(app.id) }) {
                                Text("🗑️", fontSize = 13.sp)
                            }
                        }
                    }

                    Spacer(modifier = Modifier.height(8.dp))

                    Text(
                        text = app.description,
                        color = Color.LightGray,
                        fontSize = 12.sp,
                        lineHeight = 16.sp
                    )

                    Spacer(modifier = Modifier.height(10.dp))

                    // Domain tags
                    Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                        app.focus_domains.forEach { dom ->
                            Surface(
                                color = DarkBackground,
                                shape = RoundedCornerShape(6.dp)
                            ) {
                                Text(
                                    text = dom,
                                    color = Color.Gray,
                                    fontSize = 10.sp,
                                    modifier = Modifier.padding(horizontal = 6.dp, vertical = 3.dp)
                                )
                            }
                        }
                    }

                    Spacer(modifier = Modifier.height(12.dp))

                    // Linear Words section with star prioritization
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .background(DarkBackground.copy(alpha = 0.6f), RoundedCornerShape(10.dp))
                            .padding(10.dp)
                    ) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text("🏷️ Linear Words & Concepts", color = Color.LightGray, fontSize = 11.sp, fontWeight = FontWeight.Bold)
                            Text("Tap ⭐ to prioritize", color = Color.Gray, fontSize = 10.sp)
                        }

                        Spacer(modifier = Modifier.height(6.dp))

                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(6.dp)
                        ) {
                            displayWords.forEach { word ->
                                val isPri = prioritizedSet.contains(word)
                                Surface(
                                    color = if (isPri) VlkgAccent.copy(alpha = 0.2f) else DarkSurfaceVariant,
                                    shape = RoundedCornerShape(8.dp),
                                    modifier = Modifier.clickable {
                                        haptic.triggerSuccess()
                                        onTogglePriority(word)
                                    }
                                ) {
                                    Row(
                                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                                        verticalAlignment = Alignment.CenterVertically
                                    ) {
                                        Text(text = if (isPri) "⭐ " else "☆ ", fontSize = 10.sp)
                                        Text(text = word, color = if (isPri) VlkgAccent else Color.LightGray, fontSize = 10.sp, fontWeight = FontWeight.SemiBold)
                                    }
                                }
                            }
                        }

                        Spacer(modifier = Modifier.height(4.dp))
                        Text(
                            text = if (isExpanded) "▲ Show fewer words" else "▼ +${defaultWords.size - 3} more words",
                            color = VlkgPrimary,
                            fontSize = 10.sp,
                            fontWeight = FontWeight.Bold,
                            modifier = Modifier.clickable {
                                expandedApps = if (isExpanded) expandedApps - app.id else expandedApps + app.id
                            }
                        )
                    }

                    Spacer(modifier = Modifier.height(12.dp))

                    // Card Bottom Actions (Videos, Dossier, Semantics, Linear Words)
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                            FilledTonalButton(
                                onClick = {
                                    onSelectApp(app)
                                    onOpenVideoManager()
                                },
                                shape = RoundedCornerShape(8.dp),
                                contentPadding = PaddingValues(horizontal = 8.dp, vertical = 4.dp)
                            ) {
                                Text("🎬 Videos", fontSize = 10.sp)
                            }

                            FilledTonalButton(
                                onClick = {
                                    onSelectApp(app)
                                    onOpenEnrichments()
                                },
                                shape = RoundedCornerShape(8.dp),
                                contentPadding = PaddingValues(horizontal = 8.dp, vertical = 4.dp)
                            ) {
                                Text("✨ Dossier", fontSize = 10.sp)
                            }

                            FilledTonalButton(
                                onClick = {
                                    onSelectApp(app)
                                    onNavigateTab(AppNavigationTab.PLAYER)
                                },
                                shape = RoundedCornerShape(8.dp),
                                contentPadding = PaddingValues(horizontal = 8.dp, vertical = 4.dp)
                            ) {
                                Text("⚙️ Semantics", fontSize = 10.sp)
                            }
                        }

                        Button(
                            onClick = {
                                onSelectApp(app)
                                onNavigateTab(AppNavigationTab.WORDS)
                            },
                            colors = ButtonDefaults.buttonColors(containerColor = appColor),
                            shape = RoundedCornerShape(8.dp),
                            contentPadding = PaddingValues(horizontal = 10.dp, vertical = 4.dp)
                        ) {
                            Text("Words ➔", fontSize = 11.sp, fontWeight = FontWeight.Bold)
                        }
                    }
                }
            }
        }
    }
}