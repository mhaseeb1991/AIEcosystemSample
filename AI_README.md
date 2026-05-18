# AI Development Guide

This repository uses an AI-assisted development workflow. All AI agents, architecture rules, and orchestration guidelines are defined in the **ai/** directory.

### Core Instruction for AI Agents
**Before starting any task, the AI MUST explore and read ALL files within the following directories to understand the project structure, rules, and latest guidelines:**

1.  **Architecture**: `ai/architecture/` (Core patterns and rules)
2.  **Workflow**: `ai/orchestrator/` (Agent flow and coordination)
3.  **Guidelines**: `ai/guidelines/` (ALL naming conventions, directory rules, and coding standards)
4.  **Agents**: `ai/agents/` (Specific role definitions)

### Directory Structure
*   `ai/agents/`: Agent responsibilities (Designer, Accessibility, Functionality).
*   `ai/features/`: Feature-specific instructions (e.g., `user-profile.md`).
*   `ai/guidelines/`: Project-wide rules, coding standards, and UI guidelines.
*   `ai/architecture/`: Android architectural rules and patterns.
*   `ai/orchestrator/`: Orchestration and agent communication logic.

All generated code must follow the collective rules defined in these directories.

### Agent Workflow
1.  **Designer Agent**: Generates UI components using Jetpack Compose.
2.  **Accessibility Agent**: Validates accessibility.
3.  **Functionality Agent**: Implements business logic and network calls.

The orchestrator ensures these agents respect the defined rules and stay within the `ai/` folder for documentation.
