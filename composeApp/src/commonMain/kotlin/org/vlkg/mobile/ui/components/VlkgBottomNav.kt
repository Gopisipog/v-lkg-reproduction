package org.vlkg.mobile.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import org.vlkg.mobile.theme.*
import org.vlkg.mobile.viewmodel.AppNavigationTab

@Composable
fun VlkgBottomNav(
    activeTab: AppNavigationTab,
    onTabChange: (AppNavigationTab) -> Unit,
    modifier: Modifier = Modifier
) {
    val appTheme = LocalVlkgAppTheme.current
    val primaryColor = MaterialTheme.colorScheme.primary

    Surface(
        color = DarkBackground,
        contentColor = DarkOnBackground,
        modifier = modifier
            .fillMaxWidth()
            .border(width = 1.dp, color = DarkOutline)
    ) {
        Column(modifier = Modifier.fillMaxWidth()) {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(2.dp)
                    .background(appTheme.brush)
            )
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 8.dp, vertical = 6.dp),
                horizontalArrangement = Arrangement.SpaceAround,
                verticalAlignment = Alignment.CenterVertically
            ) {
                AppNavigationTab.values().forEach { tab ->
                    val selected = activeTab == tab
                    Surface(
                        onClick = { onTabChange(tab) },
                        shape = RoundedCornerShape(8.dp),
                        color = if (selected) primaryColor.copy(alpha = 0.16f) else Color.Transparent,
                        border = if (selected) androidx.compose.foundation.BorderStroke(1.dp, primaryColor.copy(alpha = 0.5f)) else null,
                        modifier = Modifier.padding(horizontal = 2.dp)
                    ) {
                        Column(
                            horizontalAlignment = Alignment.CenterHorizontally,
                            verticalArrangement = Arrangement.Center,
                            modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp)
                        ) {
                            Text(
                                text = tab.code,
                                fontSize = 11.sp,
                                fontFamily = FontFamily.Monospace,
                                fontWeight = if (selected) FontWeight.Bold else FontWeight.Medium,
                                color = if (selected) primaryColor else Color(0xFF64748B)
                            )
                            Spacer(modifier = Modifier.height(2.dp))
                            Text(
                                text = tab.label.uppercase(),
                                fontSize = 9.sp,
                                fontFamily = FontFamily.Monospace,
                                fontWeight = FontWeight.SemiBold,
                                color = if (selected) DarkOnBackground else Color(0xFF94A3B8)
                            )
                        }
                    }
                }
            }
        }
    }
}