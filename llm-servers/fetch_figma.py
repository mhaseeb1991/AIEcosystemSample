#!/usr/bin/env python3
"""
Figma Design Fetcher - Command line tool to fetch design data for AI agents

Usage:
    python3 fetch_figma.py <file_id> <node_id> [--depth N]
    python3 fetch_figma.py vLcVO8YQvAu4G8QgSVtX2s 203:966

Environment:
    FIGMA_TOKEN - Your Figma personal access token
"""

import os
import sys
import json
import asyncio
import argparse
from figma_mcp_server import FigmaClient

async def fetch_node(file_id: str, node_id: str, depth: int = 1) -> dict:
    """Fetch a specific node from Figma."""
    client = FigmaClient()
    return await client.get_node(file_id, node_id, depth)

async def fetch_file(file_id: str) -> dict:
    """Fetch full file from Figma."""
    client = FigmaClient()
    return await client.get_file(file_id)

def extract_design_spec(node_data: dict, file_id: str, node_id: str) -> dict:
    """Convert Figma node data to DesignSpec format."""
    components = []

    def extract_components(element, parent_spacing=0):
        elem_type = element.get('type', '')
        name = element.get('name', '')

        # Skip hidden/technical nodes
        if name.startswith('/') or name.startswith('~'):
            return

        comp = {
            'id': name.lower().replace(' ', '_').replace('-', '_'),
            'type': elem_type,
            'name': name,
        }

        # Extract bounding box if available
        if 'absoluteBoundingBox' in element:
            bbox = element['absoluteBoundingBox']
            comp['width'] = bbox.get('width')
            comp['height'] = bbox.get('height')

        # Extract position
        if 'absoluteBoundingBox' in element:
            comp['x'] = bbox.get('x')
            comp['y'] = bbox.get('y')

        # Extract fills (colors)
        if 'fills' in element and element['fills']:
            comp['colors'] = [f.get('colorRef', f.get('color')) for f in element['fills'] if f.get('type') == 'SOLID']

        # Extract text content
        if elem_type == 'TEXT' and 'characters' in element:
            comp['text'] = element.get('characters', '')

        # Extract corner radius
        if 'cornerRadius' in element:
            comp['cornerRadius'] = element['cornerRadius']

        components.append(comp)

        # Recurse into children
        for child in element.get('children', []):
            extract_components(child)

    extract_components(node_data)

    return {
        'screenName': node_data.get('name', 'Unknown'),
        'backgroundColor': '#FFFFFF',
        'components': components,
        'designTokens': {
            'primaryColor': '#6200EE',
            'errorColor': '#B00020'
        },
        'source': 'figma_mcp',
        'figmaFileId': file_id,
        'figmaNodeId': node_id
    }

async def main():
    parser = argparse.ArgumentParser(description='Fetch design data from Figma')
    parser.add_argument('file_id', help='Figma file ID')
    parser.add_argument('node_id', help='Figma node ID (e.g., 203:966)')
    parser.add_argument('--depth', type=int, default=2, help='Depth of children to fetch')
    parser.add_argument('--format', choices=['json', 'spec'], default='json',
                        help='Output format: raw JSON or DesignSpec format')
    parser.add_argument('--output', '-o', help='Output file (optional)')

    args = parser.parse_args()

    # Check token
    token = os.environ.get('FIGMA_TOKEN')
    if not token:
        print("Error: FIGMA_TOKEN environment variable not set", file=sys.stderr)
        print("Set it with: export FIGMA_TOKEN='your-token-here'")
        sys.exit(1)

    try:
        print(f"Fetching node {args.node_id} from file {args.file_id}...", file=sys.stderr)

        if args.format == 'spec':
            node = await fetch_node(args.file_id, args.node_id, args.depth)
            output = extract_design_spec(node, args.file_id, args.node_id)
        else:
            output = await fetch_node(args.file_id, args.node_id, args.depth)

        result = json.dumps(output, indent=2)

        if args.output:
            with open(args.output, 'w') as f:
                f.write(result)
            print(f"Written to {args.output}", file=sys.stderr)
        else:
            print(result)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main())