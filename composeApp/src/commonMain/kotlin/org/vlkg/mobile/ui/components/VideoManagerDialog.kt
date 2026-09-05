package org.vlkg.mobile.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
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
import org.vlkg.mobile.model.VideoMetadata
import org.vlkg.mobile.theme.*

@Composable
fun VideoManagerDialog(
    isOpen: Boolean,
    onClose: () -> Unit,
    activeApp: ChildApp?,
    allVideos: List<VideoMetadata>,
    onSave: (List<String>) -> Unit
) {
    if (!isOpen || activeApp == null) return

    var selectedIds by remember(activeApp, isOpen) {
        mutableStateOf(activeApp.video_ids.toSet())
    }

    val themeColor = parseHexColor(activeApp.theme_color)

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
                        Text("🎬", fontSize = 16.sp)
                    }
                }
                Spacer(modifier = Modifier.width(10.dp))
                Column {
                    Text("Assign Videos & Intelligences", color = DarkOnBackground, fontSize = 16.sp, fontWeight = FontWeight.Bold)
                    Text("Scoped to ${activeApp.name} (${selectedIds.size} active)", color = Color.Gray, fontSize = 11.sp)
                }
            }
        },
        text = {
            LazyColumn(
                modifier = Modifier.fillMaxWidth().heightIn(max = 380.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                items(allVideos) { video ->
                    val isChecked = selectedIds.contains(video.video_id)
                    Card(
                        colors = CardDefaults.cardColors(
                            containerColor = if (isChecked) DarkSurfaceVariant else DarkBackground
                        ),
                        shape = RoundedCornerShape(10.dp),
                        modifier = Modifier
                            .fillMaxWidth()
                            .clickable {
                                selectedIds = if (isChecked) selectedIds - video.video_id else selectedIds + video.video_id
                            }
                    ) {
                        Row(
                            modifier = Modifier.padding(10.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Checkbox(
                                checked = isChecked,
                                onCheckedChange = {
                                    selectedIds = if (it) selectedIds + video.video_id else selectedIds - video.video_id
                                },
                                colors = CheckboxDefaults.colors(
                                    checkedColor = VlkgPrimary,
                                    uncheckedColor = Color.Gray
                                )
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            Column(modifier = Modifier.weight(1f)) {
                                Text(
                                    text = video.title,
                                    color = DarkOnBackground,
                                    fontSize = 13.sp,
                                    fontWeight = FontWeight.SemiBold,
                                    maxLines = 2
                                )
                                Spacer(modifier = Modifier.height(2.dp))
                                Text(
                                    text = "${video.channel} • ${video.duration_sec / 60}m",
                                    color = Color.Gray,
                                    fontSize = 11.sp
                                )
                            }
                        }
                    }
                }
            }
        },
        confirmButton = {
            Button(
                onClick = { onSave(selectedIds.toList()) },
                colors = ButtonDefaults.buttonColors(containerColor = VlkgPrimary),
                shape = RoundedCornerShape(8.dp)
            ) {
                Text("Save Assigned Videos (${selectedIds.size})")
            }
        },
        dismissButton = {
            TextButton(onClick = onClose) {
                Text("Cancel", color = Color.Gray)
            }
        }
    )
}