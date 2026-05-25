# Example: SDK / React Native Version Mismatch

## Scenario

After running `npm install expo@^52` directly (bypassing `expo install`),
the project lands on SDK 52 with React Native and React left on the previous
SDK's versions. The dev client builds but the app crashes on launch with a
React invariant violation.

## Input — package.json

```json
{
  "dependencies": {
    "expo": "~52.0.0",
    "react": "18.2.0",
    "react-native": "0.74.5",
    "expo-router": "~4.0.2",
    "react-native-screens": "~4.4.0",
    "react-native-safe-area-context": "4.12.0",
    "react-native-reanimated": "~3.16.1"
  }
}
```

## Analysis (via checks/sdk-compatibility.md)

`npx expo install --check` output:

```
Expected package react-native@0.76.x
Found react-native@0.74.5

Expected package react@18.3.x
Found react@18.2.0

Expected package react-native-reanimated@~3.16.x
Found react-native-reanimated@3.10.1
```

| Doctor finding | Severity | Reason |
|---|---|---|
| react-native 0.74.5 (expected 0.76.x) | CRITICAL | SDK 52 ships with RN 0.76; ABI mismatch — build fails or produces an unstable binary |
| react 18.2.0 (expected 18.3.x) | HIGH | Renderer version skew causes invariant violation on launch |
| react-native-reanimated 3.10.1 behind | HIGH | SDK-aligned version required for New Arch stability |

VERDICT: BLOCK — project is half-upgraded.

## Findings report

```
[CRITICAL] react-native@0.74.5 does not match SDK 52 (expects 0.76.x)
  ABI mismatch. EAS Build will fail or produce an unstable binary.
  Fix: npx expo install --fix

[HIGH] react@18.2.0 does not match SDK 52 (expects 18.3.x)
  Renderer version skew — invariant violation crash on launch.
  Fix: npx expo install --fix

[HIGH] react-native-reanimated@3.10.1 behind SDK 52 alignment
  Fix: npx expo install --fix
```

## Fix applied

```bash
npx expo install --fix
# react-native: 0.74.5 → 0.76.x
# react: 18.2.0 → 18.3.x
# react-native-reanimated: 3.10.1 → 3.16.x

rm -rf node_modules && rm -f package-lock.json && npm install
npx expo start -c
npx expo-doctor   # expect clean
npx expo install --check   # expect no mismatches
```

## Lesson

Never use `npm install expo@...` or hand-edit `expo` in `package.json` to
bump the SDK. Always use `npx expo install expo@^<major>` followed immediately
by `npx expo install --fix`. Without `--fix`, every other dependency is
stranded on the previous SDK's versions. The `react-native` and `react`
versions must come from `expo install`, never from manual edits.
