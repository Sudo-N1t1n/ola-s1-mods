package com.asjohn720.s1mods.ui.theme

import androidx.compose.ui.graphics.Color

// Obsidian & Precision Automotive Slate Palette
val BgDark = Color(0xFF090A0E)              // Deep obsidian backdrop
val SurfaceDark = Color(0xFF11141C)         // Primary card surface
val SurfaceVariantDark = Color(0xFF181C26)  // Elevated interactive surface
val SurfaceHighlight = Color(0xFF222836)    // Toggles, chips & borders
val CardBorder = Color(0xFF252D3D)          // Subtle hairline border
val DividerColor = Color(0xFF1C222E)

// High-End Electric Accents
val AccentCyan = Color(0xFF00D2FF)          // Electric Cyan (Primary Active & Highlights)
val AccentCyanSubtle = Color(0x1F00D2FF)
val AccentEmerald = Color(0xFF10B981)       // Verified Status & Safety Ok
val AccentEmeraldSubtle = Color(0x1F10B981)
val AccentAmber = Color(0xFFF59E0B)         // Caution & Alerts
val AccentAmberSubtle = Color(0x1FF59E0B)
val AccentRose = Color(0xFFF43F5E)          // Destructive & Critical Alerts
val AccentRoseSubtle = Color(0x1FF43F5E)

// Primary Action & Monochromatic Controls
val AccentMint = Color(0xFFEDEDED)          // Crisp white primary action
val AccentMintSubtle = Color(0x1AFFFFFF)
val AccentSky = AccentCyan
val AccentSkySubtle = AccentCyanSubtle

// Status Colors
val StatusOk = AccentEmerald
val StatusWarning = AccentAmber
val StatusDanger = AccentRose

// Refined Typography Hierarchy
val TextPrimary = Color(0xFFF3F4F6)         // Pure high-contrast white
val TextSecondary = Color(0xFF9CA3AF)       // Mid-slate description
val TextMuted = Color(0xFF64748B)           // Low-contrast captions & labels

// Terminal & Low-Level Console
val TerminalBg = Color(0xFF060709)
val TerminalBorder = Color(0xFF1E2430)

// Backward-Compatible Aliases
val ElectricGreen = StatusOk
val CyberCyan = AccentCyan
val ElectricYellow = StatusWarning
val DangerRed = StatusDanger
