package org.vlkg.mobile.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
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
import org.vlkg.mobile.theme.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun VlkgTopHeader(
    activeApp: ChildApp?,
    apps: List<ChildApp>,
    onSelectApp: (ChildApp) -> Unit,
    onCreateAppClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    var dropdownExpanded by remember { mutableStateOf(false) }

    Surface(
        color = DarkBackground,
        contentColor = DarkOnBackground,
        modifier = modifier
            .fillMaxWidth()
            .border(width = 1.dp, color = DarkOutline)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 14.dp, vertical = 8.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                modifier = Modifier
                    .clip(RoundedCornerShape(8.dp))
                    .clickable { dropdownExpanded = true }
                    .padding(vertical = 4.dp, horizontal = 6.dp)
            ) {
                // Online Breathing Dot Indicator
                Box(
                    modifier = Modifier
                        .size(8.dp)
                        .clip(CircleShape)
                        .background(VlkgSecondary)
                )
                Spacer(modifier = Modifier.width(8.dp))
                Column {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text(
                            text = activeApp?.name ?: "V-LKG Cockpit",
                            color = DarkOnBackground,
                            fontSize = 14.sp,
                            fontWeight = FontWeight.SemiBold,
                            letterSpacing = (-0.2).sp
                        )
                        Spacer(modifier = Modifier.width(4.dp))
                        Text(
                            text = "[v]",
                            color = Color(0xFF64748B),
                            fontFamily = FontFamily.Monospace,
                            fontSize = 10.sp
                        )
                    }
                    Text(
                        text = "${activeApp?.video_ids?.size ?: 0} STREAMS / ${activeApp?.focus_domains?.size ?: 0} LENSES",
                        color = Color(0xFF94A3B8),
                        fontFamily = FontFamily.Monospace,
                        fontSize = 10.sp,
                        letterSpacing = 0.5.sp
                    )
                }

                DropdownMenu(
                    expanded = dropdownExpanded,
                    onDismissRequest = { dropdownExpanded = false },
                    modifier = Modifier
                        .background(DarkSurface)
                        .border(1.dp, DarkOutline, RoundedCornerShape(8.dp))
                ) {
                    apps.forEach { app ->
                        DropdownMenuItem(
                            text = {
                                Row(verticalAlignment = Alignment.CenterVertically) {
                                    Box(
                                        modifier = Modifier
                                            .size(6.dp)
                                            .clip(CircleShape)
                                            .background(if (app.id == activeApp?.id) VlkgPrimary else Color(0xFF475569))
                                    )
                                    Spacer(modifier = Modifier.width(8.dp))
                                    Text(
                                        text = app.name,
                                        color = if (app.id == activeApp?.id) DarkOnBackground else Color(0xFF94A3B8),
                                        fontSize = 12.sp,
                                        fontWeight = if (app.id == activeApp?.id) FontWeight.Bold else FontWeight.Normal
                                    )
                                }
                            },
                            onClick = {
                                onSelectApp(app)
                                dropdownExpanded = false
                            }
                        )
                    }
                }
            }

            Row(verticalAlignment = Alignment.CenterVertically) {
                // Monospace App Count Pill
                Surface(
                    color = DarkSurfaceVariant,
                    shape = RoundedCornerShape(6.dp),
                    border = androidx.compose.foundation.BorderStroke(1.dp, DarkOutline)
                ) {
                    Text(
                        text = "${apps.size} APPS",
                        fontFamily = FontFamily.Monospace,
                        fontSize = 10.sp,
                        fontWeight = FontWeight.SemiBold,
                        color = Color(0xFF94A3B8),
                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 3.dp)
                    )
                }
                Spacer(modifier = Modifier.width(8.dp))
                OutlinedButton(
                    onClick = onCreateAppClick,
                    shape = RoundedCornerShape(6.dp),
                    border = androidx.compose.foundation.BorderStroke(1.dp, VlkgPrimary.copy(alpha = 0.5f)),
                    colors = ButtonDefaults.outlinedButtonColors(
                        containerColor = VlkgPrimary.copy(alpha = 0.1f),
                        contentColor = VlkgPrimary
                    ),
                    contentPadding = PaddingValues(horizontal = 10.dp, vertical = 4.dp)
                ) {
                    Text(
                        text = "+ NEW",
                        fontSize = 11.sp,
                        fontFamily = FontFamily.Monospace,
                        fontWeight = FontWeight.Bold
                    )
                }
            }
        }
    }
}