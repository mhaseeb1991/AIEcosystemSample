# Figma MCP Server

MCP server that exposes Figma API as tools for AI agents to fetch design data.

## Quick Start

### 1. Get a Figma Personal Access Token

1. Go to [Figma Settings → Account](https://www.figma.com/settings)
2. Scroll to "Personal access tokens"
3. Create a new token and copy it

### 2. Install the Server

```bash
# From the llm-servers directory (within MyAIEcoSystem project)
pip install -e .
```

### 3. Configure FIGMA_TOKEN

```bash
cp .env.example .env
```

Then edit `.env`:

```dotenv
FIGMA_TOKEN=your-figma-token
```

### 4. Configure in Your MCP Client (project root `.claude/mcp.json`)

```json
{
  "mcpServers": {
    "figma": {
      "command": "python3",
      "args": ["llm-servers/start_figma_mcp.py"],
      "env": {
        "PYTHONPATH": "tools/figma"
      }
    }
  }
}
```

`start_figma_mcp.py` performs a preflight check and prints a clear error if `FIGMA_TOKEN` is missing.

### 5. Available Tools

| Tool | Description |
|------|-------------|
| `figma_get_file` | Get full file metadata (pages, frames, styles) |
| `figma_get_node` | Get a specific node by ID |
| `figma_get_images` | Export nodes as PNG images |
| `figma_get_styles` | Get all design styles |
| `figma_get_components` | Get all components |
| `figma_normalize` | Fetch + normalize to UI schema in one call |

### 6. Usage Example

```python
# Fetch file metadata
figma_get_file(file_id="abc123XYZ")

# Fetch specific frame
figma_get_node(file_id="abc123XYZ", node_id="123:456")

# Export as image
figma_get_images(file_id="abc123XYZ", node_ids=["123:456"])
```

## File ID Extraction

From a Figma URL:
```
https://www.figma.com/file/FILE_ID/Title?node-id=NODE_ID
                              ^^^^^^^^            ^^^^^^^
```

- `FILE_ID`: path segment after `/file/` or `/design/`
- `NODE_ID`: value of `node-id` param (URL decode `%3A` → `:`)

## Integration with Your Project

Your Design Extractor Agent expects these MCP tools:
- `figma.get_file` → `figma_get_file`
- `figma.get_node` → `figma_get_node`
- `figma.get_image` → `figma_get_images`

The tool names map to the expected contract. The agent parses the JSON response into the `DesignSpec` format.