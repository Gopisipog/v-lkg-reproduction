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
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.vlkg.mobile.theme.*

@Composable
fun CreateAppDialog(
    isOpen: Boolean,
    onClose: () -> Unit,
    editingApp: org.vlkg.mobile.model.ChildApp? = null,
    onCreate: (name: String, desc: String, color: String, domains: List<String>) -> Unit
) {
    if (!isOpen) return

    var name by remember(editingApp, isOpen) { mutableStateOf(editingApp?.name ?: "") }
    var desc by remember(editingApp, isOpen) { mutableStateOf(editingApp?.description ?: "") }
    var selectedColor by remember(editingApp, isOpen) { mutableStateOf(editingApp?.theme_color ?: "#6366f1") }
    var selectedDomains by remember(editingApp, isOpen) {
        mutableStateOf(editingApp?.focus_domains?.toSet() ?: setOf("executive", "learning"))
    }

    val colorOptions = listOf("#6366f1", "#3b82f6", "#14b8a6", "#10b981", "#f59e0b", "#ec4899", "#8b5cf6")
    val domainOptions = listOf(
        "executive" to "Executive",
        "learning" to "Learning",
        "thought_leadership" to "Thought Leadership",
        "engineering" to "Engineering & AI",
        "sales" to "Sales & GTM",
        "compliance" to "Compliance"
    )

    AlertDialog(
        onDismissRequest = onClose,
        containerColor = DarkSurface,
        title = {
            Text(
                text = if (editingApp != null) "Edit Child App" else "Create New Child App",
                color = DarkOnBackground,
                fontSize = 18.sp,
                fontWeight = FontWeight.Bold
            )
        },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                OutlinedTextField(
                    value = name,
                    onValueChange = { name = it },
                    label = { Text("App Name", color = Color.Gray) },
                    placeholder = { Text("e.g. AI Product Leadership", color = Color.DarkGray) },
                    singleLine = true,
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedTextColor = DarkOnBackground,
                        unfocusedTextColor = DarkOnBackground,
                        focusedBorderColor = VlkgPrimary,
                        unfocusedBorderColor = DarkOutline
                    ),
                    modifier = Modifier.fillMaxWidth()
                )

                OutlinedTextField(
                    value = desc,
                    onValueChange = { desc = it },
                    label = { Text("Description", color = Color.Gray) },
                    placeholder = { Text("Core focus and strategic domains...", color = Color.DarkGray) },
                    maxLines = 3,
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedTextColor = DarkOnBackground,
                        unfocusedTextColor = DarkOnBackground,
                        focusedBorderColor = VlkgPrimary,
                        unfocusedBorderColor = DarkOutline
                    ),
                    modifier = Modifier.fillMaxWidth()
                )

                Text("Theme Color", color = Color.LightGray, fontSize = 12.sp, fontWeight = FontWeight.SemiBold)
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    colorOptions.forEach { hex ->
                        val isSelected = selectedColor == hex
                        Box(
                            modifier = Modifier
                                .size(28.dp)
                                .clip(CircleShape)
                                .background(parseHexColor(hex))
                                .clickable { selectedColor = hex }
                                .then(
                                    if (isSelected) Modifier.border(2.dp, Color.White, CircleShape) else Modifier
                                )
                        )
                    }
                }

                Text("Focus Intelligence Domains", color = Color.LightGray, fontSize = 12.sp, fontWeight = FontWeight.SemiBold)
                Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    domainOptions.chunked(2).forEach { row ->
                        Row(horizontalArrangement = Arrangement.spacedBy(6.dp), modifier = Modifier.fillMaxWidth()) {
                            row.forEach { (key, label) ->
                                val active = selectedDomains.contains(key)
                                FilterChip(
                                    selected = active,
                                    onClick = {
                                        selectedDomains = if (active) selectedDomains - key else selectedDomains + key
                                    },
                                    label = { Text(label, fontSize = 10.sp) },
                                    colors = FilterChipDefaults.filterChipColors(
                                        selectedContainerColor = VlkgPrimary,
                                        selectedLabelColor = Color.White,
                                        containerColor = DarkSurfaceVariant,
                                        labelColor = Color.LightGray
                                    ),
                                    modifier = Modifier.weight(1f)
                                )
                            }
                        }
                    }
                }
            }
        },
        confirmButton = {
            Button(
                onClick = {
                    if (name.isNotBlank()) {
                        onCreate(name, desc, selectedColor, selectedDomains.toList())
                    }
                },
                enabled = name.isNotBlank(),
                colors = ButtonDefaults.buttonColors(containerColor = VlkgPrimary),
                shape = RoundedCornerShape(8.dp)
            ) {
                Text(if (editingApp != null) "Save Changes" else "Create App")
            }
        },
        dismissButton = {
            TextButton(onClick = onClose) {
                Text("Cancel", color = Color.Gray)
            }
        }
    )
}