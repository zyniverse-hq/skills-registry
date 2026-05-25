# Example: Interpreting expo-doctor Warnings

## Scenario

Developer runs `npx expo-doctor` before pushing and pastes the output asking
"is this safe to build?".

## Input — expo-doctor output

```
✔ Check package.json for common issues
✖ Check Expo config for common issues
✖ Check that packages match their installed versions

  Expected package expo-router@~3.5.14
  Found expo-router@3.4.1

  Expected package react-native-screens@~3.31.1
  Found react-native-screens@3.29.0

  The following packages should be updated:
    expo-router, react-native-screens

✔ Check for app config fields that may not be synced
```

## Analysis (via checks/expo-doctor-analysis.md)

| Doctor line | Mapped severity | Reason |
| --- | --- | --- |
| expo-router mismatch | CRITICAL | Router gates all navigation |
| react-native-screens mismatch | CRITICAL | Part of the Router triad |

These are post-SDK-upgrade drift — the SDK moved but two managed packages
were left behind.

## Findings report

```
VERDICT: BLOCK — do not build until resolved.

[CRITICAL] expo-router 3.4.1 (expected ~3.5.14)
  Fix: npx expo install --fix
[CRITICAL] react-native-screens 3.29.0 (expected ~3.31.1)
  Fix: npx expo install --fix

After fix:
  npx expo install --fix
  npx expo-doctor      # expect clean
```

## Outcome

`expo install --fix` realigned both; re-running `expo-doctor` returned clean;
build unblocked.

## Lesson

Any doctor mismatch on `expo-router`, `react-native-screens`,
`react-native-safe-area-context`, `react-native-reanimated`, `react`,
`react-native` is CRITICAL — these gate build/navigation.
