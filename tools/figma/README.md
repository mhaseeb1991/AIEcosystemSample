# Figma Normalization Tool

This folder contains a schema-first normalizer for Figma MCP output.

## Why

Raw `figma_get_node` payloads are large and noisy. We normalize them into a stable JSON schema before generating Compose UI.

Pipeline:

1. Fetch raw node JSON from Figma MCP.
2. Normalize raw JSON into a clean schema.
3. Generate UI from the schema.

## Run

```bash
python3 tools/figma/normalize_figma_node.py \
  --input /tmp/login_figma_raw.json \
  --output app/src/main/assets/ui-schema/login_ui_schema.json
```

## Output Contract

Schema definition:

- `tools/figma/ui_schema_definition.json`

Generated example:

- `app/src/main/assets/ui-schema/login_ui_schema.json`

