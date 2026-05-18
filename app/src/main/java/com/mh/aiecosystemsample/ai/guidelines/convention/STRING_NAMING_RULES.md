# String Naming & Usage Rules

To maintain a clean and localized codebase, follow these rules for all UI strings.

## 1. Naming Convention
Strings must follow the hierarchy: **`feature_screen_component_state`**

| Part | Description | Examples |
| :--- | :--- | :--- |
| **Feature** | The high-level module/feature name | `catalogue`, `auth`, `profile`, `chat` |
| **Screen** | The specific screen or workflow | `reward_detail`, `login`, `history` |
| **Component** | The UI element using the string | `title`, `button`, `error`, `hint` |
| **State** | (Optional) The specific state | `loading`, `success`, `low_balance`, `disabled` |

### Example:
*   **Key:** `catalogue_reward_detail_low_balance_error`
*   **Value:** "Almost there! Keep scanning."

## 2. No Hardcoded Strings
*   **NEVER** use literal strings in Composable functions or Kotlin code.
*   **ALWAYS** use `stringResource(id = R.string.key)` in Compose.
*   **ALWAYS** use `context.getString(R.string.key)` in non-UI code.

## 3. Localization Ready
*   Keep all strings in `res/values/strings.xml`.
*   If a string has dynamic parts, use placeholders:
    *   `res/values/strings.xml`: `<string name="auth_login_welcome_back">Welcome back, %1$s!</string>`
    *   Usage: `stringResource(R.string.auth_login_welcome_back, userName)`

## 4. Reusability vs. Specificity
*   Avoid generic names like `error_message`. If an error is specific to a screen, name it after that screen.
*   Common strings like `common_ok`, `common_cancel`, `common_retry` are allowed in a `common` category.
