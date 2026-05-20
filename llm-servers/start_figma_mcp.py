#!/usr/bin/env python3
"""Preflight launcher for the Figma MCP server.

Ensures FIGMA_TOKEN is available before starting the MCP process.
Resolution order:
1) FIGMA_TOKEN from process environment
2) FIGMA_TOKEN from llm-servers/.env
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def _read_env_var_from_dotenv(var_name: str) -> str | None:
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


def _resolve_figma_token() -> str | None:
    token = os.environ.get("FIGMA_TOKEN") or _read_env_var_from_dotenv("FIGMA_TOKEN")
    if token and token != "your-token-here":
        return token
    return None


def main() -> None:
    token = _resolve_figma_token()
    if not token:
        script = Path(__file__).name
        print("Error: FIGMA_TOKEN is missing.", file=sys.stderr)
        print("Set FIGMA_TOKEN in environment or in llm-servers/.env.", file=sys.stderr)
        print("Example:", file=sys.stderr)
        print("  cp llm-servers/.env.example llm-servers/.env", file=sys.stderr)
        print("  # then edit llm-servers/.env -> FIGMA_TOKEN=your-real-token", file=sys.stderr)
        print(f"Startup aborted by {script}.", file=sys.stderr)
        sys.exit(1)

    os.environ["FIGMA_TOKEN"] = token
    server_path = Path(__file__).with_name("figma_mcp_server.py")
    os.execv(sys.executable, [sys.executable, str(server_path)])


if __name__ == "__main__":
    main()

