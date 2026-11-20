package com.asjohn720.s1mods.ui.screens

import android.widget.Toast
import androidx.compose.animation.*
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.asjohn720.s1mods.model.ScooterManager
import com.asjohn720.s1mods.ui.theme.*
import kotlin.math.abs
import kotlinx.coroutines.launch

@Composable
fun DashboardStudioScreen(manager: ScooterManager) {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()
    val scrollState = rememberScrollState()

    val isConnected by manager.isConnected.collectAsState()
    val uiConfig by manager.dashboardUi.collectAsState()

    var isRefreshing by remember { mutableStateOf(false) }
    var activeAction by remember { mutableStateOf<String?>(null) }

    // Local editing state for sliders
    var selectedDpi by remember { mutableStateOf(uiConfig.currentDpi) }
    var selectedFontScale by remember { mutableStateOf(uiConfig.fontScale) }
    var selectedAnimScale by remember { mutableStateOf(uiConfig.animationScale) }
    var isNightMode by remember { mutableStateOf(uiConfig.isNightMode) }

    LaunchedEffect(uiConfig) {
        selectedDpi = uiConfig.currentDpi
        selectedFontScale = uiConfig.fontScale
        selectedAnimScale = uiConfig.animationScale
        isNightMode = uiConfig.isNightMode
    }

    LaunchedEffect(isConnected) {
        if (isConnected) {
            isRefreshing = true
            try {
                manager.fetchDashboardUiSettings()
            } catch (_: Exception) {}
            isRefreshing = false
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(BgDark)
            .verticalScroll(scrollState)
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // Studio Header
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column {
                Text(
                    text = "Dashboard Studio",
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold,
                    color = TextPrimary
                )
                Text(
                    text = "Customize MoveOS 7\" display scaling & performance",
                    fontSize = 12.sp,
                    color = TextSecondary
                )
            }

            IconButton(
                onClick = {
                    coroutineScope.launch {
                        isRefreshing = true
                        try {
                            manager.fetchDashboardUiSettings()
                            Toast.makeText(context, "Settings reloaded", Toast.LENGTH_SHORT).show()
                        } catch (e: Exception) {
                            Toast.makeText(context, "Error: ${e.message}", Toast.LENGTH_SHORT).show()
                        } finally {
                            isRefreshing = false
                        }
                    }
                },
                enabled = isConnected && !isRefreshing
            ) {
                if (isRefreshing) {
                    CircularProgressIndicator(modifier = Modifier.size(16.dp), color = AccentCyan, strokeWidth = 2.dp)
                } else {
                    Icon(Icons.Default.Refresh, contentDescription = "Reload", tint = if (isConnected) AccentCyan else TextMuted)
                }
            }
        }

        // Live Simulated 7" Dashboard Preview Card
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .border(1.dp, CardBorder, RoundedCornerShape(14.dp)),
            colors = CardDefaults.cardColors(containerColor = SurfaceDark),
            shape = RoundedCornerShape(14.dp)
        ) {
            Column(modifier = Modifier.padding(14.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Default.Tv, contentDescription = null, tint = AccentCyan, modifier = Modifier.size(16.dp))
                        Spacer(modifier = Modifier.width(8.dp))
                        Text("Live Display Preview", fontSize = 12.sp, fontWeight = FontWeight.SemiBold, color = TextPrimary)
                    }

                    Box(
                        modifier = Modifier
                            .clip(RoundedCornerShape(6.dp))
                            .background(AccentCyanSubtle)
                            .padding(horizontal = 8.dp, vertical = 2.dp)
                    ) {
                        Text("${selectedDpi} DPI • ${selectedFontScale}x", fontSize = 10.sp, fontFamily = FontFamily.Monospace, color = AccentCyan, fontWeight = FontWeight.Bold)
                    }
                }

                Spacer(modifier = Modifier.height(12.dp))

                // Simulated 7" (16:9) Touchscreen Aspect
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(120.dp)
                        .clip(RoundedCornerShape(10.dp))
                        .background(Color(0xFF07080A))
                        .border(1.dp, CardBorder, RoundedCornerShape(10.dp))
                        .padding(10.dp),
                    contentAlignment = Alignment.Center
                ) {
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.Center
                    ) {
                        // Simulated speedometer scale
                        val speedFontSize = (32 * (selectedFontScale * (selectedDpi / 200f))).coerceIn(20f, 44f).sp
                        Text(
                            text = "42",
                            fontSize = speedFontSize,
                            fontWeight = FontWeight.Bold,
                            color = AccentCyan,
                            fontFamily = FontFamily.Monospace
                        )
                        Text(
                            text = "KM/H • NORMAL MODE",
                            fontSize = (9 * selectedFontScale).coerceIn(7f, 13f).sp,
                            color = TextSecondary,
                            fontWeight = FontWeight.Medium
                        )
                    }

                    // Floating ball mock
                    Box(
                        modifier = Modifier
                            .size(24.dp)
                            .align(Alignment.CenterEnd)
                            .clip(CircleShape)
                            .background(Color(0x88222836))
                            .border(1.dp, AccentCyan, CircleShape),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(Icons.Default.Navigation, contentDescription = null, tint = Color.White, modifier = Modifier.size(12.dp))
                    }
                }
            }
        }

        // 1. Interface Density / DPI Scaling Card
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .border(1.dp, CardBorder, RoundedCornerShape(14.dp)),
            colors = CardDefaults.cardColors(containerColor = SurfaceDark),
            shape = RoundedCornerShape(14.dp)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Default.AspectRatio, contentDescription = null, tint = AccentCyan, modifier = Modifier.size(18.dp))
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Display Density (DPI Scale)", fontSize = 14.sp, fontWeight = FontWeight.SemiBold, color = TextPrimary)
                }
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = "Controls how compact or large icons and touch targets appear on the 7\" screen.",
                    fontSize = 11.sp,
                    color = TextSecondary
                )

                Spacer(modifier = Modifier.height(14.dp))

                // Presets Grid
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    DpiPresetChip("Compact", 175, selectedDpi) { selectedDpi = it }
                    DpiPresetChip("Balanced", 195, selectedDpi) { selectedDpi = it }
                    DpiPresetChip("Stock", 213, selectedDpi) { selectedDpi = it }
                    DpiPresetChip("Large", 240, selectedDpi) { selectedDpi = it }
                }

                Spacer(modifier = Modifier.height(14.dp))

                // Slider with Apply / Reset
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text("Value: ${selectedDpi} DPI", fontSize = 12.sp, color = TextPrimary, fontFamily = FontFamily.Monospace)

                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        OutlinedButton(
                            onClick = {
                                coroutineScope.launch {
                                    activeAction = "reset_dpi"
                                    manager.resetDensity()
                                    Toast.makeText(context, "Density reset to stock", Toast.LENGTH_SHORT).show()
                                    activeAction = null
                                }
                            },
                            enabled = isConnected && activeAction == null,
                            shape = RoundedCornerShape(8.dp),
                            contentPadding = PaddingValues(horizontal = 10.dp, vertical = 6.dp)
                        ) {
                            Text("Reset", fontSize = 11.sp)
                        }

                        Button(
                            onClick = {
                                coroutineScope.launch {
                                    activeAction = "apply_dpi"
                                    val ok = manager.applyDensity(selectedDpi)
                                    if (ok) Toast.makeText(context, "Density updated to ${selectedDpi} DPI", Toast.LENGTH_SHORT).show()
                                    activeAction = null
                                }
                            },
                            enabled = isConnected && activeAction == null,
                            shape = RoundedCornerShape(8.dp),
                            colors = ButtonDefaults.buttonColors(containerColor = AccentCyan, contentColor = BgDark),
                            contentPadding = PaddingValues(horizontal = 14.dp, vertical = 6.dp)
                        ) {
                            if (activeAction == "apply_dpi") {
                                CircularProgressIndicator(modifier = Modifier.size(12.dp), color = BgDark, strokeWidth = 2.dp)
                            } else {
                                Text("Apply", fontSize = 11.sp, fontWeight = FontWeight.Bold)
                            }
                        }
                    }
                }
            }
        }

        // 2. HMI Performance Acceleration (Animations)
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .border(1.dp, CardBorder, RoundedCornerShape(14.dp)),
            colors = CardDefaults.cardColors(containerColor = SurfaceDark),
            shape = RoundedCornerShape(14.dp)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Default.Speed, contentDescription = null, tint = AccentEmerald, modifier = Modifier.size(18.dp))
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("UI Responsiveness (Animation Speed)", fontSize = 14.sp, fontWeight = FontWeight.SemiBold, color = TextPrimary)
                }
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = "Reduces UI animation duration to eliminate lag and make the dashboard feel instant.",
                    fontSize = 11.sp,
                    color = TextSecondary
                )

                Spacer(modifier = Modifier.height(14.dp))

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    AnimSpeedButton("⚡ Instant (0x)", 0.0f, selectedAnimScale, Modifier.weight(1f)) {
                        selectedAnimScale = it
                        coroutineScope.launch { manager.applyAnimationScale(it) }
                    }
                    AnimSpeedButton("🏎️ Fast (0.5x)", 0.5f, selectedAnimScale, Modifier.weight(1f)) {
                        selectedAnimScale = it
                        coroutineScope.launch { manager.applyAnimationScale(it) }
                    }
                    AnimSpeedButton("⏱️ Stock (1.0x)", 1.0f, selectedAnimScale, Modifier.weight(1f)) {
                        selectedAnimScale = it
                        coroutineScope.launch { manager.applyAnimationScale(it) }
                    }
                }
            }
        }

        // 3. System Font Scaling
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .border(1.dp, CardBorder, RoundedCornerShape(14.dp)),
            colors = CardDefaults.cardColors(containerColor = SurfaceDark),
            shape = RoundedCornerShape(14.dp)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Default.TextFields, contentDescription = null, tint = AccentAmber, modifier = Modifier.size(18.dp))
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Font Size Scaling", fontSize = 14.sp, fontWeight = FontWeight.SemiBold, color = TextPrimary)
                }
                Spacer(modifier = Modifier.height(12.dp))

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    FontScaleChip("Small (0.85x)", 0.85f, selectedFontScale, Modifier.weight(1f)) {
                        selectedFontScale = it
                        coroutineScope.launch { manager.applyFontScale(it) }
                    }
                    FontScaleChip("Normal (1.0x)", 1.0f, selectedFontScale, Modifier.weight(1f)) {
                        selectedFontScale = it
                        coroutineScope.launch { manager.applyFontScale(it) }
                    }
                    FontScaleChip("Large (1.15x)", 1.15f, selectedFontScale, Modifier.weight(1f)) {
                        selectedFontScale = it
                        coroutineScope.launch { manager.applyFontScale(it) }
                    }
                }
            }
        }

        // 4. Quick Toggles: Night Mode & Screen Timeout
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .border(1.dp, CardBorder, RoundedCornerShape(14.dp)),
            colors = CardDefaults.cardColors(containerColor = SurfaceDark),
            shape = RoundedCornerShape(14.dp)
        ) {
            Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(14.dp)) {
                // Night mode row
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text("Dark Mode Override", fontSize = 13.sp, fontWeight = FontWeight.Medium, color = TextPrimary)
                        Text("Forces dark theme across sideloaded apps", fontSize = 11.sp, color = TextSecondary)
                    }

                    Switch(
                        checked = isNightMode,
                        onCheckedChange = {
                            isNightMode = it
                            coroutineScope.launch { manager.applyNightMode(it) }
                        },
                        colors = SwitchDefaults.colors(
                            checkedThumbColor = Color.White,
                            checkedTrackColor = AccentCyan,
                            uncheckedTrackColor = SurfaceVariantDark
                        )
                    )
                }

                HorizontalDivider(color = DividerColor)

                // Screen Timeout Row
                Column {
                    Text("Auto-Sleep Timeout", fontSize = 13.sp, fontWeight = FontWeight.Medium, color = TextPrimary)
                    Spacer(modifier = Modifier.height(8.dp))
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(6.dp)
                    ) {
                        TimeoutChip("1m", 60000, uiConfig.screenTimeoutMs) { coroutineScope.launch { manager.applyScreenTimeout(it) } }
                        TimeoutChip("2m (Stock)", 120000, uiConfig.screenTimeoutMs) { coroutineScope.launch { manager.applyScreenTimeout(it) } }
                        TimeoutChip("5m", 300000, uiConfig.screenTimeoutMs) { coroutineScope.launch { manager.applyScreenTimeout(it) } }
                        TimeoutChip("10m", 600000, uiConfig.screenTimeoutMs) { coroutineScope.launch { manager.applyScreenTimeout(it) } }
                    }
                }
            }
        }

        // 5. Utility Actions: Soft Restart HMI & Restore Defaults
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            OutlinedButton(
                onClick = {
                    coroutineScope.launch {
                        manager.restartHmi()
                        Toast.makeText(context, "Restarting speedometer HMI...", Toast.LENGTH_SHORT).show()
                    }
                },
                modifier = Modifier.weight(1f).height(44.dp),
                shape = RoundedCornerShape(10.dp),
                border = androidx.compose.foundation.BorderStroke(1.dp, CardBorder)
            ) {
                Icon(Icons.Default.Refresh, contentDescription = null, modifier = Modifier.size(14.dp), tint = TextSecondary)
                Spacer(modifier = Modifier.width(6.dp))
                Text("Restart HMI", fontSize = 12.sp, color = TextPrimary)
            }

            Button(
                onClick = {
                    coroutineScope.launch {
                        manager.resetAllUiSettings()
                        Toast.makeText(context, "Restored all stock defaults", Toast.LENGTH_SHORT).show()
                    }
                },
                modifier = Modifier.weight(1f).height(44.dp),
                shape = RoundedCornerShape(10.dp),
                colors = ButtonDefaults.buttonColors(containerColor = SurfaceVariantDark, contentColor = StatusWarning)
            ) {
                Icon(Icons.Default.Restore, contentDescription = null, modifier = Modifier.size(14.dp))
                Spacer(modifier = Modifier.width(6.dp))
                Text("Reset Defaults", fontSize = 12.sp, fontWeight = FontWeight.SemiBold)
            }
        }
    }
}

@Composable
fun DpiPresetChip(label: String, dpi: Int, currentDpi: Int, onSelect: (Int) -> Unit) {
    val isSelected = dpi == currentDpi
    Box(
        modifier = Modifier
            .clip(RoundedCornerShape(8.dp))
            .background(if (isSelected) AccentCyanSubtle else SurfaceVariantDark)
            .border(1.dp, if (isSelected) AccentCyan else CardBorder, RoundedCornerShape(8.dp))
            .clickable { onSelect(dpi) }
            .padding(horizontal = 10.dp, vertical = 6.dp),
        contentAlignment = Alignment.Center
    ) {
        Text(
            text = "$label ($dpi)",
            fontSize = 11.sp,
            fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Normal,
            color = if (isSelected) AccentCyan else TextSecondary
        )
    }
}

@Composable
fun AnimSpeedButton(label: String, scale: Float, currentScale: Float, modifier: Modifier = Modifier, onSelect: (Float) -> Unit) {
    val isSelected = abs(scale - currentScale) < 0.05f
    Box(
        modifier = modifier
            .clip(RoundedCornerShape(8.dp))
            .background(if (isSelected) AccentEmeraldSubtle else SurfaceVariantDark)
            .border(1.dp, if (isSelected) AccentEmerald else CardBorder, RoundedCornerShape(8.dp))
            .clickable { onSelect(scale) }
            .padding(vertical = 8.dp),
        contentAlignment = Alignment.Center
    ) {
        Text(
            text = label,
            fontSize = 11.sp,
            fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Medium,
            color = if (isSelected) AccentEmerald else TextSecondary
        )
    }
}

@Composable
fun FontScaleChip(label: String, scale: Float, currentScale: Float, modifier: Modifier = Modifier, onSelect: (Float) -> Unit) {
    val isSelected = abs(scale - currentScale) < 0.05f
    Box(
        modifier = modifier
            .clip(RoundedCornerShape(8.dp))
            .background(if (isSelected) AccentAmberSubtle else SurfaceVariantDark)
            .border(1.dp, if (isSelected) AccentAmber else CardBorder, RoundedCornerShape(8.dp))
            .clickable { onSelect(scale) }
            .padding(vertical = 8.dp),
        contentAlignment = Alignment.Center
    ) {
        Text(
            text = label,
            fontSize = 11.sp,
            fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Medium,
            color = if (isSelected) AccentAmber else TextSecondary
        )
    }
}

@Composable
fun TimeoutChip(label: String, ms: Int, currentMs: Int, onSelect: (Int) -> Unit) {
    val isSelected = ms == currentMs
    Box(
        modifier = Modifier
            .clip(RoundedCornerShape(6.dp))
            .background(if (isSelected) AccentCyanSubtle else SurfaceVariantDark)
            .border(1.dp, if (isSelected) AccentCyan else CardBorder, RoundedCornerShape(6.dp))
            .clickable { onSelect(ms) }
            .padding(horizontal = 8.dp, vertical = 5.dp)
    ) {
        Text(
            text = label,
            fontSize = 11.sp,
            fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Normal,
            color = if (isSelected) AccentCyan else TextSecondary
        )
    }
}
