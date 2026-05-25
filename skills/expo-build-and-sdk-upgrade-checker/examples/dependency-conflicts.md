# Example: Dependency Conflict (Reanimated + duplicate React)

## Scenario

App crashes immediately on launch in a dev client with a worklet/invariant
error. Monorepo setup.

## Input — package.json (app package)

```json
{
  "dependencies": {
    "expo": "~51.0.0",
    "react": "18.2.0",
    "react-native": "0.74.5",
    "react-native-reanimated": "^3.10.1"
  }
}
```

`babel.config.js`:

```js
module.exports = function (api) {
  api.cache(true);
  return { presets: ['babel-preset-expo'] }; // no reanimated plugin
};
```

Also: root `node_modules/react@18.3.1` and app `node_modules/react@18.2.0`.

## Analysis (via detect-risky-dependencies.js + dependency-alignment.md)

```
[CRITICAL] REANIMATED_NO_PLUGIN
  react-native-reanimated installed but Babel plugin not referenced.
  App crashes on launch.

[CRITICAL] DUPLICATE_CORE
  react resolved twice (18.3.1 root vs 18.2.0 app) → invariant violation.

[LOW] EXPO_PKG_CARET
  reanimated uses "^3.10.1" — prefer expo install pinning.
```

## Fix

```js
// babel.config.js
module.exports = function (api) {
  api.cache(true);
  return {
    presets: ['babel-preset-expo'],
    plugins: ['react-native-reanimated/plugin'], // MUST be last
  };
};
```

```bash
# Re-pin reanimated to the SDK
npx expo install react-native-reanimated

# Dedupe React in the monorepo (package manager resolutions/nohoist)
# package.json (workspace root):
#   "resolutions": { "react": "18.2.0", "react-native": "0.74.5" }
npx expo start -c
```

## Lesson

Reanimated needs its Babel plugin **last**, every time. In monorepos enforce a
single `react`/`react-native` via resolutions/nohoist — duplicates cause
invariant crashes that look like unrelated bugs.
