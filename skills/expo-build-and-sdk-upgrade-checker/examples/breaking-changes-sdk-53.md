# Example: Breaking Changes — SDK 52 → 53

## Scenario

App is a production React Native project upgrading from SDK 52 to 53. After
bumping `expo` and running `expo install --fix`, TypeScript compilation fails
with ~40 errors spread across the codebase — all from React 19's API removals.
Two packages also need major-version bumps before the build can proceed.

## Input — package.json (excerpt, after `expo install --fix`)

```json
{
  "dependencies": {
    "expo": "~53.0.0",
    "react": "19.0.0",
    "react-native": "0.79.x",
    "react-native-safe-area-context": "5.4.0",
    "@react-native-async-storage/async-storage": "2.1.2",
    "@react-native-firebase/app": "^21.0.0"
  }
}
```

Pre-upgrade source patterns:

```tsx
// src/components/Card.tsx
const Card: React.FC<{ title: string }> = ({ title, children }) => ...
Card.propTypes = { title: PropTypes.string };
Card.defaultProps = { title: 'Untitled' };

// src/hooks/useInputRef.ts
const inputRef = useRef<TextInput>();   // no-arg form

// src/types/navigation.ts
import type { React } from 'react';
const MyScreen: React.VFC = () => ...
```

## Analysis (via checks/breaking-changes-sdk-53.md)

Phase A fast import audit:

```bash
REACT_FILES=$(grep -rln "from 'react'\|propTypes\|defaultProps\|useRef\|React\.FC\|React\.VFC" \
  --include="*.tsx" --include="*.ts" src/ app/ components/ hooks/ 2>/dev/null)
```

Phase B targeted scans:

```bash
# propTypes — CRITICAL
echo "$REACT_FILES" | xargs grep -n "\.propTypes\s*="
# → src/components/Card.tsx:12, src/components/Button.tsx:28 (2 files)

# defaultProps — CRITICAL
echo "$REACT_FILES" | xargs grep -n "\.defaultProps\s*="
# → src/components/Card.tsx:13 (1 file)

# React.VFC — CRITICAL
echo "$REACT_FILES" | xargs grep -n "React\.VFC\b\|: VFC\b"
# → src/types/navigation.ts:4 (1 file)

# useRef no-arg — CRITICAL
echo "$REACT_FILES" | xargs grep -n "useRef<[^>]*>\s*(\s*)"
# → src/hooks/useInputRef.ts:3, src/screens/Search.tsx:8 (7 total)

# React.FC implicit children — HIGH
echo "$REACT_FILES" | xargs grep -n "React\.FC<\|: FC<"
# → 14 files — audit each for props.children usage
```

Running the codemod first handles the bulk of these:

```bash
npx codemod@latest react/19/migration-recipe
```

## Findings report

```
VERDICT: BLOCK — 4 CRITICAL pattern types found, requires codemod + manual fixes.

[CRITICAL] .propTypes = assignment — 2 files, 2 occurrences
  React 19 removes propTypes. TS2339 "Property does not exist".
  Fix: delete propTypes assignments; rely on TypeScript types.

[CRITICAL] .defaultProps = on function components — 1 file
  React 19 removes defaultProps on function components. TS2339.
  Fix: use ES6 default parameters.

[CRITICAL] React.VFC / VoidFunctionComponent — 1 file
  Removed in React 19. TS2339 "Property 'VFC' does not exist".
  Fix: replace with React.FC.

[CRITICAL] useRef<T>() with no initial value — 7 occurrences in 4 files
  TS2554 "Expected 1 arguments, but got 0."
  Fix: useRef<TextInput>(null) or useRef(null).

[CRITICAL] react-native-safe-area-context major version jump (4.12.0 → 5.4.0)
  Breaking if version not explicitly updated via expo install.
  Fix: npx expo install react-native-safe-area-context

[HIGH] @react-native-firebase Metro package exports failure
  RN 0.79 enforces exports field; Firebase internal paths fail to resolve.
  Fix: config.resolver.unstable_enablePackageExports = false in metro.config.js
```

## Fix applied

```bash
# Run codemod first (handles propTypes, defaultProps, VFC, most useRef)
npx codemod@latest react/19/migration-recipe

# Manual: remaining useRef no-arg calls the codemod missed
# Before: const ref = useRef<TextInput>()
# After:  const ref = useRef<TextInput>(null)

# Re-align major-bumped managed packages
npx expo install react-native-safe-area-context
npx expo install @react-native-async-storage/async-storage
```

`metro.config.js` Firebase fix:

```js
const config = getDefaultConfig(__dirname);
config.resolver.unstable_enablePackageExports = false;  // Firebase fix
module.exports = config;
```

React.FC implicit children fix (for each matched component using `children`):

```tsx
// Before
const Card: React.FC<{ title: string }> = ({ title, children }) => ...
// After
type CardProps = { title: string; children: React.ReactNode };
const Card: React.FC<CardProps> = ({ title, children }) => ...
```

```bash
npx expo-doctor          # expect clean
npx expo install --check # expect no mismatches
eas build --profile preview --platform ios --non-interactive
```

## Lesson

SDK 53's React 19 upgrade is the highest-volume code-change hop in the SDK 52→55
path. Run `npx codemod@latest react/19/migration-recipe` before any other step —
it handles ~80% of the TypeScript errors automatically. Then use Phase B scans to
catch what it missed (`useRef<T>()` no-arg and implicit `React.FC` children are
the most common survivors). Never skip the major-package version bump check for
`react-native-safe-area-context` and `@react-native-async-storage` — `expo-doctor`
won't flag them until after `expo install --fix` lands the new versions.
