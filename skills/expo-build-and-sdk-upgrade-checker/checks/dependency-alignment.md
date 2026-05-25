# Check: Dependency Alignment & Expo Router Compatibility

Ensures every Expo-managed package is on the version the pinned SDK expects,
and that risky dependency combinations are flagged.

## Validation rules

1. **All `expo-*` and Expo-curated RN packages** must be installed via
   `expo install` so their versions track the SDK. Hand-pinned versions that
   diverge are HIGH (CRITICAL if it's a core navigation/render package).
2. **Expo Router triad** must be mutually aligned:
   `expo-router`, `react-native-screens`, `react-native-safe-area-context`.
   A mismatch here breaks navigation at runtime → CRITICAL.
3. **Reanimated / Gesture Handler** (`react-native-reanimated`,
   `react-native-gesture-handler`) must match the SDK; Reanimated also
   requires its Babel plugin to be **last** in `babel.config.js`. Missing/
   misordered plugin = CRITICAL (crashes on launch).
4. **Worklets**: SDK 52+ may split `react-native-worklets`; ensure presence
   when Reanimated 3.x+ requires it.
5. **No duplicate React / React Native** (monorepo hoist) → CRITICAL.
6. **One package manager / one lockfile** → HIGH if violated.
7. **Config-plugin packages** that are listed in `app.json` `plugins` must be
   present in `package.json` and vice-versa (MEDIUM/HIGH).

## Expo-managed packages that MUST go through `expo install`

Non-exhaustive but commonly drifted:

```
expo-router            react-native-screens
expo-status-bar        react-native-safe-area-context
expo-splash-screen     react-native-reanimated
expo-constants         react-native-gesture-handler
expo-linking           react-native-svg
expo-font              react-native-webview
expo-asset             @react-native-async-storage/async-storage
expo-updates           react-native-maps
expo-build-properties  react-native-pager-view
expo-dev-client        expo-image
```

## Risky / managed-incompatible patterns

| Pattern | Severity | Note |
| --- | --- | --- |
| `react-native-reanimated` without Babel plugin (last) | CRITICAL | App crashes immediately |
| Reanimated major newer than SDK supports | HIGH | Worklet/ABI mismatch |
| `react-native-screens` not aligned with `expo-router` | CRITICAL | Navigation crash / blank screen |
| A dependency requiring manual native linking (no config plugin) | HIGH | Out of managed scope |
| Two state/nav libs duplicating React (e.g. nested deps) | CRITICAL | Invariant violation |
| `@react-native-community/*` packages not via expo install | MEDIUM | Drift |
| Pinned `^`/`*` on `expo-*` packages | MEDIUM | Defeats SDK alignment |
| Patch-package patches on Expo core | HIGH | Breaks on SDK bump |

## Expo Router compatibility specifics

- `expo-router` major is tied to the SDK (e.g. Router 3.x ↔ SDK 50/51,
  Router 4.x ↔ SDK 52+). Never bump Router across a major without bumping the
  SDK.
- Requires `react-native-safe-area-context` and `react-native-screens` at
  SDK-matched versions, plus `main` in `package.json` set to
  `expo-router/entry`.
- Typed routes / `experiments.typedRoutes` must match the Router major.
- Deep-linking `scheme` must exist in app config (see
  `validate-expo-config.js`).

## Recommended fixes

```bash
npx expo install --check                 # list every drifted package
npx expo install --fix                   # realign all at once
npx expo install expo-router react-native-screens react-native-safe-area-context
```

For the Reanimated Babel plugin, ensure `babel.config.js` ends with:

```js
plugins: [
  // ...other plugins
  'react-native-reanimated/plugin', // MUST be last
],
```

## Example output

```
[CRITICAL] Expo Router triad misaligned
  expo-router 3.5.14  | react-native-screens 3.29.0 (expected ~3.31.x)
  Navigation will crash on iOS. Fix: npx expo install --fix

[CRITICAL] react-native-reanimated installed but Babel plugin missing
  babel.config.js has no 'react-native-reanimated/plugin'
  Fix: add it as the LAST entry in plugins[]

[MEDIUM] expo-image pinned to "^1.10.0" (bypasses SDK alignment)
  Fix: re-add via npx expo install expo-image
```
