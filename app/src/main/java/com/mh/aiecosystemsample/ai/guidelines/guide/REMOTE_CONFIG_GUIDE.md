# Firebase Remote Config Guide

This document outlines the process for adding and managing Remote Config keys in the project.

## How to Add a New Remote Config Key

1.  **Define the Key in `RemoteConfigKeys.kt`**:
    Add a new constant to the `RemoteConfigKeys` object.
    ```kotlin
    const val NEW_FEATURE_ENABLED = "new_feature_enabled"
    ```

2.  **Update the POJO in `AppConfig.kt`**:
    Add the new field to the `AppConfig` data class with a default value.
    ```kotlin
    data class AppConfig(
        // ...
        val newFeatureEnabled: Boolean = false
    )
    ```

3.  **Update `RemoteConfigManager.kt`**:
    Update the `getAppConfig()` function or the simulated `configs` map to include the new key.

4.  **Add to Firebase Console**:
    *   Go to the Firebase Console -> Remote Config.
    *   Click "Add parameter".
    *   Enter the key (matching `RemoteConfigKeys`) and the default value.
    *   Publish changes.

## Best Practices
*   **Default Values**: Always provide sensible default values in the `AppConfig` POJO.
*   **Key Naming**: Use `snake_case` for keys in Firebase and `SCREAMING_SNAKE_CASE` for constants in Kotlin.
*   **Documentation**: Briefly describe what each flag does in `RemoteConfigKeys.kt`.
