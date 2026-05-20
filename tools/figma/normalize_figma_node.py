#!/usr/bin/env python3
"""Universal Figma node normalizer.

Converts ANY raw Figma node JSON into a deterministic, clean UI schema
that AI agents can directly use for Compose code generation.
No hardcoded screen names or node names — works for any frame.

Pipeline:
  Figma MCP (figma_get_node)
         ↓
  normalize_figma_node.py   ← this file
         ↓
  Clean UI Schema JSON
         ↓
  AI Designer Agent generates Compose UI

Usage:
  python3 tools/figma/normalize_figma_node.py \
    --input  /tmp/login_figma_raw.json \
    --output app/src/main/assets/ui-schema/login_ui_schema.json \
    --file-id vLcVO8YQvAu4G8QgSVtX2s
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

# ─────────────────────────────────────────────
#  Noise filters — nodes that are UI chrome,
#  not real product UI (status bars, annotations)
# ─────────────────────────────────────────────
SKIP_NAME_FRAGMENTS = [
    "Status Bar", "iPhone X/Status", "android/status",
    "Annotation", "Note", "Redline", "_guide", "_annotation",
]
SKIP_EXACT_NAMES = {"9:41"}

# ─────────────────────────────────────────────
#  Heuristic keyword maps for semantic detection
# ─────────────────────────────────────────────
TEXT_FIELD_KEYWORDS  = ["input","field","textfield","text field","holder","email",
                        "password","phone","username","search","address","name"]
PASSWORD_KEYWORDS    = ["password","pin","otp","passcode"]
BUTTON_KEYWORDS      = ["button","btn","cta","submit","login","log in","sign in",
                        "sign up","continue","next","done"]
IMAGE_KEYWORDS       = ["logo","banner","illustration","avatar","image"]
CHECKBOX_KEYWORDS    = ["checkbox","check box","toggle","switch","radio"]
DIVIDER_KEYWORDS     = ["divider","separator","line","hr"]


# ─────────────────────────────────────────────
#  Colour helpers
# ─────────────────────────────────────────────
def to_hex(color: dict[str, Any] | None) -> str | None:
    if not color:
        return None
    r = round(float(color.get("r", 0)) * 255)
    g = round(float(color.get("g", 0)) * 255)
    b = round(float(color.get("b", 0)) * 255)
    a = float(color.get("a", 1.0))
    if round(a * 255) == 255:
        return f"#{r:02X}{g:02X}{b:02X}"
    return f"#{r:02X}{g:02X}{b:02X}{round(a*255):02X}"

def first_solid_fill(node: dict[str, Any]) -> str | None:
    for f in node.get("fills", []):
        if f.get("type") == "SOLID" and f.get("visible", True) is not False:
            return to_hex(f.get("color"))
    return None

def first_solid_stroke(node: dict[str, Any]) -> str | None:
    for s in node.get("strokes", []):
        if s.get("type") == "SOLID" and s.get("visible", True) is not False:
            return to_hex(s.get("color"))
    return None

def has_image_fill(node: dict[str, Any]) -> bool:
    return any(f.get("type") == "IMAGE" for f in node.get("fills", []))


# ─────────────────────────────────────────────
#  Typography helpers
# ─────────────────────────────────────────────
def extract_typography(node: dict[str, Any]) -> dict[str, Any] | None:
    s = node.get("style")
    if not s:
        return None
    return {k: v for k, v in {
        "fontFamily":    s.get("fontFamily"),
        "fontWeight":    s.get("fontWeight"),
        "fontSize":      s.get("fontSize"),
        "lineHeightPx":  s.get("lineHeightPx"),
        "letterSpacing": s.get("letterSpacing"),
        "textAlign":     s.get("textAlignHorizontal"),
    }.items() if v is not None}

def extract_mixed_typography(node: dict[str, Any]) -> list[dict[str, Any]]:
    """Per-run overrides — e.g. first line bold, second line medium."""
    result = []
    for style_data in node.get("styleOverrideTable", {}).values():
        span = {k: v for k, v in {
            "fontFamily": style_data.get("fontFamily"),
            "fontWeight": style_data.get("fontWeight"),
            "fontSize":   style_data.get("fontSize"),
            "fontStyle":  style_data.get("fontStyle"),
        }.items() if v is not None}
        if span:
            result.append(span)
    return result


# ─────────────────────────────────────────────
#  Layout / sizing helpers
# ─────────────────────────────────────────────
def bbox_size(node: dict[str, Any]) -> dict[str, Any]:
    bb = node.get("absoluteBoundingBox", {})
    return {k: v for k, v in {"width": bb.get("width"), "height": bb.get("height")}.items() if v is not None}

def extract_auto_layout(node: dict[str, Any]) -> dict[str, Any] | None:
    mode = node.get("layoutMode")
    if not mode or mode == "NONE":
        return None
    return {k: v for k, v in {
        "direction":       "vertical" if mode == "VERTICAL" else "horizontal",
        "itemSpacing":     node.get("itemSpacing"),
        "paddingTop":      node.get("paddingTop"),
        "paddingBottom":   node.get("paddingBottom"),
        "paddingLeft":     node.get("paddingLeft"),
        "paddingRight":    node.get("paddingRight"),
        "primaryAxisAlign": node.get("primaryAxisAlignItems"),
        "counterAxisAlign": node.get("counterAxisAlignItems"),
    }.items() if v is not None}

def extract_border_radius(node: dict[str, Any]) -> int | None:
    cr = node.get("cornerRadius")
    if cr is not None:
        return int(round(cr))
    corners = node.get("rectangleCornerRadii", [])
    return int(round(max(corners))) if corners else None

def y_order(node: dict[str, Any]) -> float:
    return node.get("absoluteBoundingBox", {}).get("y", 0.0)


# ─────────────────────────────────────────────
#  Semantic detection
# ─────────────────────────────────────────────
def _norm(name: str) -> str:
    return name.lower().replace("-", " ").replace("_", " ").strip()

def _matches(name: str, kws: list[str]) -> bool:
    n = _norm(name)
    return any(kw in n for kw in kws)

def infer_type(node: dict[str, Any]) -> str | None:
    t = node.get("type", "")
    name = node.get("name", "")
    if t == "TEXT":
        return "Text"
    if t == "RECTANGLE" and has_image_fill(node):
        return "Image"
    if t in ("FRAME", "GROUP", "COMPONENT", "INSTANCE"):
        if _matches(name, BUTTON_KEYWORDS):
            return "Button"
        if _matches(name, TEXT_FIELD_KEYWORDS):
            return "TextField"
        if _matches(name, IMAGE_KEYWORDS):
            return "Image"
        if _matches(name, CHECKBOX_KEYWORDS):
            return "Checkbox"
        if _matches(name, DIVIDER_KEYWORDS):
            return "Divider"
    if t == "VECTOR" and _matches(name, ["icon", "chevron", "arrow"]):
        return "Icon"
    return None


# ─────────────────────────────────────────────
#  Noise predicate
# ─────────────────────────────────────────────
def is_noise(node: dict[str, Any]) -> bool:
    name = node.get("name", "")
    if name in SKIP_EXACT_NAMES:
        return True
    return any(frag.lower() in name.lower() for frag in SKIP_NAME_FRAGMENTS)


# ─────────────────────────────────────────────
#  Interaction extraction
# ─────────────────────────────────────────────
def extract_interactions(node: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    for ix in node.get("interactions", []):
        trigger = ix.get("trigger", {}).get("type")
        for act in ix.get("actions", []):
            entry: dict[str, Any] = {"trigger": trigger, "actionType": act.get("type")}
            if act.get("destinationId"):
                entry["destinationNodeId"] = act["destinationId"]
            if act.get("navigation"):
                entry["navigation"] = act["navigation"]
            out.append(entry)
    return out


# ─────────────────────────────────────────────
#  Recursive collector
# ─────────────────────────────────────────────
def _deep_first_text(node: dict[str, Any]) -> str:
    if node.get("type") == "TEXT":
        return node.get("characters", "").strip()
    for c in node.get("children", []):
        t = _deep_first_text(c)
        if t:
            return t
    return ""

def _deep_fill(node: dict[str, Any]) -> str | None:
    c = first_solid_fill(node)
    if c:
        return c
    for child in node.get("children", []):
        c = _deep_fill(child)
        if c:
            return c
    return None

def _deep_border_radius(node: dict[str, Any]) -> int | None:
    cr = extract_border_radius(node)
    if cr is not None:
        return cr
    for child in node.get("children", []):
        cr = _deep_border_radius(child)
        if cr is not None:
            return cr
    return None


def collect(node: dict[str, Any], out: list[dict[str, Any]], _root: bool = False) -> None:
    if is_noise(node):
        return

    # The root screen frame must never be treated as a component itself
    if _root:
        for child in sorted(node.get("children", []), key=y_order):
            collect(child, out, _root=False)
        return

    semantic = infer_type(node)

    # ── Text ──
    if semantic == "Text":
        text = node.get("characters", "").strip()
        if not text:
            return
        entry: dict[str, Any] = {"type": "Text", "id": node["id"], "name": node.get("name", "")}
        entry["text"] = text
        tc = first_solid_fill(node)
        if tc:
            entry["textColor"] = tc
        typo = extract_typography(node)
        if typo:
            entry["typography"] = typo
        mixed = extract_mixed_typography(node)
        if mixed:
            entry["mixedTypography"] = mixed
        entry.update(bbox_size(node))
        out.append(entry)
        return

    # ── Image ──
    if semantic == "Image":
        entry = {"type": "Image", "id": node["id"],
                 "name": _norm(node.get("name", "")).replace(" ", "_"),
                 "figmaNodeId": node["id"]}
        entry.update(bbox_size(node))
        # If the Image container also has text children, collect them first then add image
        text_children: list[dict[str, Any]] = []
        for child in sorted(node.get("children", []), key=y_order):
            if child.get("type") == "TEXT":
                collect(child, text_children)
        out.extend(text_children)
        out.append(entry)
        return

    # ── Button ──
    if semantic == "Button":
        entry: dict[str, Any] = {"type": "Button", "id": node["id"], "name": node.get("name", "")}
        entry["text"] = _deep_first_text(node)
        bg = _deep_fill(node)
        if bg:
            entry["backgroundColor"] = bg
        cr = _deep_border_radius(node)
        if cr is not None:
            entry["cornerRadius"] = cr
        entry.update(bbox_size(node))
        # text color from label child
        def _text_color(n: dict[str, Any]) -> str | None:
            if n.get("type") == "TEXT":
                return first_solid_fill(n)
            for c in n.get("children", []):
                tc = _text_color(c)
                if tc:
                    return tc
            return None
        tc = _text_color(node)
        if tc:
            entry["textColor"] = tc
        ixs = extract_interactions(node)
        if ixs:
            entry["interactions"] = ixs
        out.append(entry)
        return

    # ── TextField ──
    if semantic == "TextField":
        label = _deep_first_text(node) or node.get("name", "")
        entry = {
            "type": "TextField",
            "id": node["id"],
            "name": node.get("name", ""),
            "label": label,
            "isPassword": _matches(node.get("name", ""), PASSWORD_KEYWORDS),
        }
        border = first_solid_stroke(node)
        if not border:
            # check children for stroked frame
            for child in node.get("children", []):
                border = first_solid_stroke(child)
                if border:
                    break
        if border:
            entry["borderColor"] = border
        entry.update(bbox_size(node))
        auto = extract_auto_layout(node)
        if auto:
            entry["autoLayout"] = auto
        out.append(entry)
        return

    # ── Checkbox ──
    if semantic == "Checkbox":
        out.append({"type": "Checkbox", "id": node["id"], "name": node.get("name", "")})
        return

    # ── Divider ──
    if semantic == "Divider":
        entry = {"type": "Divider", "id": node["id"], "name": node.get("name", "")}
        fill = first_solid_fill(node)
        if fill:
            entry["color"] = fill
        entry.update(bbox_size(node))
        out.append(entry)
        return

    # ── Container: recurse, children sorted top-to-bottom ──
    for child in sorted(node.get("children", []), key=y_order):
        collect(child, out, _root=False)


# ─────────────────────────────────────────────
#  Global design token extraction
# ─────────────────────────────────────────────
def extract_global_tokens(root: dict[str, Any]) -> dict[str, Any]:
    color_usage: dict[str, int] = {}
    fonts: list[dict[str, Any]] = []
    seen_fonts: set[str] = set()

    def walk(n: dict[str, Any]) -> None:
        if is_noise(n):
            return
        for fill in n.get("fills", []):
            if fill.get("type") == "SOLID" and fill.get("visible", True) is not False:
                h = to_hex(fill.get("color"))
                if h:
                    color_usage[h] = color_usage.get(h, 0) + 1
        st = n.get("style") or {}
        if st.get("fontFamily"):
            key = f"{st.get('fontFamily')}_{st.get('fontSize')}_{st.get('fontWeight')}"
            if key not in seen_fonts:
                seen_fonts.add(key)
                fonts.append({k: v for k, v in {
                    "fontFamily":  st.get("fontFamily"),
                    "fontSize":    st.get("fontSize"),
                    "fontWeight":  st.get("fontWeight"),
                    "lineHeightPx": st.get("lineHeightPx"),
                }.items() if v is not None})
        for child in n.get("children", []):
            walk(child)

    walk(root)
    sorted_colors = [{"hex": c, "usageCount": cnt}
                     for c, cnt in sorted(color_usage.items(), key=lambda x: -x[1])]
    return {
        "palette": sorted_colors,
        "typography": sorted(fonts, key=lambda f: -(f.get("fontSize") or 0)),
    }


def extract_background(root: dict[str, Any]) -> str | None:
    for fill in (root.get("background", []) or root.get("fills", [])):
        if fill.get("type") == "SOLID":
            return to_hex(fill.get("color"))
    return None


# ─────────────────────────────────────────────
#  Public normalize entry point
# ─────────────────────────────────────────────
def normalize(root: dict[str, Any], file_id: str = "") -> dict[str, Any]:
    bb = root.get("absoluteBoundingBox", {})
    screen_name = root.get("name", "Screen").strip()

    components: list[dict[str, Any]] = []
    collect(root, components, _root=True)

    tokens = extract_global_tokens(root)
    primary = tokens["palette"][0]["hex"] if tokens["palette"] else None
    bg = extract_background(root)

    # Content width = widest direct child frame
    content_width: float | None = None
    for child in root.get("children", []):
        w = child.get("absoluteBoundingBox", {}).get("width")
        if w and (content_width is None or w > content_width):
            content_width = w

    schema: dict[str, Any] = {
        "screen": screen_name,
        "source": {"fileId": file_id, "nodeId": root.get("id", ""), "nodeName": screen_name},
        "layout": {
            "width": bb.get("width"),
            "height": bb.get("height"),
            "contentWidth": content_width,
            "backgroundColor": bg,
        },
        "tokens": {
            "primaryColor": primary,
            "palette": tokens["palette"],
            "typography": tokens["typography"],
        },
        "components": components,
    }

    auto = extract_auto_layout(root)
    if auto:
        schema["layout"]["autoLayout"] = auto

    return schema


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize raw Figma node JSON into a clean UI schema")
    parser.add_argument("--input",   required=True)
    parser.add_argument("--output",  required=True)
    parser.add_argument("--file-id", default="", dest="file_id")
    args = parser.parse_args()

    raw = json.loads(Path(args.input).read_text(encoding="utf-8"))
    schema = normalize(raw, file_id=args.file_id)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(schema, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"✅  Wrote normalized UI schema → {out_path}")
    print(f"    Screen   : {schema['screen']}")
    print(f"    Components: {len(schema['components'])}")
    print(f"    Primary  : {schema['tokens']['primaryColor']}")
    print(f"    Palette  : {[p['hex'] for p in schema['tokens']['palette'][:5]]}")


if __name__ == "__main__":
    main()

