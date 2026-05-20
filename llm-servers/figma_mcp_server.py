#!/usr/bin/env python3
"""
Figma MCP Server

Exposes Figma API as MCP tools for AI agents to fetch design data.
Includes a built-in normalize tool that turns raw Figma JSON
into a clean UI schema for Compose code generation.
"""

import os
import sys
import json
from pathlib import Path
from typing import Any, Optional
import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from mcp.server import InitializationOptions

# Import normalizer from this repo.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_NORMALIZER_PATH = _PROJECT_ROOT / "tools" / "figma"
if _NORMALIZER_PATH.is_dir():
    sys.path.insert(0, str(_NORMALIZER_PATH))
try:
    from normalize_figma_node import normalize as _normalize_node
    _NORMALIZER_AVAILABLE = True
except ImportError:
    _NORMALIZER_AVAILABLE = False


def _read_env_var_from_dotenv(var_name: str) -> Optional[str]:
    """Read a single variable from llm-servers/.env without extra dependencies."""
    dotenv_path = Path(__file__).with_name(".env")
    if not dotenv_path.is_file():
        return None

    for raw_line in dotenv_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        if key.strip() != var_name:
            continue

        cleaned = value.strip().strip('"').strip("'")
        return cleaned or None

    return None


FIGMA_API_BASE = "https://api.figma.com/v1"


class FigmaClient:
    """Client for interacting with Figma API."""

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.environ.get("FIGMA_TOKEN") or _read_env_var_from_dotenv("FIGMA_TOKEN")
        if not self.token:
            raise ValueError("FIGMA_TOKEN is required (set env var or llm-servers/.env)")
        self.client = httpx.AsyncClient(
            headers={"X-Figma-Token": self.token},
            timeout=30.0
        )

    async def get_file(self, file_key: str) -> dict:
        """Fetch full file metadata."""
        response = await self.client.get(f"{FIGMA_API_BASE}/files/{file_key}")
        response.raise_for_status()
        return response.json()

    async def get_node(
        self,
        file_key: str,
        node_id: str,
        depth: int = 1
    ) -> dict:
        """Fetch a specific node from the file."""
        response = await self.client.get(
            f"{FIGMA_API_BASE}/files/{file_key}/nodes",
            params={"ids": node_id, "depth": depth}
        )
        response.raise_for_status()
        data = response.json()
        nodes = data.get("nodes", {})
        return nodes.get(node_id, {}).get("document", {})

    async def get_images(
        self,
        file_key: str,
        node_ids: list[str],
        scale: float = 2.0,
        format: str = "png"
    ) -> dict:
        """Export nodes as images."""
        response = await self.client.get(
            f"{FIGMA_API_BASE}/images/{file_key}",
            params={
                "ids": ",".join(node_ids),
                "scale": scale,
                "format": format
            }
        )
        response.raise_for_status()
        return response.json()

    async def get_styles(self, file_key: str) -> dict:
        """Fetch all styles in the file."""
        response = await self.client.get(f"{FIGMA_API_BASE}/files/{file_key}/styles")
        response.raise_for_status()
        return response.json()

    async def get_components(self, file_key: str) -> dict:
        """Fetch all components in the file."""
        response = await self.client.get(f"{FIGMA_API_BASE}/files/{file_key}/components")
        response.raise_for_status()
        return response.json()


# Create MCP server
app = Server("figma-mcp-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="figma_get_file",
            description="Get full Figma file metadata including all pages, frames, and styles",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_id": {
                        "type": "string",
                        "description": "Figma file ID (from URL like figma.com/file/FILE_ID/...)"
                    }
                },
                "required": ["file_id"]
            }
        ),
        Tool(
            name="figma_get_node",
            description="Get a specific node (frame, component, group) from a Figma file",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_id": {
                        "type": "string",
                        "description": "Figma file ID"
                    },
                    "node_id": {
                        "type": "string",
                        "description": "Node ID (from Figma URL like ?node-id=123:456)"
                    },
                    "depth": {
                        "type": "integer",
                        "description": "Depth of children to fetch (default: 1)",
                        "default": 1
                    }
                },
                "required": ["file_id", "node_id"]
            }
        ),
        Tool(
            name="figma_get_images",
            description="Export nodes as PNG images",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_id": {
                        "type": "string",
                        "description": "Figma file ID"
                    },
                    "node_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of node IDs to export"
                    },
                    "scale": {
                        "type": "number",
                        "description": "Image scale (1, 2, 3, or 4)",
                        "default": 2.0
                    },
                    "format": {
                        "type": "string",
                        "enum": ["png", "svg", "jpg", "pdf"],
                        "description": "Image format",
                        "default": "png"
                    }
                },
                "required": ["file_id", "node_ids"]
            }
        ),
        Tool(
            name="figma_get_styles",
            description="Get all styles (colors, text, effects) from a Figma file",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_id": {
                        "type": "string",
                        "description": "Figma file ID"
                    }
                },
                "required": ["file_id"]
            }
        ),
        Tool(
            name="figma_get_components",
            description="Get all components from a Figma file",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_id": {
                        "type": "string",
                        "description": "Figma file ID"
                    }
                },
                "required": ["file_id"]
            }
        ),
        Tool(
            name="figma_normalize",
            description=(
                "Fetch a Figma node and return a clean, normalized UI schema JSON ready for "
                "Compose code generation. Extracts components (Text, TextField, Button, Image), "
                "per-component colors, typography (fontFamily, fontSize, fontWeight, lineHeight), "
                "spacing, border radius, interactions, and global design tokens (palette + type scale). "
                "Use this instead of figma_get_node when you want to generate UI code."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "file_id": {
                        "type": "string",
                        "description": "Figma file ID"
                    },
                    "node_id": {
                        "type": "string",
                        "description": "Node ID (from Figma URL param node-id=, decoded e.g. 203:966)"
                    },
                    "depth": {
                        "type": "integer",
                        "description": "Depth to fetch from Figma (recommend 6 for screens)",
                        "default": 6
                    }
                },
                "required": ["file_id", "node_id"]
            }
        ),
    ]


@app.call_tool()
async def call_tool(
    name: str,
    arguments: dict | None
) -> list[TextContent]:
    """Handle tool calls."""
    if not arguments:
        arguments = {}

    try:
        client = FigmaClient()

        if name == "figma_get_file":
            result = await client.get_file(arguments["file_id"])
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "figma_get_node":
            result = await client.get_node(
                arguments["file_id"],
                arguments["node_id"],
                arguments.get("depth", 1)
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "figma_get_images":
            result = await client.get_images(
                arguments["file_id"],
                arguments["node_ids"],
                arguments.get("scale", 2.0),
                arguments.get("format", "png")
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "figma_get_styles":
            result = await client.get_styles(arguments["file_id"])
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "figma_get_components":
            result = await client.get_components(arguments["file_id"])
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "figma_normalize":
            if not _NORMALIZER_AVAILABLE:
                return [TextContent(type="text", text=(
                    "Error: normalizer not found. Ensure tools/figma/normalize_figma_node.py "
                    "exists in the MyAIEcoSystem project directory."
                ))]
            raw = await client.get_node(
                arguments["file_id"],
                arguments["node_id"],
                arguments.get("depth", 6)
            )
            schema = _normalize_node(raw, file_id=arguments["file_id"])
            return [TextContent(type="text", text=json.dumps(schema, indent=2, ensure_ascii=False))]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="figma-mcp-server",
                server_version="0.1.0",
                capabilities={}
            )
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())