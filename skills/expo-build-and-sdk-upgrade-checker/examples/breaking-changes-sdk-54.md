# Example: Breaking Changes — SDK 53 → 54

## Scenario

App uses Reanimated gestures and worklet callbacks extensively. After the SDK 53→54
hop, the app crashes at runtime with "useWorkletCallback is not a function".
A second issue — `react-native-worklets` missing — causes every worklet to fail.
A third silent issue — nativewind 4.0.x — makes all Tailwind styling disappear
with no error in the console.

## Input — package.json (excerpt, after `expo install --fix`)

```json
{
  "dependencies": {
    "expo": "~54.0.0",
    "react-native-reanimated": "~4.1.0",
    "react-native-gesture-handler": "~2.28.0",
    "nativewind": "^4.0.36",
    "tailwindcss": "^3.4.17"
  }
}
```

`babel.config.js` (pre-upgrade, manually specifies the plugin):

```js
module.exports = function (api) {
  api.cache(true);
  return {
    presets: ['babel-preset-expo'],
    plugins: ['react-native-reanimated/plugin'],  // manual plugin — must change
  };
};
```

Pre-upgrade source patterns:

```tsx
// src/hooks/useSwipeHandler.ts
import { useWorkletCallback, runOnJS } from 'react-native-reanimated';
const onSwipe = useWorkletCallback((direction) => {
  handleSwipe(direction);
}, [handleSwipe]);

// src/components/AnimatedCard.tsx
import { executeOnUIRuntimeSync } from 'react-native-reanimated';
```

## Analysis (via checks/breaking-changes-sdk-54.md)

Phase A fast import audit:

```bash
REANIMATED_FILES=$(grep -rln "from 'react-native-reanimated'" \
  --include="*.tsx" --include="*.ts" src/ app/ components/ hooks/ 2>/dev/null)
```

Phase B targeted scans:

```bash
# useWorkletCallback — CRITICAL
echo "$REANIMATED_FILES" | xargs grep -n "useWorkletCallback\s*("
# → src/hooks/useSwipeHandler.ts:3  ← CRITICAL: removed in Reanimated v4

# executeOnUIRuntimeSync — CRITICAL
echo "$REANIMATED_FILES" | xargs grep -n "executeOnUIRuntimeSync"
# → src/components/AnimatedCard.tsx:8  ← CRITICAL: removed in Reanimated v4

# Babel plugin — MEDIUM
grep -n "react-native-reanimated/plugin" babel.config.js
# → babel.config.js:5  ← must change to react-native-worklets/plugin

# react-native-worklets missing — HIGH
node -e "const p=require('./package.json'); console.log(p.dependencies['react-native-worklets'] || 'MISSING')"
# → MISSING  ← HIGH: Reanimated v4 peer dep not installed
```

Third-party check:

```bash
node -e "const p=require('./package.json'); console.log('nativewind:', p.dependencies?.['nativewind'])"
# → nativewind: ^4.0.36  ← CRITICAL: must be >=4.2.1 for SDK 54
```

## Findings report

```
VERDICT: BLOCK — 3 CRITICAL, 1 HIGH, 1 MEDIUM

[CRITICAL] useWorkletCallback() removed in Reanimated v4
  src/hooks/useSwipeHandler.ts:3
  Runtime: "useWorkletCallback is not a function"
  Fix: use useCallback with 'worklet'; directive

[CRITICAL] executeOnUIRuntimeSync removed in Reanimated v4
  src/components/AnimatedCard.tsx:8
  Runtime: "executeOnUIRuntimeSync is not a function"
  Fix: replace with runOnUISync

[CRITICAL] nativewind@4.0.36 — must be >=4.2.1
  All className styling silently produces no styles on SDK 54.
  Fix: npm install nativewind@^4.2.1 tailwindcss@3.4.17

[HIGH] react-native-worklets not installed
  Any worklet will crash: "Worklets runtime not available"
  Fix: npx expo install react-native-worklets

[MEDIUM] babel.config.js: react-native-reanimated/plugin must change
  Fix: change to 'react-native-worklets/plugin' (last in plugins[])
```

## Fix applied

```bash
# Install missing peer dep
npx expo install react-native-worklets
```

`babel.config.js` fix:

```js
module.exports = function (api) {
  api.cache(true);
  return {
    presets: ['babel-preset-expo'],
    plugins: ['react-native-worklets/plugin'],  // changed from reanimated/plugin
  };
};
```

Source code fixes:

```tsx
// src/hooks/useSwipeHandler.ts
// Before
const onSwipe = useWorkletCallback((direction) => {
  handleSwipe(direction);
}, [handleSwipe]);

// After
const onSwipe = useCallback((direction: string) => {
  'worklet';
  runOnJS(handleSwipe)(direction);
}, [handleSwipe]);

// src/components/AnimatedCard.tsx
// Before
executeOnUIRuntimeSync(() => { syncValue.value = 0; });
// After
runOnUISync(() => { syncValue.value = 0; });
```

```bash
npm install nativewind@^4.2.1 tailwindcss@3.4.17

rm -rf node_modules && rm -f package-lock.json && npm install
npx expo start -c
npx expo-doctor   # expect clean
eas build --profile preview --platform ios --non-interactive
```

## Lesson

Reanimated v3→v4 is a source-level breaking upgrade — removed APIs crash at
runtime with no TypeScript warning. Run the Phase B grep for all removed
Reanimated APIs before touching any packages. The nativewind silent regression
is the most dangerous: the app compiles and runs with zero errors but every
screen is visually broken. Always check nativewind's version explicitly as
part of the SDK 53→54 hop — `expo-doctor` will not flag it.
