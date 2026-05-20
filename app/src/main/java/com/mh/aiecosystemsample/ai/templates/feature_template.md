# Feature Template: [Feature Name]

## Description
[Provide a clear and concise description of the feature]

## Acceptance Criteria
- [ ] [Criteria 1]
- [ ] [Criteria 2]
- [ ] [Criteria 3]

## Figma Design
- **URL:** [Full Figma URL, e.g. https://www.figma.com/design/FILE_ID/Title?node-id=NODE_ID]
- **file_id:** [FILE_ID extracted from the URL]
- **node_id:** [NODE_ID extracted from the URL, decoded, e.g. 203:966]
- **Note:** AI agents must use `figma_get_node` and `figma_get_styles` MCP tools (see `ai/guidelines/guide/FIGMA_MCP_GUIDE.md`). Do NOT use a PNG file as the design source.

## Accessibility Design
- **Link:** [Insert Accessibility Figma URL or specific section here]

## Is it Configurable (A/B Test Details)
- **Config Key:** [e.g., feature_x_enabled]
- **Experiment Details:** [e.g., Control vs Variant A]

## Markets
- [e.g., Global, US, UK, etc.]

## F.E Functional Requirements
### B.E Integration
- **Endpoint:** [API Endpoint]
- **Method:** [GET/POST/PUT/DELETE]
- **Data Mapping:** [Briefly describe how data maps to UI]

### Click Action
- [Button/Element Name]: [Describe what happens when clicked]

### Navigation Flow
- [Start Screen] -> [Trigger] -> [Destination Screen]

### Analytics & Events
- **Data Requirement Document (DRD):** [Link to DRD/Analytics Spec]
- **Notes:** [Add any feature-specific analytics requirements not covered in the DRD]

## Test Cases
This feature will be tested using the **[Test Guidelines](../guidelines/guide/TEST_GUIDELINES.md)**.

### QA-Specific Test Cases
[Link to QA test case file or specific QA requirements here]

### Feature-Specific Requirements
- [Add any unique test cases for this specific feature]
