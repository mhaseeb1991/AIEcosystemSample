# AI Development Guide

This repository uses an AI-assisted development workflow. All AI agents, architecture rules, and orchestration guidelines are defined in the **ai/** directory.

### Core Instruction for AI Agents
**Before starting any task, the AI MUST explore and read ALL files within the following directories to understand the project structure, rules, and latest guidelines:**

1.  **Architecture**: `ai/architecture/` (Core patterns and rules)
2.  **Workflow**: `ai/orchestrator/` (Agent flow and coordination)
3.  **Guidelines**: `ai/guidelines/` (ALL naming conventions, directory rules, coding standards, and Figma MCP usage)
4.  **Agents**: `ai/agents/` (Specific role definitions)

### Figma MCP Server (Design Source of Truth)
This project uses a live Figma MCP server for design data. **Do NOT use PNG files as the design reference.**

- **MCP Launcher Script:** `llm-servers/start_figma_mcp.py`
- **MCP Server Script:** `llm-servers/figma_mcp_server.py`
- **MCP Config:** `.claude/mcp.json` (registered in this project)
- **Usage Guide:** `ai/guidelines/guide/FIGMA_MCP_GUIDE.md`

Every feature spec in `ai/features/` must include a `file_id` and `node_id` from the Figma URL. The Designer Agent calls `figma_get_node` and `figma_get_styles`, normalizes raw Figma JSON into `app/src/main/assets/ui-schema/<feature>_ui_schema.json`, then generates Compose UI from that schema.

### Directory Structure
*   `ai/agents/`: Agent responsibilities (Designer, Accessibility, Functionality).
*   `ai/features/`: Feature-specific instructions (e.g., `user-profile.md`).
*   `ai/guidelines/`: Project-wide rules, coding standards, UI guidelines, and Figma MCP guide.
*   `ai/architecture/`: Android architectural rules and patterns.
*   `ai/orchestrator/`: Orchestration and agent communication logic.

All generated code must follow the collective rules defined in these directories.

### Agent Workflow
1.  **Designer Agent**: Fetches live design data via Figma MCP, then generates UI components using Jetpack Compose.
2.  **Accessibility Agent**: Validates accessibility.
3.  **Functionality Agent**: Implements business logic and network calls.

The orchestrator ensures these agents respect the defined rules and stay within the `ai/` folder for documentation.
