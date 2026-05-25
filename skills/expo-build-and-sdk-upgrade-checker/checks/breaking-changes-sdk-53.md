# Breaking Changes: SDK 52 → 53

**React Native:** 0.76 → 0.79  
**React:** 18.3.1 → 19.0.0  
**expo-router:** ~4.0.x → ~5.0.x  
**react-native-reanimated:** ~3.16.x → ~3.17.x  
**New Architecture:** default for ALL projects (opt-out via `newArchEnabled: false` still allowed)

> React 19 is the dominant source of code changes in this hop.
> Run the official codemod first — it catches the majority of issues automatically:
> ```bash
> npx codemod@latest react/19/migration-recipe
> ```
> Then use the Phase B patterns below to catch what the codemod missed.

---

## Phase A — Fast import audit

```bash
REACT_FILES=$(grep -rln \
  "from 'react'\|from \"react\"\|propTypes\|defaultProps\|contextTypes\|getChildContext\|createFactory\|useRef\|forwardRef\|React\.FC\|React\.VFC" \
  --include="*.tsx" --include="*.ts" --include="*.js" --include="*.jsx" \
  src/ app/ components/ hooks/ screens/ lib/ 2>/dev/null \
  || grep -rln \
  "from 'react'\|propTypes\|defaultProps\|contextTypes\|useRef\|forwardRef\|React\.FC\|React\.VFC" \
  --include="*.tsx" --include="*.ts" --include="*.js" --include="*.jsx" \
  --exclude-dir=node_modules --exclude-dir=.expo .)

ROUTER_FILES=$(grep -rln "from 'expo-router'\|from \"expo-router\"" \
  --include="*.tsx" --include="*.ts" --include="*.js" --include="*.jsx" \
  src/ app/ components/ hooks/ screens/ lib/ 2>/dev/null \
  || grep -rln "from 'expo-router'\|from \"expo-router\"" \
  --include="*.tsx" --include="*.ts" --include="*.js" --include="*.jsx" \
  --exclude-dir=node_modules --exclude-dir=.expo .)

AV_FILES=$(grep -rln "from 'expo-av'\|from \"expo-av\"" \
  --include="*.tsx" --include="*.ts" --include="*.js" --include="*.jsx" \
  src/ app/ components/ hooks/ screens/ lib/ 2>/dev/null \
  || grep -rln "from 'expo-av'\|from \"expo-av\"" \
  --include="*.tsx" --include="*.ts" \
  --exclude-dir=node_modules --exclude-dir=.expo .)

TEST_FILES=$(grep -rln "react-dom/test-utils\|@testing-library" \
  --include="*.test.tsx" --include="*.test.ts" --include="*.spec.tsx" --include="*.spec.ts" \
  src/ app/ __tests__/ 2>/dev/null \
  || grep -rln "react-dom/test-utils\|@testing-library" \
  --include="*.test.tsx" --include="*.test.ts" \
  --exclude-dir=node_modules .)
```

---

## Phase B — Per-issue targeted scans

---

### React 19 — Removed APIs (hard TypeScript / runtime errors)

---

#### [CRITICAL] `propTypes` on function components — TS error + runtime removal

React 19 removes `propTypes` support entirely. Results in TS2339 "Property
'propTypes' does not exist on type" and a runtime error if a strict runtime
checks library is used.

```bash
echo "$REACT_FILES" | xargs grep -n "\.propTypes\s*="
```

Fix: delete the `propTypes` assignment. Rely on TypeScript types.

---

#### [CRITICAL] `defaultProps` on function components — TS error

`defaultProps` on function components is removed. Class components are unaffected.
Results in TS2339 on the assignment and TS2554 on callers.

```bash
echo "$REACT_FILES" | xargs grep -n "\.defaultProps\s*="
```

Fix: use ES6 default parameters instead.
```tsx
// Before
MyComponent.defaultProps = { count: 0 };
// After
function MyComponent({ count = 0 }: Props) { ... }
```

---

#### [CRITICAL] `React.VFC` / `React.VoidFunctionComponent` — removed

`React.VFC` is removed in React 19. Produces TS2339 "Property 'VFC' does not exist".

```bash
echo "$REACT_FILES" | xargs grep -n \
  "React\.VFC\b\|React\.VoidFunctionComponent\b\|: VFC\b\|: VoidFunctionComponent\b"
```

Fix: replace with `React.FC` (children are now explicitly typed, not implicit).

---

#### [CRITICAL] `contextTypes` / `getChildContext` — removed

Legacy context API removed. Produces TS errors and runtime "contextTypes is not
a function" crash.

```bash
echo "$REACT_FILES" | xargs grep -n \
  "contextTypes\s*=\|getChildContext\s*(\|static contextType\b"
```

Fix: migrate to `React.createContext()` + `useContext()`.

---

#### [CRITICAL] `React.createFactory()` — removed

Produces TS2339 "Property 'createFactory' does not exist on type 'typeof React'".

```bash
echo "$REACT_FILES" | xargs grep -n "createFactory\s*("
```

Fix: replace with JSX directly.

---

#### [CRITICAL] String refs — removed

`ref="inputName"` (string literal ref) produces a runtime error and TS error.

```bash
echo "$REACT_FILES" | xargs grep -n 'ref=["'"'"'][a-zA-Z]'
```

Fix: replace with `useRef()` or a ref callback.

---

#### [CRITICAL] `act` from `react-dom/test-utils` — moved

`act` is removed from `react-dom/test-utils`. Produces "act is not exported from
react-dom/test-utils" at runtime.

```bash
echo "$TEST_FILES" | xargs grep -n \
  "from 'react-dom/test-utils'\|require.*react-dom/test-utils"
```

Fix:
```tsx
// Before
import { act } from 'react-dom/test-utils';
// After
import { act } from 'react';
```

---

### React 19 — TypeScript type errors (compile-time breaks)

---

#### [CRITICAL] `useRef()` with no initial value — TS2554

`useRef()` with no argument, or `useRef<Type>()` with a type parameter but no
initial value, is a TypeScript error in React 19's type definitions.

```bash
# No-arg form: useRef()
echo "$REACT_FILES" | xargs grep -n "useRef\s*(\s*)"

# Generic with no value: useRef<TextInput>()
echo "$REACT_FILES" | xargs grep -n "useRef<[^>]*>\s*(\s*)"

# Qualified form: React.useRef()
echo "$REACT_FILES" | xargs grep -n "React\.useRef\s*(\s*)"
```

**Failure mode:** `TS2554: Expected 1 arguments, but got 0.`

Fix:
```tsx
const ref = useRef(null);            // mutable ref
const ref = useRef<TextInput>(null); // typed mutable ref
```

---

#### [HIGH] `React.FC` / `React.FunctionComponent` — children no longer implicit

In React 19, `React.FC` no longer includes `children` in props automatically.
Code that uses `props.children` without declaring it in the prop type gets
TS2339 "Property 'children' does not exist on type '...'".

```bash
echo "$REACT_FILES" | xargs grep -n \
  "React\.FC\b\|React\.FunctionComponent\b\|: FC\b\|: FunctionComponent\b"
```

For each match, check if the component uses `props.children` or `{ children }`.
If so, add `children: React.ReactNode` to the prop type explicitly.

```tsx
// Before (children was implicit)
const Card: React.FC<{ title: string }> = ({ title, children }) => ...

// After
type CardProps = { title: string; children: React.ReactNode };
const Card: React.FC<CardProps> = ({ title, children }) => ...
```

---

#### [MEDIUM] Ref callback returning a value — TS error

Ref callbacks that return a value produce a TS error in React 19. The return
value of a ref callback is now used for cleanup, so assigning it means React
treats the return as a cleanup function.

```bash
echo "$REACT_FILES" | xargs grep -n "ref=\s*{.*=>"
```

Inspect each result. If the arrow function returns a value (implicit return),
convert to a block body:
```tsx
// Before — implicit return of assignment
ref={el => (this.el = el)}
// After
ref={el => { this.el = el; }}
```

---

#### [LOW] `forwardRef` deprecated — deprecation warning at runtime

`forwardRef` is not removed but emits a deprecation warning. In React 19, `ref`
can be passed as a plain prop to function components.

```bash
echo "$REACT_FILES" | xargs grep -n "forwardRef\s*("
```

Can migrate incrementally — no hard break in SDK 53.

---

### Metro package `exports` enforcement — HIGH

React Native 0.79 enforces the `exports` field in package manifests. Deep
imports that bypass a package's `exports` map fail at Metro bundling with
"Unable to resolve module".

```bash
# Find third-party subpath imports (e.g. 'some-lib/internal/path')
grep -rn "from '[a-z@][^']*\/[^']*'" \
  --include="*.tsx" --include="*.ts" --include="*.js" \
  --exclude-dir=node_modules . \
  | grep -v "^.*from '\.\|from '\.\.\|from 'expo-router\|from 'react-native\|from '@react-navigation\|from '@expo"
```

For each result: check if the package's `package.json` has an `exports` field.
If it does and the subpath isn't listed, it will fail. Upgrade the package or
use only the public top-level import.

---

### `setImmediate` removed — MEDIUM

`setImmediate` is removed from the Expo runtime. Produces "setImmediate is not
defined" at runtime.

```bash
grep -rn "setImmediate\s*(" \
  --include="*.tsx" --include="*.ts" --include="*.js" \
  --exclude-dir=node_modules .
```

Fix: replace with `setTimeout(fn, 0)`.

---

### expo-router 5.0

---

#### [MEDIUM] `useRootNavigation()` deprecated

Returns undefined in some contexts in v5. Produces a runtime warning.

```bash
echo "$ROUTER_FILES" | xargs grep -n "useRootNavigation\s*("
```

Fix: replace with `useNavigationContainerRef()`.

---

#### [MEDIUM] `@testing-library/react-native` no longer bundled

`expo-router/testing-library` no longer re-exports `@testing-library/react-native`.
Produces "Cannot find module '@testing-library/react-native'" at test time.

```bash
echo "$TEST_FILES" | xargs grep -n "from 'expo-router/testing-library'"
```

Fix: install the peer dep explicitly.
```bash
npx expo install @testing-library/react-native
```

---

### expo-av Audio — MEDIUM

Audio API in `expo-av` will receive no more updates. Migrate to `expo-audio`.

```bash
echo "$AV_FILES" | xargs grep -n \
  "Audio\.\|import.*Audio.*expo-av\|from 'expo-av'.*Audio"
```

Fix:
```tsx
// Before
import { Audio } from 'expo-av';
const { sound } = await Audio.Sound.createAsync(source);
await Audio.setAudioModeAsync({ ... });

// After
import { useAudioPlayer, setAudioModeAsync } from 'expo-audio';
const player = useAudioPlayer(source);
```

---

### app.json / config

```bash
# jsEngine deprecated (Hermes is the default — remove the field)
grep -n "jsEngine" app.json app.config.js app.config.ts 2>/dev/null

# Android deep links — package name no longer auto-added as scheme
grep -n "scheme\|intentFilters" app.json app.config.js 2>/dev/null
```

---

### Summary table

| Pattern | Failure mode | Severity |
|---|---|---|
| `.propTypes =` | TS2339 + runtime removal | CRITICAL |
| `.defaultProps =` on function components | TS2339 / TS2554 | CRITICAL |
| `React.VFC` / `VoidFunctionComponent` | TS2339 "does not exist" | CRITICAL |
| `contextTypes` / `getChildContext` | TS error + runtime crash | CRITICAL |
| `React.createFactory()` | TS2339 "does not exist" | CRITICAL |
| String refs `ref="name"` | TS error + runtime error | CRITICAL |
| `act` from `react-dom/test-utils` | "act is not exported" runtime | CRITICAL |
| `useRef()` / `useRef<T>()` no-arg | TS2554 "Expected 1 argument" | CRITICAL |
| `React.FC` with implicit children | TS2339 "children does not exist" | HIGH |
| Ref callback returning value | TS error (cleanup conflict) | HIGH |
| Third-party subpath imports | Metro "Unable to resolve module" | HIGH |
| `setImmediate(` | "setImmediate is not defined" runtime | MEDIUM |
| `useRootNavigation()` | Undefined in some contexts | MEDIUM |
| `forwardRef(` | Deprecation warning | LOW |

---

## Third-party packages — SDK 52 → 53

See `checks/third-party-packages.md` for the full compatibility matrix and migration notes.

### Phase A — 3rd party import audit

```bash
THIRD_PARTY_FILES=$(grep -rln \
  "@gorhom/bottom-sheet\|@shopify/flash-list\|react-native-maps\|nativewind\|@react-native-firebase\|react-native-skia\|moti\b\|@legendapp/motion\|@tanstack/react-query\|react-native-mmkv\|async-storage" \
  --include="*.tsx" --include="*.ts" --include="*.js" --include="*.jsx" \
  src/ app/ components/ hooks/ screens/ lib/ 2>/dev/null \
  || grep -rln \
  "@gorhom/bottom-sheet\|@shopify/flash-list\|nativewind\|@react-native-firebase\|react-native-skia\|moti\b\|@tanstack/react-query\|async-storage" \
  --include="*.tsx" --include="*.ts" --include="*.js" --include="*.jsx" \
  --exclude-dir=node_modules --exclude-dir=.expo .)
```

### Version checks

```bash
node -e "
const p = require('./package.json');
const deps = { ...p.dependencies, ...p.devDependencies };
const check = (name, note) => console.log(name + ': ' + (deps[name] || 'not installed') + '  ' + note);
check('@gorhom/bottom-sheet', '← v5.0.x required for SDK 53');
check('@shopify/flash-list', '← 1.7.6 expected');
check('@react-native-async-storage/async-storage', '← 2.1.2 expected (major bump from 1.x)');
check('react-native-safe-area-context', '← 5.4.0 expected (major bump from 4.x)');
check('@shopify/react-native-skia', '← v2.0+ required for React 19');
check('nativewind', '← v4.x required');
check('@tanstack/react-query', '← v5 recommended for React 19');
check('zustand', '← v5 recommended for React 19');
"
```

### [CRITICAL] react-native-safe-area-context — major version jump

SDK 53 requires v5.4.0 (from 4.12.0). This is a major version bump. If still on v4,
context values and hook return shapes may differ, causing silent layout regressions or
TS errors.

```bash
echo "$THIRD_PARTY_FILES" | xargs grep -n \
  "from 'react-native-safe-area-context'\|useSafeAreaInsets\|SafeAreaView\|SafeAreaProvider"
```

`npx expo install react-native-safe-area-context` installs the correct v5.4.0.
After upgrading, smoke-test all screens that use safe area insets — especially on
devices with notches or Dynamic Island.

### [CRITICAL] @react-native-async-storage — major version jump

SDK 53 requires v2.1.2 (from 1.23.1). If still on v1, `npx expo install` will
install v2 which has different internal implementation. No API breaks in typical
usage, but test persistence-critical flows after upgrading.

```bash
node -e "const p=require('./package.json'); console.log(p.dependencies?.['@react-native-async-storage/async-storage'] || 'not installed')"
```

`npx expo install @react-native-async-storage/async-storage` pins to the correct version.

### [CRITICAL] @shopify/react-native-skia — React 19 incompatibility below v2.0

If installed and below v2.0, React 19's changes cause runtime crashes or TS errors
related to type changes in React element internals.

```bash
echo "$THIRD_PARTY_FILES" | xargs grep -n \
  "from '@shopify/react-native-skia'\|from 'react-native-skia'"
```

Fix: `npm install @shopify/react-native-skia@^2.0`

### [HIGH] @react-native-firebase — Metro package exports failure

React Native 0.79 (SDK 53) enables `package.json` `exports` field enforcement by default.
`@firebase/*` packages use internal paths that are not in their `exports` map.
Result: Metro bundling fails with "Unable to resolve module" for Firebase imports.

```bash
echo "$THIRD_PARTY_FILES" | xargs grep -n \
  "from '@react-native-firebase/\|from '@firebase/"
```

If found, add to `metro.config.js`:
```js
config.resolver.unstable_enablePackageExports = false;
```

### [HIGH] @gorhom/bottom-sheet — must be v5.x for SDK 53

v4 is incompatible with New Arch (default in SDK 53). Upgrade to v5.

```bash
echo "$THIRD_PARTY_FILES" | xargs grep -n \
  "from '@gorhom/bottom-sheet'\|BottomSheet\b\|BottomSheetModal\b"
```

```bash
npm install @gorhom/bottom-sheet@^5.0.0
```

### [HIGH] @tanstack/react-query v4 — breaking API differences with v5

v4 still works but is unmaintained. v5 API changes the hook call signature everywhere.
Key symptom on React 19 with v4: subtle async state update timing changes cause
test failures and occasional stale data display.

```bash
echo "$THIRD_PARTY_FILES" | xargs grep -n \
  "useQuery\s*(\[\|useMutation\s*(\|\bisLoading\b\|status.*loading"
```

`isLoading` → `isPending`; `status: 'loading'` → `status: 'pending'`

### [HIGH] zustand selector infinite loops — v5 required

Unstable (non-memoized) selectors in zustand v4 cause infinite re-render loops
under React 19's stricter rendering:
`"Maximum update depth exceeded"`

```bash
grep -rn "useStore\s*(\|create\s*(" \
  --include="*.tsx" --include="*.ts" src/ app/ 2>/dev/null \
  | grep -v "node_modules"
```

Audit each store selector for memoization. Upgrade: `npm install zustand@^5`

### [MEDIUM] moti — web crash on SDK 53

moti 0.20.0 + Reanimated 3.17.4 + RN 0.79 causes a web platform crash:
`"Cannot destructure property '__extends' of '_tslib.default' as it is undefined"`

If the project targets web, test moti-animated components on web after upgrading.
No fix available as of research — may need to conditionally exclude moti on web.

```bash
echo "$THIRD_PARTY_FILES" | xargs grep -n "from 'moti'"
```

### 3rd party summary — SDK 53

| Package | Required action | Risk if skipped |
|---|---|---|
| react-native-safe-area-context | `npx expo install` (4.x → 5.x) | Layout regressions, TS errors |
| @react-native-async-storage | `npx expo install` (1.x → 2.x) | Persistence failures |
| @shopify/react-native-skia | `npm install @shopify/react-native-skia@^2.0` | React 19 crash |
| @react-native-firebase | Add Metro `unstable_enablePackageExports: false` | Metro bundle failure |
| @gorhom/bottom-sheet | `npm install @gorhom/bottom-sheet@^5.0.0` | New Arch crash |
| @tanstack/react-query | Upgrade to v5 or audit v4 usage | Stale data, test failures |
| zustand | Upgrade to v5 or memoize all selectors | Infinite re-render loop |
| moti | Test on web; may need conditional exclusion | Web platform crash |
