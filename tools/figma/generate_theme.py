#!/usr/bin/env python3
"""Generate Compose theme files (Color.kt, Theme.kt, Type.kt) from a normalized UI schema.

Reads the schema's `tokens.palette` and `tokens.typography` and writes Kotlin
source files that match the Figma design rather than default Material purple/pink.

Usage:
  python3 tools/figma/generate_theme.py \
    --schema app/src/main/assets/ui-schema/login_ui_schema.json \
    --theme-dir app/src/main/java/com/mh/aiecosystemsample/core/theme \
    --package com.mh.aiecosystemsample.core.theme
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def hex_to_argb(hex_color: str) -> str:
    """Convert '#RRGGBB' or '#RRGGBBAA' to '0xFFRRGGBB' format."""
    h = hex_color.lstrip("#")
    if len(h) == 6:
        return f"0xFF{h.upper()}"
    elif len(h) == 8:
        # Figma uses RRGGBBAA, Android uses AARRGGBB
        return f"0x{h[6:8].upper()}{h[0:6].upper()}"
    return f"0xFF{h.upper()}"


def _is_light(hex_color: str) -> bool:
    """Rough luminance check — True if color is light."""
    h = hex_color.lstrip("#")[:6]
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return luminance > 0.5


def _sanitize_name(name: str) -> str:
    """Turn a hex color into a valid Kotlin val name."""
    return name.lstrip("#").upper()


def generate_color_kt(palette: list[dict[str, Any]], background: str | None, package: str) -> str:
    """Generate Color.kt with Figma palette colors."""
    lines = [
        f"package {package}",
        "",
        "import androidx.compose.ui.graphics.Color",
        "",
        "// ── Figma Design Tokens ──",
        "// Auto-generated from UI schema palette. Do not edit manually.",
        "",
    ]

    # Assign semantic names based on usage order
    semantic_names = [
        ("FigmaPrimary", "Most used color → primary"),
        ("FigmaSecondary", "Second most used → secondary"),
        ("FigmaTertiary", "Third most used → tertiary"),
        ("FigmaAccent1", "Accent color 1"),
        ("FigmaAccent2", "Accent color 2"),
        ("FigmaAccent3", "Accent color 3"),
    ]

    for i, entry in enumerate(palette[:10]):
        hex_val = entry["hex"]
        argb = hex_to_argb(hex_val)
        count = entry.get("usageCount", 0)
        if i < len(semantic_names):
            name, comment = semantic_names[i]
            lines.append(f"val {name} = Color({argb}) // {hex_val} (used {count}x) — {comment}")
        else:
            lines.append(f"val FigmaColor{i} = Color({argb}) // {hex_val} (used {count}x)")

    lines.append("")

    # Background color
    if background:
        lines.append(f"val FigmaBackground = Color({hex_to_argb(background)}) // {background}")
    else:
        lines.append("val FigmaBackground = Color(0xFFFFFFFF) // default white")

    # On-colors (auto-derived)
    lines.append("")
    lines.append("// ── Derived on-colors ──")
    if palette:
        primary_hex = palette[0]["hex"]
        on_primary = "0xFF000000" if _is_light(primary_hex) else "0xFFFFFFFF"
        lines.append(f"val FigmaOnPrimary = Color({on_primary})")
    else:
        lines.append("val FigmaOnPrimary = Color(0xFFFFFFFF)")

    if background:
        on_bg = "0xFF000000" if _is_light(background) else "0xFFFFFFFF"
        lines.append(f"val FigmaOnBackground = Color({on_bg})")
    else:
        lines.append("val FigmaOnBackground = Color(0xFF000000)")

    lines.append("val FigmaOnSurface = FigmaOnBackground")
    lines.append("")

    return "\n".join(lines) + "\n"


def generate_theme_kt(palette: list[dict[str, Any]], background: str | None, package: str, theme_name: str = "AIEcosystemPocTheme") -> str:
    """Generate Theme.kt that uses Figma palette colors."""
    lines = [
        f"package {package}",
        "",
        "import android.os.Build",
        "import androidx.compose.foundation.isSystemInDarkTheme",
        "import androidx.compose.material3.MaterialTheme",
        "import androidx.compose.material3.darkColorScheme",
        "import androidx.compose.material3.lightColorScheme",
        "import androidx.compose.runtime.Composable",
        "",
        "// ── Figma-derived color schemes ──",
        "// Auto-generated from UI schema. Do not edit manually.",
        "",
    ]

    has_colors = len(palette) >= 1

    # Light scheme
    lines.append("private val LightColorScheme = lightColorScheme(")
    if has_colors:
        lines.append(f"    primary = FigmaPrimary,")
        lines.append(f"    onPrimary = FigmaOnPrimary,")
        if len(palette) >= 2:
            lines.append(f"    secondary = FigmaSecondary,")
        if len(palette) >= 3:
            lines.append(f"    tertiary = FigmaTertiary,")
        lines.append(f"    background = FigmaBackground,")
        lines.append(f"    surface = FigmaBackground,")
        lines.append(f"    onBackground = FigmaOnBackground,")
        lines.append(f"    onSurface = FigmaOnSurface,")
    lines.append(")")
    lines.append("")

    # Dark scheme — same primary but keep readable
    lines.append("private val DarkColorScheme = darkColorScheme(")
    if has_colors:
        lines.append(f"    primary = FigmaPrimary,")
        lines.append(f"    onPrimary = FigmaOnPrimary,")
        if len(palette) >= 2:
            lines.append(f"    secondary = FigmaSecondary,")
        if len(palette) >= 3:
            lines.append(f"    tertiary = FigmaTertiary,")
    lines.append(")")
    lines.append("")

    # Theme composable — dynamicColor=false so Figma colors are always used
    lines.append("@Composable")
    lines.append(f"fun {theme_name}(")
    lines.append("    darkTheme: Boolean = isSystemInDarkTheme(),")
    lines.append("    dynamicColor: Boolean = false, // Disabled: use Figma design colors")
    lines.append("    content: @Composable () -> Unit")
    lines.append(") {")
    lines.append("    val colorScheme = when {")
    lines.append("        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {")
    lines.append("            val context = androidx.compose.ui.platform.LocalContext.current")
    lines.append("            if (darkTheme) androidx.compose.material3.dynamicDarkColorScheme(context)")
    lines.append("            else androidx.compose.material3.dynamicLightColorScheme(context)")
    lines.append("        }")
    lines.append("        darkTheme -> DarkColorScheme")
    lines.append("        else -> LightColorScheme")
    lines.append("    }")
    lines.append("")
    lines.append("    MaterialTheme(")
    lines.append("        colorScheme = colorScheme,")
    lines.append("        typography = Typography,")
    lines.append("        content = content")
    lines.append("    )")
    lines.append("}")
    lines.append("")

    return "\n".join(lines) + "\n"


def generate_type_kt(typography: list[dict[str, Any]], package: str) -> str:
    """Generate Type.kt from Figma typography tokens."""
    lines = [
        f"package {package}",
        "",
        "import androidx.compose.material3.Typography",
        "import androidx.compose.ui.text.TextStyle",
        "import androidx.compose.ui.text.font.FontFamily",
        "import androidx.compose.ui.text.font.FontWeight",
        "import androidx.compose.ui.unit.sp",
        "",
        "// ── Figma-derived typography ──",
        "// Auto-generated from UI schema. Do not edit manually.",
        "",
    ]

    # Map Figma weights to Compose FontWeight
    def _fw(w: int | None) -> str:
        if not w:
            return "FontWeight.Normal"
        mapping = {
            100: "FontWeight.Thin", 200: "FontWeight.ExtraLight",
            300: "FontWeight.Light", 400: "FontWeight.Normal",
            500: "FontWeight.Medium", 600: "FontWeight.SemiBold",
            700: "FontWeight.Bold", 800: "FontWeight.ExtraBold",
            900: "FontWeight.Black",
        }
        return mapping.get(w, f"FontWeight(weight = {w})")

    # Map sorted fonts to Material typography slots
    # Index 0 = largest font → headlineLarge, etc.
    slots = [
        ("headlineLarge", "Largest text"),
        ("headlineMedium", ""),
        ("headlineSmall", ""),
        ("titleLarge", ""),
        ("titleMedium", ""),
        ("bodyLarge", ""),
        ("bodyMedium", ""),
        ("bodySmall", ""),
        ("labelLarge", ""),
        ("labelMedium", ""),
        ("labelSmall", "Smallest text"),
    ]

    lines.append("val Typography = Typography(")
    for i, font_entry in enumerate(typography[:len(slots)]):
        slot_name, comment = slots[i]
        size = font_entry.get("fontSize", 16)
        weight = font_entry.get("fontWeight")
        lh = font_entry.get("lineHeightPx")
        comma = "," if i < min(len(typography), len(slots)) - 1 else ""

        lh_line = f"lineHeight = {lh:.1f}.sp, " if lh else ""
        lines.append(f"    {slot_name} = TextStyle(")
        lines.append(f"        fontFamily = FontFamily.Default,")
        lines.append(f"        fontWeight = {_fw(weight)},")
        lines.append(f"        fontSize = {size:.1f}.sp,")
        if lh:
            lines.append(f"        lineHeight = {lh:.1f}.sp,")
        lines.append(f"    ){comma}")

    lines.append(")")
    lines.append("")

    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Compose theme from UI schema")
    parser.add_argument("--schema", required=True, help="Path to normalized UI schema JSON")
    parser.add_argument("--theme-dir", required=True, help="Target directory for theme files")
    parser.add_argument("--package", required=True, help="Kotlin package name")
    parser.add_argument("--skip-type", action="store_true", help="Skip Type.kt generation")
    parser.add_argument("--theme-name", default="AIEcosystemPocTheme", help="Name of the theme composable function")
    args = parser.parse_args()

    schema = json.loads(Path(args.schema).read_text(encoding="utf-8"))
    tokens = schema.get("tokens", {})
    palette = tokens.get("palette", [])
    typography = tokens.get("typography", [])
    background = schema.get("layout", {}).get("backgroundColor")

    out_dir = Path(args.theme_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Color.kt
    color_kt = generate_color_kt(palette, background, args.package)
    (out_dir / "Color.kt").write_text(color_kt, encoding="utf-8")
    print(f"✅  Wrote Color.kt → {out_dir / 'Color.kt'}")
    print(f"    Palette entries: {len(palette)}")

    # Theme.kt
    theme_kt = generate_theme_kt(palette, background, args.package, args.theme_name)
    (out_dir / "Theme.kt").write_text(theme_kt, encoding="utf-8")
    print(f"✅  Wrote Theme.kt → {out_dir / 'Theme.kt'}")

    # Type.kt
    if not args.skip_type and typography:
        type_kt = generate_type_kt(typography, args.package)
        (out_dir / "Type.kt").write_text(type_kt, encoding="utf-8")
        print(f"✅  Wrote Type.kt → {out_dir / 'Type.kt'}")
        print(f"    Typography entries: {len(typography)}")
    else:
        print("⏭️  Skipped Type.kt (no typography tokens or --skip-type)")

    print("\n🎨 Theme files generated from Figma design tokens!")
    print("   Colors will now match the Figma design exactly.")


if __name__ == "__main__":
    main()

