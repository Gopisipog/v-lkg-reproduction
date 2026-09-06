package org.vlkg.mobile.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.vlkg.mobile.theme.*

@Composable
fun CreateAppDialog(
    isOpen: Boolean,
    onClose: () -> Unit,
    editingApp: org.vlkg.mobile.model.ChildApp? = null,
    onCreate: (
        name: String,
        desc: String,
        colorScheme: String,
        pattern: String,
        patternColors: List<String>,
        domains: List<String>,
        saveToAura: Boolean
    ) -> Unit
) {
    if (!isOpen) return

    var name by remember(editingApp, isOpen) { mutableStateOf(editingApp?.name ?: "") }
    var desc by remember(editingApp, isOpen) { mutableStateOf(editingApp?.description ?: "") }
    var selectedTab by remember(editingApp, isOpen) { mutableStateOf(if ((editingApp?.pattern_colors?.size ?: 2) > 2) 1 else 0) } // 0 = Bi-Color, 1 = Tri-Color
    
    var selectedSchemeId by remember(editingApp, isOpen) { 
        mutableStateOf(editingApp?.color_scheme ?: BI_COLOR_PRESETS.first().id) 
    }
    var selectedPattern by remember(editingApp, isOpen) { 
        mutableStateOf(editingApp?.pattern ?: "gradient-bi") 
    }
    var selectedColors by remember(editingApp, isOpen) {
        val initial = if (editingApp != null && editingApp.pattern_colors.isNotEmpty()) {
            editingApp.pattern_colors
        } else {
            BI_COLOR_PRESETS.first().colors
        }
        mutableStateOf(initial)
    }
    var saveToAura by remember(editingApp, isOpen) { mutableStateOf(true) }
    var selectedDomains by remember(editingApp, isOpen) {
        mutableStateOf(editingApp?.focus_domains?.toSet() ?: setOf("executive", "learning"))
    }

    val domainOptions = listOf(
        "executive" to "Executive",
        "learning" to "Learning",
        "thought_leadership" to "Thought Leadership",
        "engineering" to "Engineering & AI",
        "sales" to "Sales & GTM",
        "compliance" to "Compliance"
    )

    val currentBrush = getPatternBrush(selectedPattern, selectedColors.map { parseHexColor(it) })

    AlertDialog(
        onDismissRequest = onClose,
        containerColor = DarkSurface,
        modifier = Modifier.widthIn(max = 540.dp),
        title = {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text(
                        text = if (editingApp != null) "Edit Child App Workspace" else "Create New Child App Workspace",
                        color = DarkOnBackground,
                        fontSize = 17.sp,
                        fontWeight = FontWeight.Bold
                    )
                    Text(
                        text = "Custom Mixed Color Schemes & Bi/Tri Geometric Patterns",
                        color = VlkgPrimary,
                        fontSize = 11.sp,
                        fontFamily = FontFamily.Monospace
                    )
                }
            }
        },
        text = {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .verticalScroll(rememberScrollState()),
                verticalArrangement = Arrangement.spacedBy(14.dp)
            ) {
                // Live Card Preview
                Surface(
                    color = DarkBackground,
                    shape = RoundedCornerShape(10.dp),
                    border = androidx.compose.foundation.BorderStroke(1.dp, DarkOutline),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column {
                        // Pattern top bar
                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(6.dp)
                                .background(currentBrush)
                        )
                        Row(
                            modifier = Modifier.padding(12.dp),
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Box(
                                    modifier = Modifier
                                        .size(36.dp)
                                        .clip(RoundedCornerShape(8.dp))
                                        .background(currentBrush),
                                    contentAlignment = Alignment.Center
                                ) {
                                    Text("APP", color = Color.White, fontSize = 10.sp, fontWeight = FontWeight.Bold, fontFamily = FontFamily.Monospace)
                                }
                                Spacer(modifier = Modifier.width(10.dp))
                                Column {
                                    Text(
                                        text = if (name.isNotBlank()) name else "Workspace Card Preview",
                                        color = DarkOnBackground,
                                        fontSize = 14.sp,
                                        fontWeight = FontWeight.Bold
                                    )
                                    Text(
                                        text = "${selectedColors.size}-Color · ${selectedPattern.uppercase()}",
                                        color = Color(0xFF94A3B8),
                                        fontSize = 10.sp,
                                        fontFamily = FontFamily.Monospace
                                    )
                                }
                            }

                            Surface(
                                color = if (saveToAura) Color(0xFF064E3B) else DarkSurfaceVariant,
                                shape = RoundedCornerShape(4.dp),
                                border = androidx.compose.foundation.BorderStroke(1.dp, if (saveToAura) Color(0xFF059669) else DarkOutline)
                            ) {
                                Text(
                                    text = if (saveToAura) "AURA DB READY" else "LOCAL ONLY",
                                    color = if (saveToAura) Color(0xFF34D399) else Color(0xFF94A3B8),
                                    fontSize = 9.sp,
                                    fontFamily = FontFamily.Monospace,
                                    fontWeight = FontWeight.Bold,
                                    modifier = Modifier.padding(horizontal = 6.dp, vertical = 3.dp)
                                )
                            }
                        }
                    }
                }

                // Workspace Identity Fields
                OutlinedTextField(
                    value = name,
                    onValueChange = { name = it },
                    label = { Text("App Workspace Name", color = Color.Gray) },
                    placeholder = { Text("e.g. AI Executive Strategy", color = Color.DarkGray) },
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
                    label = { Text("Strategic Focus Description", color = Color.Gray) },
                    placeholder = { Text("Isolated multimodal knowledge graph for executive AI engineering...", color = Color.DarkGray) },
                    maxLines = 2,
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedTextColor = DarkOnBackground,
                        unfocusedTextColor = DarkOnBackground,
                        focusedBorderColor = VlkgPrimary,
                        unfocusedBorderColor = DarkOutline
                    ),
                    modifier = Modifier.fillMaxWidth()
                )

                // ── Color Scheme Selector (Bi-Color vs Tri-Color) ──
                Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                    Text(
                        text = "MIXED COLOR SCHEMES",
                        color = Color.White,
                        fontSize = 11.sp,
                        fontFamily = FontFamily.Monospace,
                        fontWeight = FontWeight.Bold
                    )

                    // Tab bar
                    TabRow(
                        selectedTabIndex = selectedTab,
                        containerColor = DarkBackground,
                        contentColor = VlkgPrimary,
                        divider = {}
                    ) {
                        Tab(
                            selected = selectedTab == 0,
                            onClick = { 
                                selectedTab = 0 
                                val first = BI_COLOR_PRESETS.first()
                                selectedSchemeId = first.id
                                selectedColors = first.colors
                                if (selectedPattern == "stripe-tri" || selectedPattern == "gradient-tri") {
                                    selectedPattern = "gradient-bi"
                                }
                            },
                            text = { Text("Bi-Color (2-Color Mix)", fontSize = 11.sp, fontWeight = FontWeight.Bold) }
                        )
                        Tab(
                            selected = selectedTab == 1,
                            onClick = { 
                                selectedTab = 1 
                                val first = TRI_COLOR_PRESETS.first()
                                selectedSchemeId = first.id
                                selectedColors = first.colors
                                if (selectedPattern == "gradient-bi") {
                                    selectedPattern = "gradient-tri"
                                }
                            },
                            text = { Text("Tri-Color (3-Color Mix)", fontSize = 11.sp, fontWeight = FontWeight.Bold) }
                        )
                    }

                    // Scheme cards list
                    val currentPresets = if (selectedTab == 0) BI_COLOR_PRESETS else TRI_COLOR_PRESETS
                    Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                        currentPresets.forEach { preset ->
                            val isSelected = selectedSchemeId == preset.id
                            Surface(
                                color = if (isSelected) DarkSurfaceVariant else DarkBackground,
                                shape = RoundedCornerShape(8.dp),
                                border = androidx.compose.foundation.BorderStroke(
                                    1.dp,
                                    if (isSelected) VlkgPrimary else DarkOutline
                                ),
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .clickable {
                                        selectedSchemeId = preset.id
                                        selectedColors = preset.colors
                                    }
                            ) {
                                Row(
                                    modifier = Modifier.padding(8.dp),
                                    verticalAlignment = Alignment.CenterVertically,
                                    horizontalArrangement = Arrangement.SpaceBetween
                                ) {
                                    Row(verticalAlignment = Alignment.CenterVertically) {
                                        // Color preview strip
                                        Row(
                                            modifier = Modifier
                                                .width(48.dp)
                                                .height(18.dp)
                                                .clip(RoundedCornerShape(4.dp))
                                                .border(1.dp, Color(0xFF334155), RoundedCornerShape(4.dp))
                                        ) {
                                            preset.colors.forEach { hex ->
                                                Box(
                                                    modifier = Modifier
                                                        .weight(1f)
                                                        .fillMaxHeight()
                                                        .background(parseHexColor(hex))
                                                )
                                            }
                                        }
                                        Spacer(modifier = Modifier.width(10.dp))
                                        Column {
                                            Text(
                                                text = preset.name,
                                                color = if (isSelected) Color.White else DarkOnBackground,
                                                fontSize = 12.sp,
                                                fontWeight = FontWeight.Bold
                                            )
                                            Text(
                                                text = preset.description,
                                                color = Color(0xFF94A3B8),
                                                fontSize = 10.sp
                                            )
                                        }
                                    }

                                    if (isSelected) {
                                        Surface(
                                            color = VlkgPrimary.copy(alpha = 0.2f),
                                            shape = RoundedCornerShape(4.dp)
                                        ) {
                                            Text(
                                                text = "SELECTED",
                                                color = VlkgPrimary,
                                                fontSize = 9.sp,
                                                fontFamily = FontFamily.Monospace,
                                                fontWeight = FontWeight.Bold,
                                                modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                                            )
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                // ── Pattern Geometry Selector ──
                Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                    Text(
                        text = "GEOMETRIC PATTERNS",
                        color = Color.White,
                        fontSize = 11.sp,
                        fontFamily = FontFamily.Monospace,
                        fontWeight = FontWeight.Bold
                    )

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(6.dp)
                    ) {
                        PATTERN_MODES.forEach { pattern ->
                            val isSelected = selectedPattern == pattern.id
                            Surface(
                                color = if (isSelected) VlkgPrimary.copy(alpha = 0.15f) else DarkBackground,
                                shape = RoundedCornerShape(6.dp),
                                border = androidx.compose.foundation.BorderStroke(
                                    1.dp,
                                    if (isSelected) VlkgPrimary else DarkOutline
                                ),
                                modifier = Modifier
                                    .weight(1f)
                                    .clickable { selectedPattern = pattern.id }
                            ) {
                                Column(
                                    modifier = Modifier.padding(6.dp),
                                    horizontalAlignment = Alignment.CenterHorizontally
                                ) {
                                    Box(
                                        modifier = Modifier
                                            .size(16.dp)
                                            .clip(CircleShape)
                                            .background(getPatternBrush(pattern.id, selectedColors.map { parseHexColor(it) }))
                                    )
                                    Spacer(modifier = Modifier.height(4.dp))
                                    Text(
                                        text = pattern.name.substringBefore(" "),
                                        color = if (isSelected) Color.White else Color(0xFF94A3B8),
                                        fontSize = 9.sp,
                                        fontWeight = FontWeight.SemiBold,
                                        fontFamily = FontFamily.Monospace
                                    )
                                }
                            }
                        }
                    }
                }

                // ── Neo4j Aura DB Cloud Persistence Toggle ──
                Surface(
                    color = DarkBackground,
                    shape = RoundedCornerShape(8.dp),
                    border = androidx.compose.foundation.BorderStroke(
                        1.dp,
                        if (saveToAura) Color(0xFF059669) else DarkOutline
                    ),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clickable { saveToAura = !saveToAura }
                            .padding(10.dp),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Column(modifier = Modifier.weight(1f)) {
                            Text(
                                text = "Save Child App to Neo4j Aura DB",
                                color = Color.White,
                                fontSize = 12.sp,
                                fontWeight = FontWeight.Bold
                            )
                            Text(
                                text = "Persists (:ChildApp) node, scheme, patterns, and video relations to cloud graph",
                                color = Color(0xFF94A3B8),
                                fontSize = 10.sp
                            )
                        }
                        Checkbox(
                            checked = saveToAura,
                            onCheckedChange = { saveToAura = it },
                            colors = CheckboxDefaults.colors(
                                checkedColor = Color(0xFF10B981),
                                checkmarkColor = Color.White
                            )
                        )
                    }
                }

                // Focus Intelligence Domains
                Text(
                    text = "FOCUS INTELLIGENCE DOMAINS",
                    color = Color.White,
                    fontSize = 11.sp,
                    fontFamily = FontFamily.Monospace,
                    fontWeight = FontWeight.Bold
                )
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
                        onCreate(
                            name,
                            desc,
                            selectedSchemeId,
                            selectedPattern,
                            selectedColors,
                            selectedDomains.toList(),
                            saveToAura
                        )
                    }
                },
                enabled = name.isNotBlank(),
                colors = ButtonDefaults.buttonColors(containerColor = VlkgPrimary),
                shape = RoundedCornerShape(8.dp)
            ) {
                Text(if (editingApp != null) "Save Changes" else "Create App Workspace", fontWeight = FontWeight.Bold)
            }
        },
        dismissButton = {
            TextButton(onClick = onClose) {
                Text("Cancel", color = Color.Gray)
            }
        }
    )
}