#!/usr/bin/env python3
"""Quick test for the improved infer_type and theme generator."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.figma.normalize_figma_node import infer_type

tests = [
    ({"type": "TEXT", "name": "title"}, "Text"),
    ({"type": "RECTANGLE", "name": "bg", "fills": [{"type": "IMAGE"}]}, "Image"),
    ({"type": "VECTOR", "name": "arrow_right"}, "Icon"),
    ({"type": "BOOLEAN_OPERATION", "name": "shape"}, "Icon"),
    ({"type": "ELLIPSE", "name": "circle"}, "Icon"),
    ({"type": "LINE", "name": "line1"}, "Icon"),
    ({"type": "INSTANCE", "name": "eye icon", "absoluteBoundingBox": {"x":0,"y":0,"width":24,"height":24}}, "Icon"),
    ({"type": "FRAME", "name": "logo container", "absoluteBoundingBox": {"x":0,"y":0,"width":200,"height":100}}, "Image"),
    ({"type": "FRAME", "name": "login button"}, "Button"),
    ({"type": "FRAME", "name": "email field"}, "TextField"),
    ({"type": "INSTANCE", "name": "visibility", "absoluteBoundingBox": {"x":0,"y":0,"width":20,"height":20}}, "Icon"),
    ({"type": "FRAME", "name": "avatar image"}, "Image"),
    ({"type": "COMPONENT", "name": "ic_lock", "absoluteBoundingBox": {"x":0,"y":0,"width":16,"height":16}, "children": [{"type": "VECTOR"}]}, "Icon"),
    ({"type": "FRAME", "name": "banner", "fills": [{"type": "IMAGE"}]}, "Image"),
]

passed = 0
for node, expected in tests:
    result = infer_type(node)
    if result == expected:
        passed += 1
    else:
        print(f"FAIL: {node['type']}(\"{node['name']}\") -> {result} (expected {expected})")

print(f"{passed}/{len(tests)} infer_type tests passed")

# Test theme generator
from tools.figma.generate_theme import generate_color_kt

palette = [
    {"hex": "#4A90D9", "usageCount": 15},
    {"hex": "#FFFFFF", "usageCount": 10},
    {"hex": "#333333", "usageCount": 8},
]
color_kt = generate_color_kt(palette, "#FFFFFF", "com.test.theme")
assert "FigmaPrimary" in color_kt
assert "0xFF4A90D9" in color_kt
assert "FigmaBackground" in color_kt
print("Theme generator test passed")

