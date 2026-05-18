# AI Directory Rules

All AI-related documentation, guidelines, and agent definitions must reside within the `ai/` folder.

## 1. Allowed Locations
All `.md` files that guide the AI or define project rules must be placed in:
`app/src/main/java/com/a7/aiecosystempoc/ai/`

### Sub-directory structure:
*   `ai/agents/`: Definitions of specific AI roles (e.g., Designer, Tester).
*   `ai/architecture/`: Core architectural rules and patterns.
*   `ai/features/`: Specific instructions for individual features.
*   `ai/guidelines/`: Coding standards, naming conventions, and UI rules.
*   `ai/orchestrator/`: Rules for how AI agents interact.

## 2. Prohibited Locations
*   Do **NOT** place `.md` files in the project root (except for the main `README.md`).
*   Do **NOT** place `.md` files inside `core/`, `ui/`, or other functional code packages.

## 3. Enforcement
If an AI agent needs to create a new guideline or rule, it must first check `ai/guidelines/` and place the new file there.
