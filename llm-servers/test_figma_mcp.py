#!/usr/bin/env python3
"""
Test script to verify Figma MCP server connection.
Run this to check your token works and the server is functional.
"""

import asyncio
import sys
import os
import httpx

# Add current dir to path
sys.path.insert(0, os.path.dirname(__file__))

from figma_mcp_server import FigmaClient


async def test_connection():
    """Test the Figma client with a real file."""
    try:
        client = FigmaClient()
        print("✓ Client initialized successfully")
        print(f"  Token: {client.token[:10]}...{client.token[-4:]}")
    except ValueError as e:
        print(f"✗ Configuration error: {e}")
        print("\n  Set your token with:")
        print("  export FIGMA_TOKEN='your-token-here'")
        return False
    except Exception as e:
        print(f"✗ Failed to initialize client: {e}")
        return False

    # Test with a public Figma file (Figma's own design system)
    test_file_id = "abc123"  # Replace with your file ID

    try:
        print(f"\n  Testing file fetch for: {test_file_id}")
        result = await client.get_file(test_file_id)
        print(f"✓ Got file response")
        print(f"  Keys: {list(result.keys())}")
        return True
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            print(f"✓ Connection works (404 = file not found, but API responded)")
            return True
        elif e.response.status_code == 403:
            print(f"✗ Token invalid or no access to this file")
            return False
        else:
            print(f"✗ HTTP error: {e.response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Request failed: {e}")
        return False


if __name__ == "__main__":
    result = asyncio.run(test_connection())
    sys.exit(0 if result else 1)