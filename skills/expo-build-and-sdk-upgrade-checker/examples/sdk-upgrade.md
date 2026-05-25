# Example: Expo SDK Upgrade (50 → 51)

## Scenario

Team wants to upgrade a managed Expo Router app from SDK 50 to SDK 51 before
the next release.

## Input — package.json (excerpt)

```json
{
  "main": "expo-router/entry",
  "dependencies": {
    "expo": "~50.0.14",
    "expo-router": "~3.4.8",
    "react": "18.2.0",
    "react-native": "0.73.6",
    "react-native-screens": "~3.29.0",
    "react-native-safe-area-context": "4.8.2",
    "react-native-reanimated": "~3.6.2"
  }
}
```

## Analysis

`check-sdk-alignment.js` resolves SDK 50 → currently aligned. The request is a
*forward* upgrade, so follow `checks/upgrade-checklist.md` (one major).

## Procedure executed

```bash
git checkout -b chore/expo-sdk-51
npx expo-doctor                 # baseline: clean
npx expo install expo@^51
npx expo install --fix          # moves RN→0.74, router→3.5.x, screens, etc.
rm -rf node_modules package-lock.json && npm install
npx expo start -c
npx expo-doctor                 # must be clean
```

## Expected post-upgrade state

```
expo                          ~51.0.x
react-native                  0.74.x
react                         18.2.0
expo-router                   ~3.5.x
react-native-screens          ~3.31.x
react-native-safe-area-context 4.10.x
react-native-reanimated       ~3.10.x
```

## Findings report

```
[LOW]  SDK 50 → 51 single-major upgrade — supported path.
[INFO] expo install --fix realigned 6 packages.
[MEDIUM] Verify SDK 51 breaking changes for expo-router typedRoutes.
Decision: GO after preview EAS build passes.
```

## Lesson

Bump `expo` first, then `expo install --fix` — never hand-edit
`react-native`/`react`. Always run a preview EAS build before production.
