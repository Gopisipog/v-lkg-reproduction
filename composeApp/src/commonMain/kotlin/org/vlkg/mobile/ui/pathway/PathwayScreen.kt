package org.vlkg.mobile.ui.pathway

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.vlkg.mobile.model.LearningPathway
import org.vlkg.mobile.platform.HapticFeedbackHelper
import org.vlkg.mobile.theme.*

@Composable
fun PathwayScreen(
    pathways: List<LearningPathway>,
    selectedPathway: LearningPathway?,
    completedStepIds: Set<String>,
    onSelectPathway: (LearningPathway) -> Unit,
    onToggleStep: (String) -> Unit,
    modifier: Modifier = Modifier
) {
    val haptic = remember { HapticFeedbackHelper() }

    LazyColumn(
        modifier = modifier
            .fillMaxSize()
            .background(DarkBackground)
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        item {
            Text(
                text = "Structured Learning Pathways",
                color = DarkOnBackground,
                fontSize = 20.sp,
                fontWeight = FontWeight.Bold
            )
            Text(
                text = "Prerequisite sequences mined directly from video knowledge triplets",
                color = Color.Gray,
                fontSize = 13.sp
            )
        }

        // Pathway Selector Chips
        item {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                pathways.forEach { pathway ->
                    val isSelected = selectedPathway?.id == pathway.id
                    FilterChip(
                        selected = isSelected,
                        onClick = {
                            haptic.triggerClick()
                            onSelectPathway(pathway)
                        },
                        label = {
                            Text(
                                text = pathway.title,
                                fontSize = 12.sp,
                                maxLines = 1
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

        if (selectedPathway != null) {
            val totalSteps = selectedPathway.steps.size
            val completedCount = selectedPathway.steps.count { completedStepIds.contains(it.id) }
            val progress = if (totalSteps > 0) completedCount.toFloat() / totalSteps else 0f

            item {
                // Pathway Progress Banner
                Card(
                    colors = CardDefaults.cardColors(containerColor = DarkSurface),
                    shape = RoundedCornerShape(14.dp),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Text(
                                text = "Role: ${selectedPathway.targetRole}",
                                color = VlkgSecondary,
                                fontSize = 12.sp,
                                fontWeight = FontWeight.SemiBold
                            )
                            Text(
                                text = "${(progress * 100).toInt()}% Complete",
                                color = VlkgTertiary,
                                fontSize = 12.sp,
                                fontWeight = FontWeight.Bold
                            )
                        }

                        Spacer(modifier = Modifier.height(6.dp))

                        Text(
                            text = selectedPathway.title,
                            color = DarkOnBackground,
                            fontSize = 17.sp,
                            fontWeight = FontWeight.Bold
                        )

                        Spacer(modifier = Modifier.height(10.dp))

                        LinearProgressIndicator(
                            progress = { progress },
                            modifier = Modifier.fillMaxWidth().height(6.dp),
                            color = VlkgTertiary,
                            trackColor = DarkSurfaceVariant
                        )
                    }
                }
            }

            item {
                Text(
                    text = "Pathway Milestones & Prerequisites",
                    color = DarkOnBackground,
                    fontSize = 15.sp,
                    fontWeight = FontWeight.SemiBold
                )
            }

            // Step List
            itemsIndexed(selectedPathway.steps) { index, step ->
                val isMastered = completedStepIds.contains(step.id)

                Card(
                    colors = CardDefaults.cardColors(
                        containerColor = if (isMastered) DarkSurface.copy(alpha = 0.6f) else DarkSurfaceVariant
                    ),
                    shape = RoundedCornerShape(12.dp),
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable {
                            if (!isMastered) haptic.triggerSuccess() else haptic.triggerClick()
                            onToggleStep(step.id)
                        }
                ) {
                    Row(
                        modifier = Modifier.padding(14.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        // Step number / check circle
                        Surface(
                            shape = CircleShape,
                            color = if (isMastered) VlkgTertiary else VlkgPrimary.copy(alpha = 0.2f),
                            modifier = Modifier.size(36.dp)
                        ) {
                            Box(contentAlignment = Alignment.Center) {
                                Text(
                                    text = if (isMastered) "✓" else "${index + 1}",
                                    color = if (isMastered) Color.White else VlkgPrimary,
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 14.sp
                                )
                            }
                        }

                        Spacer(modifier = Modifier.width(14.dp))

                        Column(modifier = Modifier.weight(1f)) {
                            Text(
                                text = step.name,
                                color = if (isMastered) Color.Gray else DarkOnBackground,
                                fontSize = 15.sp,
                                fontWeight = FontWeight.SemiBold
                            )
                            Spacer(modifier = Modifier.height(4.dp))
                            Text(
                                text = step.description,
                                color = Color.Gray,
                                fontSize = 12.sp,
                                maxLines = 2
                            )
                        }
                    }
                }
            }
        }
    }
}
