# Figma MCP Integration Guide

This project uses a schema-first Figma pipeline. AI agents MUST NOT generate UI from raw Figma JSON or PNGs.

**Pipeline:**
```
Figma MCP → figma_normalize tool → Clean UI Schema JSON → Compose code generation
```

---

## MCP Server Details

- **Server Script:** `llm-servers/figma_mcp_server.py`
- **Config Registered:** `.claude/mcp.json` (project root)
- **Auth:** Reads `FIGMA_TOKEN` from the MCP config env block.
- **Token issues:** If you see `403 Token expired`, refresh your token at Figma → Settings → Personal Access Tokens.

---

## Available MCP Tools

| Tool | Purpose | When to use |
| :--- | :--- | :--- |
| `figma_normalize` | **PRIMARY TOOL.** Fetch + normalize in one call → returns clean UI schema JSON | Always use this first for any new screen |
| `figma_get_node` | Raw Figma node JSON | Only if debugging the raw data |
| `figma_get_styles` | All named styles (color/text) in the file | Verifying design tokens |
| `figma_get_images` | Export node as PNG/SVG URL | Exporting logo/image assets |
| `figma_get_file` | Full file tree | Exploring an unfamiliar file |
| `figma_get_components` | All components | Cross-checking existing component library |

---

## How to Extract IDs from a Figma URL

```
https://www.figma.com/design/FILE_ID/Title?node-id=NODE_ID
                              ^^^^^^^^            ^^^^^^^^
```

- **`file_id`** — segment right after `/design/` or `/file/`
- **`node_id`** — `node-id` query param, URL-decode `%3A` → `:`

**Example:**
```
URL:      https://www.figma.com/design/vLcVO8YQvAu4G8QgSVtX2s/LoginApp?node-id=203%3A966
file_id:  vLcVO8YQvAu4G8QgSVtX2s
node_id:  203:966
```

---

## Designer Agent Mandatory Workflow

### Step 1 — Normalize (single call)
```
figma_normalize(file_id="<FILE_ID>", node_id="<NODE_ID>", depth=6)
```

This returns a clean UI schema with:
- All semantic components (`Text`, `TextField`, `Button`, `Image`, …) ordered top-to-bottom
- Per-component `textColor`, `backgroundColor`, `cornerRadius`
- `typography` per component: `fontFamily`, `fontWeight`, `fontSize`, `lineHeightPx`
- `mixedTypography` for text nodes with run-level overrides (e.g. bold first line, medium second)
- `isPassword: true` for password fields
- `interactions` listing Figma click targets
- Global `tokens.palette` sorted by usage frequency — `[0]` is the primary color
- Global `tokens.typography` scale sorted by font size descending

### Step 2 — Generate theme from Figma tokens

Run the theme generator to create `Color.kt`, `Theme.kt`, and `Type.kt` from the schema:

```bash
python3 tools/figma/generate_theme.py \
  --schema app/src/main/assets/ui-schema/<feature>_ui_schema.json \
  --theme-dir app/src/main/java/com/mh/aiecosystemsample/core/theme \
  --package com.mh.aiecosystemsample.core.theme \
  --theme-name AIEcosystemPocTheme
```

This automatically maps Figma palette to Material color tokens and typography to Material text styles.

> Never hardcode hex values in Kotlin. Always run the theme generator.
> Never keep default purple/pink Material colors. The theme must match Figma.

### Step 3 — Generate Compose UI per component

For each component in `schema.components[]`:

| schema `type` | Compose component | Notes |
| :--- | :--- | :--- |
| `Text` | `Text()` | Use `typography` field for style; `textColor` maps to colorScheme token |
| `TextField` | `OutlinedTextField()` | Use `label`, `isPassword: true` for `PasswordVisualTransformation()` |
| `Button` | `PrimaryButton()` | Use `text`, `cornerRadius`, `backgroundColor` for `RoundedCornerShape(cornerRadius.dp)` |
| `Image` | `Image(painterResource)` | `imageExportUrl` is auto-populated — download to `res/drawable/` |
| `Icon` | `Icon(painterResource)` | Small vector asset — download from `svgExportUrl`, use `tintColor` |
| `Card` | `Card()` | Container with `children[]` — recurse into nested components |
| `TopAppBar` | `TopAppBar()` | Use `title`, `backgroundColor`, `children[]` for nav icon/actions |
| `BottomBar` | `NavigationBar()` | Use `children[]` for nav items |
| `Chip` | `AssistChip()` / `FilterChip()` | Use `text`, `cornerRadius` |
| `Tab` | `Tab()` inside `TabRow` | Use `text` |
| `Dropdown` | `ExposedDropdownMenuBox()` | Use `text` as selected value |
| `Divider` | `HorizontalDivider()` | Use `color` token |
| `Checkbox` | `Checkbox()` | |

### Step 4 — Download image/icon assets

The `figma_normalize` tool now **automatically exports** image URLs. Each `Image` or `Icon` component
in the schema includes:
- `imageExportUrl` — PNG download link (3× scale, for raster images)
- `svgExportUrl` — SVG download link (for vector icons, convertible to Android VectorDrawable)

**Important:** The normalizer extracts only the actual image/vector child from a container — not the
whole container. If a Figma group named "Logo" contains both a text node and an image rectangle,
only the image rectangle's node ID is used for export. This prevents text from appearing inside
the exported image.

For each component with export URLs:
1. Download the PNG or SVG from the URL.
2. Save to `app/src/main/res/drawable/<component_name>.png` (or `.xml` for SVG→VectorDrawable).
3. Reference in Compose: `painterResource(R.drawable.<component_name>)`.

If export URLs are missing (e.g. network error), manually call:
```
figma_get_images(file_id="<FILE_ID>", node_ids=["<figmaNodeId>"], format="svg", scale=1)
```
Download the returned URL and save to `app/src/main/res/drawable/`.

---

## Feature Spec Convention

Every `ai/features/*.md` must include:

```markdown
## Figma Design
- **URL:** https://www.figma.com/design/<FILE_ID>/Title?node-id=<NODE_ID>
- **file_id:** <FILE_ID>
- **node_id:** <NODE_ID>
```

> ❌ No PNG paths. ❌ No raw Figma JSON in feature specs. ✅ Only `file_id` + `node_id`.

---

## Offline / Manual Normalization

If the MCP tool is unavailable, manually run:

```bash
# 1. Fetch raw node
cd llm-servers
export FIGMA_TOKEN="$(grep '^FIGMA_TOKEN=' .env | cut -d'=' -f2-)"
python3 fetch_figma.py <FILE_ID> <NODE_ID> --depth 6 --format json > /tmp/<feature>_raw.json

# 2. Normalize
cd ..
python3 tools/figma/normalize_figma_node.py \
  --input /tmp/<feature>_raw.json \
  --output app/src/main/assets/ui-schema/<feature>_ui_schema.json \
  --file-id <FILE_ID>
```

---

## Error Handling

| Error | Cause | Fix |
| :--- | :--- | :--- |
| `403 Token expired` | Figma PAT expired | Refresh token at Figma Settings → Personal Access Tokens |
| `403 Forbidden` on node | Token has no access to this file | Ensure the file belongs to your workspace |
| Node ID not found | `%3A` not decoded | Use `:` not `%3A` in `node_id` |
| Empty components list | Depth too shallow | Re-run with `--depth 6` |
| Wrong semantic type | Figma layer named ambiguously | Add the correct keyword to the relevant list in `normalize_figma_node.py` |

If any step fails: log with `AppLogger.ai("DesignerAgent", "…")`, report `❌ FAIL` in the Orchestrator dashboard.

---

## Normalizer Extension

The normalizer at `tools/figma/normalize_figma_node.py` uses keyword lists for semantic detection:

```python
BUTTON_KEYWORDS   = ["button","btn","cta","submit","login","log in","sign in",...]
TEXT_FIELD_KEYWORDS = ["input","field","holder","email","password","username",...]
IMAGE_KEYWORDS    = ["logo","banner","illustration","avatar","image"]
```

If a component is being misclassified, add its naming keyword to the correct list.

Schema contract: see `tools/figma/ui_schema_definition.json`.

---

*This guide is enforced by `designer.md`, `orchestrator/agent-flow.md`, and `ui_validator.md`.*
