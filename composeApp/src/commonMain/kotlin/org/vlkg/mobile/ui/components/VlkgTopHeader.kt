package org.vlkg.mobile.ui.components

import androidx.compose.foundation.background
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

    TopAppBar(
        title = {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                modifier = Modifier.clickable { dropdownExpanded = true }
            ) {
                // Active Child App Indicator Dot
                Box(
                    modifier = Modifier
                        .size(10.dp)
                        .clip(CircleShape)
                        .background(parseHexColor(activeApp?.theme_color ?: "#6366f1"))
                )
                Spacer(modifier = Modifier.width(8.dp))
                Column {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text(
                            text = activeApp?.name ?: "V-LKG Mobile",
                            color = DarkOnBackground,
                            fontSize = 15.sp,
                            fontWeight = FontWeight.Bold,
                            maxLines = 1
                        )
                        Text(
                            text = " ▾",
                            color = Color.Gray,
                            fontSize = 12.sp
                        )
                    }
                    Text(
                        text = "${activeApp?.video_ids?.size ?: 0} Videos • ${activeApp?.focus_domains?.joinToString(", ") ?: "All"}",
                        color = Color.Gray,
                        fontSize = 11.sp,
                        maxLines = 1
                    )
                }

                DropdownMenu(
                    expanded = dropdownExpanded,
                    onDismissRequest = { dropdownExpanded = false },
                    modifier = Modifier.background(DarkSurfaceVariant)
                ) {
                    apps.forEach { app ->
                        DropdownMenuItem(
                            text = {
                                Row(verticalAlignment = Alignment.CenterVertically) {
                                    Text(
                                        text = if (app.id == activeApp?.id) "✓ " else "  ",
                                        color = VlkgPrimary,
                                        fontWeight = FontWeight.Bold
                                    )
                                    Text(
                                        text = app.name,
                                        color = DarkOnBackground,
                                        fontSize = 14.sp
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
        },
        actions = {
            FilledTonalButton(
                onClick = onCreateAppClick,
                colors = ButtonDefaults.filledTonalButtonColors(
                    containerColor = VlkgPrimary.copy(alpha = 0.2f),
                    contentColor = VlkgPrimary
                ),
                shape = RoundedCornerShape(8.dp),
                contentPadding = PaddingValues(horizontal = 10.dp, vertical = 6.dp)
            ) {
                Text("+ App", fontSize = 12.sp, fontWeight = FontWeight.Bold)
            }
        },
        colors = TopAppBarDefaults.topAppBarColors(
            containerColor = DarkBackground,
            titleContentColor = DarkOnBackground
        ),
        modifier = modifier
    )
}