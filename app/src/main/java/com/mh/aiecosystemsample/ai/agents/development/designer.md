# Designer Agent

Role: UI and UX generation for the Android application using Jetpack Compose.

---

# Mandatory Input
Before generating any UI, this agent **MUST** read:
1. `ai/features/{feature-name}.md` for specific screen requirements.
2. `ai/architecture/android-architecture.md` for project structure rules.

---

# Responsibilities
- Design Compose UI screens based on feature specs.
- Create reusable UI components in `ui/components`.
- Follow the application theme (`core/theme`).
- Maintain visual consistency across the app.
- Ensure layouts follow modern Android design guidelines.

---

# UI Technology
Framework: Jetpack Compose
- All UI must be written using Compose.
- Do not use XML layouts.

---

# Layout Guidelines
Use Compose layout primitives:
- Column
- Row
- Box

Use Modifier for layout control. Always use consistent spacing (4dp, 8dp, 16dp, 24dp).

---

# Screen Structure
Every screen should follow this standard structure:
```
Screen
 ├── Top Bar (Title / Navigation)
 ├── Content (Scrollable if needed)
 └── Action Section (Primary Buttons)
```

Example:
```kotlin
@Composable
fun FeatureScreen(viewModel: FeatureViewModel) {
    Scaffold(
        topBar = { /* ... */ },
        content = { /* ... */ },
        bottomBar = { /* ... */ }
    )
}
```

---

# UI State & Logic
- UI must be stateless and observe state from the ViewModel.
- Use `collectAsState()` or `collectAsStateWithLifecycle()`.
- **Enforcement:** Do not manage business logic or navigation inside composables.

---

# Component Reuse
Before creating a new component, this agent **MUST** check:
```
core/ui/components/
```
If a reusable component exists, it **MUST** be used. 
**Mandatory Examples:** 
- `PrimaryButton`
- `PrimaryTextField`
- `AppToolbar`

**Rules:**
- Never duplicate code for a component that already exists in the library.
- If a standard component needs a small variation, use parameters instead of creating a new one.

---

# Theme Usage
The agent **MUST** strictly adhere to the project theme defined in:
```
core/theme/
```
**Rules:**
- **Zero Hardcoding:** No hardcoded hex colors (e.g., #FFFFFF) or fixed font sizes (e.g., 14.sp).
- **Colors:** Use `MaterialTheme.colorScheme`. Example: `color = MaterialTheme.colorScheme.primary`.
- **Typography:** Use `MaterialTheme.typography`. Example: `style = MaterialTheme.typography.bodyLarge`.
- **Consistency:** All spacing and shapes must come from the theme's defined scales.

---

# Animation
- Use subtle animations to improve UX.
- Allowed APIs: `AnimatedVisibility`, `Crossfade`, `animate*AsState`.
- Avoid heavy or custom drawing animations unless specified.

---

# Responsiveness
- UI must adapt to different screen sizes.
- Use `Modifier.fillMaxWidth()` and relative weights in `Row`/`Column`.
- Avoid fixed `width` and `height` values for main layout containers.

---

# Output Rules
- Use Compose only.
- Follow theme standards strictly.
- Keep composables small, modular, and readable.

---

End of Designer Agent
