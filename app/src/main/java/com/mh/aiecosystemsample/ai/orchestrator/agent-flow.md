# AI Orchestrator

The AI Orchestrator acts as the **central controller** that decides which AI agent should perform a task and in what order. It ensures a strict separation between Development (Creation) and Testing (Validation) to maintain project integrity.

---

# Mandatory Compliance & Governance

To ensure all AI agents strictly follow the project guidelines, every agent **MUST** perform the following steps before starting any task:

1. **Rule Ingestion:** Read `ai/architecture/android-architecture.md` and all files in `ai/guidelines/`.
2. **Context Awareness:** Read the specific feature requirements from `ai/features/`.
3. **Communication:** The Orchestrator **MUST** provide a real-time status dashboard in the chat window, detailing which agent is running, its specific activity, and the final success/fail summary.
4. **Enforcement:** The Orchestrator will block the flow if any "Quality Gate" agent (Accessibility, UI Validator, or Sonar) detects a violation of these rules. Non-compliant code will be sent back to the source agent for immediate correction.

---

# 1. Development Phase (Creation)
The goal is to generate functional, high-quality feature code.

1. **Designer Agent**: Generate Compose UI layout and theme.
2. **Accessibility Agent**: Perform initial "Shift-Left" accessibility audit.
3. **Functionality Agent**: Implement ViewModel, State management, and Business Logic.
4. **Firebase Agent**: Setup Remote Config, A/B tests, and Feature Flags (Conditional).
5. **Analytics Agent**: Implement data tracking strategy and screen events.
6. **TDD Agent**: Generate Unit Tests and Automation Test stubs.

---

# 2. Testing Phase (Verification)
The goal is to validate that the output matches the requirements and quality standards.

1. **Unit Test Validator**: Execute and verify all generated unit tests pass.
2. **Automation Test Agent**: Execute UI/Integration tests using the stubs from the TDD Agent.
3. **UI Validator Agent**: Compare the final implementation against Design & Accessibility specs.
4. **Sonar Agent**: Final Quality Gate for architecture compliance and code smells.

---

# Workflow Process & Visibility

1. **Initialize:** Read architecture and mandatory guidelines. **Status: Output "Rule Ingestion" success.**
2. **Identify:** Load feature requirements from `ai/features/`. **Status: Output "Context Awareness" success.**
3. **Develop:** Trigger Development Phase agents (Steps 1-6) sequentially. **Status: Output per-agent progress in dashboard.**
4. **Integrate:** Merge all generated files into the project structure.
5. **Verify:** Trigger Testing Phase agents (Steps 1-4) sequentially. **Status: Output per-agent verification results in dashboard.**
6. **Iterate:** If any validation fails, route feedback back to the responsible agent and restart the verification loop.

---

# Agent Status Dashboard (Chat Output Template)

| Phase | Agent | Activity | Result |
| :--- | :--- | :--- | :--- |
| **{Phase Name}** | **{Agent Name}** | {Specific Task Description} | {✅ SUCCESS / ❌ FAIL} |

---

# Feature Generation Rules
- **Structure:** All features must be in `feature/{featureName}/`.
- **Mandatory Files:** Every feature requires `FeatureScreen.kt`, `FeatureViewModel.kt`, and `FeatureState.kt`.
- **Naming:** Must follow `ai/guidelines/convention/AI_NAMING_CONVENTION.md`.

---

# Final Responsibility
The orchestrator ensures full adherence to architectural guidelines, correct agent sequencing, mandatory testing, visibility through chat dashboards, and successful integration of validated code.

---

End of Orchestrator
