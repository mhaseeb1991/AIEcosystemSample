# Android Architecture Guide

Project: AIEcosystemPOC

This document defines the official Android architecture for the project.
All developers and AI agents must follow these rules when generating or modifying code.

---

# 1. Tech Stack

Language: Kotlin
UI Framework: Jetpack Compose
Architecture Pattern: MVVM
Navigation: Navigation Compose
Min SDK: 24+

Libraries allowed:

* Jetpack Compose
* AndroidX Lifecycle
* Kotlin Coroutines
* Navigation Compose

Do not introduce new frameworks unless approved.

---

# 2. High Level Architecture

The project follows a layered architecture:

Core Layer
UI Layer
Feature Layer
AI Instruction Layer

```
com.a7.aiecosystempoc
│
├── ai
│
├── core
│
├── ui
│
└── feature
```

Each layer has a strict responsibility.

---

# 3. AI Layer

Location:

```
ai/
```

Purpose:

This folder contains AI instruction files used by AI coding assistants.

Subfolders:

```
ai/
 ├── agents
 ├── architecture
 ├── features
 └── orchestrator
```

Rules:

* Only Markdown files allowed
* Used for instructions, not executable code
* Must not contain Android logic

Agents read these files to understand how to generate project code.

---

# 4. Core Layer

Location:

```
core/
```

Purpose:

Contains shared infrastructure used by the entire app.

Structure:

```
core/
 ├── analytics
 ├── logger
 ├── navigation
 └── theme
```

Responsibilities:

Analytics tracking
Logging system
Navigation control
Theme management

Rules:

Core must NOT depend on Feature modules.

Core must NOT contain UI screens.

Core must be reusable across the entire app.

---

# 5. UI Layer

Location:

```
ui/
```

Purpose:

Contains Activities and reusable UI components.

Structure:

```
ui/
 ├── activity
 └── components
```

Example:

```
ui/activity
   MainActivity.kt
   SplashActivity.kt

ui/components
   PrimaryButton.kt
```

Rules:

UI layer must not contain business logic.

UI components must be reusable.

All UI must be written using Jetpack Compose.

---

# 6. Feature Layer

Location:

```
feature/
```

Purpose:

Contains all application features.

Each feature must be isolated in its own package.

Example:

```
feature/
   splash/
   home/
   auth/
```

Each feature must contain:

```
FeatureScreen.kt
FeatureViewModel.kt
FeatureState.kt
```

Example:

```
feature/home

HomeScreen.kt
HomeViewModel.kt
HomeState.kt
```

Rules:

Features must not depend directly on other features.

Features may use core services.

---

# 7. Navigation Architecture

Navigation is centralized.

Location:

```
core/navigation
```

Files:

```
AppNavHost.kt
AppNavigator.kt
```

Responsibilities:

Define navigation routes
Control navigation flow

Rules:

Screens must not directly manipulate navigation.

Navigation must be performed through AppNavigator.

Example:

```
navigator.navigateToHome()
```

---

# 8. Compose UI Rules

All UI must follow Compose best practices.

Rules:

UI must be stateless whenever possible.

State must be managed inside ViewModels.

Composable functions should only render UI.

Example:

```
@Composable
fun HomeScreen(
    viewModel: HomeViewModel
)
```

UI should observe ViewModel state.

---

# 9. ViewModel Rules

Every feature must include a ViewModel.

Responsibilities:

State management
Business logic
Data preparation

Rules:

ViewModel must not reference Android Views.

ViewModel must expose immutable UI state.

Example:

```
data class HomeState(
    val isLoading: Boolean = false,
    val items: List<String> = emptyList()
)
```

---

# 10. Logging System

All logs must go through:

```
core/logger/AppLogger
```

Example:

```
AppLogger.d("Home screen loaded")
```

Do not use Android Log directly.

---

# 11. Analytics System

All analytics events must go through:

```
core/analytics/AnalyticsManager
```

Example:

```
AnalyticsManager.trackScreen("HomeScreen")
```

---

# 12. Theme System

Theme configuration lives in:

```
core/theme
```

Files include:

```
Color.kt
Theme.kt
Type.kt
ThemeController.kt
```

Rules:

All UI must use the project theme.

Do not hardcode colors in screens.

---

# 13. Reusable UI Components

Location:

```
ui/components
```

Examples:

PrimaryButton
PrimaryTextField
AppToolbar

Rules:

Components must be reusable.

Components must not contain business logic.

Components must be stateless.

Example:

```
PrimaryButton(
    text = "Continue",
    onClick = {}
)
```

---

# 14. Accessibility

Accessibility must follow accessibility agent rules.

Minimum requirements:

All images must include contentDescription.

Touch targets must be at least 48dp.

Text must support screen readers.

Avoid relying only on color for meaning.

---

# 15. AI Code Generation Rules

When AI agents generate code they must:

1. Read this architecture document first
2. Follow the defined project structure
3. Place features inside the feature folder
4. Use Compose UI
5. Use ViewModels for state
6. Use Core services for logging and analytics

AI agents must NOT:

Create new architecture patterns.

Add dependencies without permission.

Place business logic inside UI.

---

# 16. Future Scalability

The architecture must support:

Large feature sets
AI generated features
Modular architecture
Plugin style extensions

Future improvements may include:

Multi module setup
Domain layer
Data layer

---

End of Android Architecture Guide