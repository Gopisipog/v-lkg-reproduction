package org.vlkg.mobile.ui.graph

import androidx.compose.animation.core.*
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.gestures.detectTransformGestures
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.PathEffect
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.vlkg.mobile.model.ConceptNode
import org.vlkg.mobile.model.EdgeRelationship
import org.vlkg.mobile.platform.HapticFeedbackHelper
import org.vlkg.mobile.theme.*
import kotlin.math.sqrt

@Composable
fun GraphCanvas(
    nodes: List<ConceptNode>,
    edges: List<EdgeRelationship>,
    selectedNode: ConceptNode?,
    scale: Float,
    offsetX: Float,
    offsetY: Float,
    onNodeSelected: (ConceptNode) -> Unit,
    onTransform: (panX: Float, panY: Float, zoom: Float) -> Unit,
    onResetView: () -> Unit,
    modifier: Modifier = Modifier
) {
    val hapticHelper = remember { HapticFeedbackHelper() }

    // Pulsing halo animation for the selected node
    val infiniteTransition = rememberInfiniteTransition(label = "halo")
    val pulseRadius by infiniteTransition.animateFloat(
        initialValue = 28f,
        targetValue = 44f,
        animationSpec = infiniteRepeatable(
            animation = tween(1200, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "pulseRadius"
    )
    val pulseAlpha by infiniteTransition.animateFloat(
        initialValue = 0.6f,
        targetValue = 0.1f,
        animationSpec = infiniteRepeatable(
            animation = tween(1200, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "pulseAlpha"
    )

    Box(modifier = modifier.fillMaxSize().background(DarkBackground)) {
        Canvas(
            modifier = Modifier
                .fillMaxSize()
                .pointerInput(Unit) {
                    detectTransformGestures { _, pan, zoom, _ ->
                        onTransform(pan.x, pan.y, zoom)
                    }
                }
                .pointerInput(nodes, scale, offsetX, offsetY) {
                    detectTapGestures { tapOffset ->
                        // Reverse transform tap point to graph space
                        val graphX = (tapOffset.x - offsetX) / scale
                        val graphY = (tapOffset.y - offsetY) / scale

                        // Hit test nodes
                        val hitNode = nodes.firstOrNull { node ->
                            val dx = node.x - graphX
                            val dy = node.y - graphY
                            val dist = sqrt(dx * dx + dy * dy)
                            dist <= 40f // Hit radius
                        }

                        if (hitNode != null) {
                            hapticHelper.triggerClick()
                            onNodeSelected(hitNode)
                        }
                    }
                }
        ) {
            val canvasWidth = size.width
            val canvasHeight = size.height

            // Center coordinate origin
            val centerX = canvasWidth / 2f + offsetX
            val centerY = canvasHeight / 2f + offsetY

            // 1. Draw Subtle Grid Lines
            val gridSpacing = 60f * scale
            val startGridX = (offsetX % gridSpacing)
            val startGridY = (offsetY % gridSpacing)
            var curX = startGridX
            while (curX < canvasWidth) {
                drawLine(
                    color = Color.White.copy(alpha = 0.04f),
                    start = Offset(curX, 0f),
                    end = Offset(curX, canvasHeight),
                    strokeWidth = 1f
                )
                curX += gridSpacing
            }
            var curY = startGridY
            while (curY < canvasHeight) {
                drawLine(
                    color = Color.White.copy(alpha = 0.04f),
                    start = Offset(0f, curY),
                    end = Offset(canvasWidth, curY),
                    strokeWidth = 1f
                )
                curY += gridSpacing
            }

            // Build node lookup map
            val nodeMap = nodes.associateBy { it.id }

            // 2. Draw Edges
            edges.forEach { edge ->
                val src = nodeMap[edge.sourceId]
                val dst = nodeMap[edge.targetId]
                if (src != null && dst != null) {
                    val p1 = Offset(src.x * scale + offsetX, src.y * scale + offsetY)
                    val p2 = Offset(dst.x * scale + offsetX, dst.y * scale + offsetY)

                    val isConnectedToSelected = selectedNode != null &&
                            (selectedNode.id == src.id || selectedNode.id == dst.id)

                    val edgeColor = if (isConnectedToSelected) VlkgSecondary else Color(0xFF3B4861)
                    val edgeWidth = if (isConnectedToSelected) 3f * scale else 1.5f * scale

                    drawLine(
                        color = edgeColor,
                        start = p1,
                        end = p2,
                        strokeWidth = edgeWidth.coerceAtLeast(1f),
                        pathEffect = if (isConnectedToSelected) null else PathEffect.dashPathEffect(floatArrayOf(10f, 6f), 0f)
                    )
                }
            }

            // 3. Draw Nodes
            nodes.forEach { node ->
                val nodePos = Offset(node.x * scale + offsetX, node.y * scale + offsetY)
                val isSelected = selectedNode?.id == node.id
                val baseRadius = (18f + (node.centrality * 12f).toFloat()) * scale

                val nodeColor = when (node.category.name) {
                    "CORE_LEADERSHIP" -> VlkgPrimary
                    "DECISION_MAKING" -> VlkgSecondary
                    "AI_INNOVATION" -> VlkgTertiary
                    else -> VlkgAccent
                }

                // Selected glow halo
                if (isSelected) {
                    drawCircle(
                        color = nodeColor.copy(alpha = pulseAlpha),
                        radius = (baseRadius + pulseRadius * scale),
                        center = nodePos
                    )
                    drawCircle(
                        color = nodeColor.copy(alpha = 0.35f),
                        radius = baseRadius + 12f * scale,
                        center = nodePos,
                        style = Stroke(width = 2f * scale)
                    )
                }

                // Node Body
                drawCircle(
                    color = if (isSelected) nodeColor else nodeColor.copy(alpha = 0.85f),
                    radius = baseRadius,
                    center = nodePos
                )

                // Inner core
                drawCircle(
                    color = Color.White.copy(alpha = 0.9f),
                    radius = baseRadius * 0.35f,
                    center = nodePos
                )
            }
        }

        // Floating Control Overlay (Zoom & Reset)
        Column(
            modifier = Modifier
                .align(Alignment.BottomEnd)
                .padding(bottom = 120.dp, end = 16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            SmallFloatingActionButton(
                onClick = { onTransform(0f, 0f, 1.25f) },
                containerColor = DarkSurfaceVariant,
                contentColor = DarkOnBackground,
                shape = CircleShape
            ) {
                Text("+", fontSize = 20.sp)
            }
            SmallFloatingActionButton(
                onClick = { onTransform(0f, 0f, 0.8f) },
                containerColor = DarkSurfaceVariant,
                contentColor = DarkOnBackground,
                shape = CircleShape
            ) {
                Text("−", fontSize = 20.sp)
            }
            SmallFloatingActionButton(
                onClick = onResetView,
                containerColor = DarkSurfaceVariant,
                contentColor = DarkOnBackground,
                shape = CircleShape
            ) {
                Text("⟲", fontSize = 16.sp)
            }
        }
    }
}
