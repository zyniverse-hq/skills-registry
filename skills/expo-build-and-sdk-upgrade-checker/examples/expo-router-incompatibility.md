# Example: Expo Router Incompatibility

## Scenario

After `npm install react-native-screens@latest`, navigation renders a blank
white screen on iOS and deep links don't open.

## Input

```json
{
  "main": "expo-router/entry",
  "dependencies": {
    "expo": "~51.0.0",
    "expo-router": "~3.5.14",
    "react-native-screens": "^4.0.0",
    "react-native-safe-area-context": "4.10.5"
  }
}
```

`app.json` has no `scheme`.

## Analysis (via dependency-alignment.md + validate-expo-config.js)

```
[CRITICAL] ROUTER triad misaligned
  expo-router ~3.5.14 (SDK 51) expects react-native-screens ~3.31.x
  Found react-native-screens 4.0.0 (manually installed, off-SDK).
  Result: navigation crash / blank screen.

[HIGH] NO_SCHEME
  expo-router present but app.json "scheme" missing.
  Deep links and auth redirects will not resolve.
```

## Fix

```bash
# Restore SDK-aligned screens version (never hand-pick for managed)
npx expo install react-native-screens react-native-safe-area-context

# Add a URL scheme for Router deep links
```

```json
// app.json
{ "expo": { "scheme": "acmeapp" } }
```

```bash
npx expo start -c
npx expo-doctor   # expect clean
```

## Lesson

`expo-router`, `react-native-screens`, and `react-native-safe-area-context`
move together with the SDK — only install them via `expo install`. Expo Router
also requires a `scheme` for deep linking.
