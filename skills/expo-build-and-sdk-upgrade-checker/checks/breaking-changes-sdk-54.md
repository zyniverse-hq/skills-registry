# Breaking Changes: SDK 53 → 54

**React Native:** 0.79 → 0.81  
**React:** 19.0.0 → 19.1.0  
**expo-router:** ~5.0.x → ~6.0.x  
**react-native-reanimated:** ~3.17.x → ~4.1.x  
**react-native-worklets:** (not present) → ~0.5.x ← **new required peer dep**  
**New Architecture:** default (LAST SDK where `newArchEnabled: false` opt-out is allowed)

> SDK 54 is the last SDK supporting Legacy Architecture. SDK 55 removes it entirely.
> Plan the New Arch migration now.

---

## Phase A — Fast import audit

```bash
REANIMATED_FILES=$(grep -rln \
  "from 'react-native-reanimated'\|from \"react-native-reanimated\"" \
  --include="*.tsx" --include="*.ts" --include="*.js" --include="*.jsx" \
  src/ app/ components/ hooks/ screens/ lib/ 2>/dev/null \
  || grep -rln \
  "from 'react-native-reanimated'\|from \"react-native-reanimated\"" \
  --include="*.tsx" --include="*.ts" --include="*.js" --include="*.jsx" \
  --exclude-dir=node_modules --exclude-dir=.expo .)

ROUTER_FILES=$(grep -rln "from 'expo-router'\|from \"expo-router\"" \
  --include="*.tsx" --include="*.ts" --include="*.js" --include="*.jsx" \
  src/ app/ components/ hooks/ screens/ lib/ 2>/dev/null \
  || grep -rln "from 'expo-router'\|from \"expo-router\"" \
  --include="*.tsx" --include="*.ts" \
  --exclude-dir=node_modules --exclude-dir=.expo .)

RN_IMPORT_FILES=$(grep -rln "from 'react-native'\|from \"react-native\"" \
  --include="*.tsx" --include="*.ts" --include="*.js" --include="*.jsx" \
  src/ app/ components/ hooks/ screens/ lib/ 2>/dev/null \
  || grep -rln "from 'react-native'\|from \"react-native\"" \
  --include="*.tsx" --include="*.ts" \
  --exclude-dir=node_modules --exclude-dir=.expo .)

FS_FILES=$(grep -rln "from 'expo-file-system'\|from \"expo-file-system\"" \
  --include="*.tsx" --include="*.ts" --include="*.js" \
  src/ app/ components/ hooks/ screens/ lib/ 2>/dev/null \
  || grep -rln "from 'expo-file-system'" \
  --include="*.tsx" --include="*.ts" \
  --exclude-dir=node_modules --exclude-dir=.expo .)

NAV_FILES=$(grep -rln "from '@react-navigation/" \
  --include="*.tsx" --include="*.ts" --include="*.js" \
  src/ app/ components/ hooks/ screens/ lib/ 2>/dev/null \
  || grep -rln "from '@react-navigation/" \
  --include="*.tsx" --include="*.ts" \
  --exclude-dir=node_modules --exclude-dir=.expo .)
```

Also check `babel.config.js` and `app.json` directly — neither is covered by the above.

---

## Phase B — Per-issue targeted scans

---

### react-native-reanimated 3 → 4

---

#### [CRITICAL] `executeOnUIRuntimeSync` removed — runtime error

Removed entirely. Produces "executeOnUIRuntimeSync is not a function" at runtime.

```bash
echo "$REANIMATED_FILES" | xargs grep -n "executeOnUIRuntimeSync"
```

Fix: replace with `runOnUISync`.

---

#### [CRITICAL] `makeShareableCloneRecursive` removed — runtime error

```bash
echo "$REANIMATED_FILES" | xargs grep -n "makeShareableCloneRecursive"
```

Fix: replace with `createSerializable`.

---

#### [CRITICAL] `useWorkletCallback` removed — runtime error

```bash
echo "$REANIMATED_FILES" | xargs grep -n "useWorkletCallback\s*("
```

Fix: use `useCallback` with a `'worklet';` directive inside the callback body.
```tsx
// Before
const handler = useWorkletCallback(() => { doSomething(); });

// After
const handler = useCallback(() => {
  'worklet';
  doSomething();
}, []);
```

---

#### [CRITICAL] `useAnimatedGestureHandler` removed — runtime error

```bash
echo "$REANIMATED_FILES" | xargs grep -n "useAnimatedGestureHandler\s*("
```

**Failure mode:** "useAnimatedGestureHandler is not a function"  
Fix: migrate to Gesture Handler 2's `Gesture` API with `useAnimatedReaction` or
`useSharedValue` + `GestureDetector`.

---

#### [CRITICAL] `combineTransition` removed — runtime error

```bash
echo "$REANIMATED_FILES" | xargs grep -n "combineTransition\s*("
```

Fix: use `EntryExitTransition.entering(MyEntering).exiting(MyExiting)`.

---

#### [CRITICAL] `addWhitelistedNativeProps` / `addWhitelistedUIProps` removed

These were no-ops in v3 already, but calling them in v4 throws.

```bash
echo "$REANIMATED_FILES" | xargs grep -n \
  "addWhitelistedNativeProps\|addWhitelistedUIProps"
```

Fix: delete the calls entirely.

---

#### [HIGH] `withSpring` config — `restDisplacementThreshold` / `restSpeedThreshold` removed

These spring config properties are replaced by `energyThreshold`.
No TypeScript error (extra object keys are ignored in JS), but the spring
behavior will differ from what was tuned — **silent visual regression**.

```bash
echo "$REANIMATED_FILES" | xargs grep -n \
  "restDisplacementThreshold\|restSpeedThreshold"
```

Fix:
```tsx
// Before
withSpring(value, { restDisplacementThreshold: 0.01, restSpeedThreshold: 0.01 })
// After
withSpring(value, { energyThreshold: 0.01 })
```

---

#### [MEDIUM] `runOnJS` / `runOnUI` / `runOnRuntime` — deprecated, renamed

These are re-exported in v4 with their old names but emit console warnings.
Will be removed in a future version.

```bash
echo "$REANIMATED_FILES" | xargs grep -n \
  "\brunOnJS\b\|\brunOnUI\b\|\brunOnRuntime\b"
```

Fix: rename to `scheduleOnRN`, `scheduleOnUI`, `scheduleOnRuntime` respectively.

---

#### [MEDIUM] `useScrollViewOffset` deprecated — renamed

Re-exported with old name but warns.

```bash
echo "$REANIMATED_FILES" | xargs grep -n "useScrollViewOffset\s*("
```

Fix: rename to `useScrollOffset`.

---

#### [MEDIUM] Babel plugin — `react-native-reanimated/plugin` in manual config

Only relevant if `babel.config.js` manually specifies the plugin (not using
`babel-preset-expo`). The plugin must change to `react-native-worklets/plugin`.

```bash
grep -n "react-native-reanimated/plugin" babel.config.js babel.config.ts 2>/dev/null
```

**Failure mode:** Metro startup error or missing worklet compilation.  
Fix: change to `'react-native-worklets/plugin'` and ensure it's the last plugin.

---

#### [HIGH] `react-native-worklets` missing — worklet runtime crash

If `react-native-reanimated` ~4.x is installed but `react-native-worklets` is
not, any worklet will crash at runtime: "Worklets runtime not available".

```bash
node -e "const p=require('./package.json'); console.log(p.dependencies['react-native-worklets'] || p.devDependencies?.['react-native-worklets'] || 'MISSING')"
```

Fix: `npx expo install react-native-worklets`

---

### expo-router 6.0

---

#### [HIGH] Direct `@react-navigation/*` imports — Module not found

expo-router 6 removed `@react-navigation` as a peer dependency. Direct imports
fail with "Cannot find module '@react-navigation/native'" or similar.

```bash
echo "$NAV_FILES" | xargs grep -n "from '@react-navigation/"
```

For each result: check if the same symbol is re-exported by `expo-router`.
If yes, switch to `expo-router`. If not, install the `@react-navigation` package
explicitly and verify version compatibility.

---

#### [MEDIUM] `Stack.Screen.Title` → `Stack.Title`

Deprecated alias exists in v6 but logs a warning. Removed in v7 (SDK 56).

```bash
echo "$ROUTER_FILES" | xargs grep -n "Stack\.Screen\.Title"
```

Fix: rename to `Stack.Title`.

---

#### [MEDIUM] `NativeTabs.Trigger.options` replaced

```bash
echo "$ROUTER_FILES" | xargs grep -n \
  "NativeTabs\.Trigger\.options\|NativeTabs\.Trigger\.TabBar"
```

Fix: `NativeTabs.Trigger.options` → `unstable_nativeProps`; `NativeTabs.Trigger.TabBar` removed.

---

### expo-file-system API change — MEDIUM

The default export of `expo-file-system` is now the new "next" API. Code
written against the old API will get TS errors on missing methods or different
return types.

```bash
echo "$FS_FILES" | xargs grep -n \
  "FileSystem\.readAsStringAsync\|FileSystem\.writeAsStringAsync\|FileSystem\.downloadAsync\|FileSystem\.deleteAsync\|FileSystem\.moveAsync\|FileSystem\.copyAsync\|FileSystem\.makeDirectoryAsync\|FileSystem\.readDirectoryAsync\|FileSystem\.getInfoAsync\|FileSystem\.documentDirectory\|FileSystem\.cacheDirectory"
```

**Failure mode:** TS2339 if using removed methods; undefined at runtime if relying
on removed properties.  
Fix options:
- Switch import to `expo-file-system/legacy` to keep the old API unchanged during migration.
- Migrate to the new API (check the expo-file-system changelog for the new method names).

---

### SafeAreaView from `react-native` deprecated — LOW

```bash
# Find files that import SafeAreaView from react-native (not from react-native-safe-area-context)
echo "$RN_IMPORT_FILES" | xargs grep -n "SafeAreaView" | grep "from 'react-native'\|from \"react-native\""
```

Note: the above won't work reliably because the import and usage are on different lines.
Use this two-step approach instead:

```bash
# Step 1: files that import SafeAreaView from react-native
grep -rln "SafeAreaView" --include="*.tsx" --include="*.ts" src/ app/ 2>/dev/null \
  | xargs grep -ln "from 'react-native'"

# Step 2: check those files for actual SafeAreaView usage
# (run manually against each file returned by step 1)
grep -n "SafeAreaView\|from 'react-native'" FILE
```

Fix:
```tsx
// Before
import { SafeAreaView } from 'react-native';
// After
import { SafeAreaView } from 'react-native-safe-area-context';
```

---

### app.json changes

```bash
# enableProguardInReleaseBuilds → enableMinifyInReleaseBuilds
grep -n "enableProguardInReleaseBuilds" app.json app.config.js app.config.ts 2>/dev/null

# notification field deprecated (must move to expo-notifications plugin)
grep -n '"notification"' app.json app.config.js app.config.ts 2>/dev/null
```

---

### Summary table

| Pattern | Failure mode | Severity |
|---|---|---|
| `executeOnUIRuntimeSync` | "is not a function" runtime crash | CRITICAL |
| `makeShareableCloneRecursive` | "is not a function" runtime crash | CRITICAL |
| `useWorkletCallback(` | "is not a function" runtime crash | CRITICAL |
| `useAnimatedGestureHandler(` | "is not a function" runtime crash | CRITICAL |
| `combineTransition(` | "is not a function" runtime crash | CRITICAL |
| `addWhitelistedNativeProps/UIProps` | runtime crash on call | CRITICAL |
| `restDisplacementThreshold` / `restSpeedThreshold` in `withSpring` | silent visual regression (spring tuning ignored) | HIGH |
| `react-native-worklets` missing | "Worklets runtime not available" crash | HIGH |
| `@react-navigation/*` direct import | "Cannot find module" Metro failure | HIGH |
| `react-native-reanimated/plugin` in babel | Metro startup error | MEDIUM |
| `runOnJS` / `runOnUI` / `runOnRuntime` | Console deprecation warning | MEDIUM |
| `useScrollViewOffset(` | Console deprecation warning | MEDIUM |
| `Stack.Screen.Title` | Console warning now, crash in SDK 56 | MEDIUM |
| `expo-file-system` old API | TS errors or undefined at runtime | MEDIUM |
| `SafeAreaView` from `react-native` | Deprecation warning | LOW |

---

## Third-party packages — SDK 53 → 54

See `checks/third-party-packages.md` for the full compatibility matrix and migration notes.

### Phase A — 3rd party import audit

```bash
THIRD_PARTY_FILES=$(grep -rln \
  "@gorhom/bottom-sheet\|@shopify/flash-list\|nativewind\|react-native-mmkv\|@react-native-firebase\|react-native-vision-camera\|moti\b\|react-native-maps\|react-native-svg\|react-native-screens" \
  --include="*.tsx" --include="*.ts" --include="*.js" --include="*.jsx" \
  src/ app/ components/ hooks/ screens/ lib/ 2>/dev/null \
  || grep -rln \
  "@gorhom/bottom-sheet\|@shopify/flash-list\|nativewind\|react-native-mmkv\|@react-native-firebase\|react-native-vision-camera\|moti\b\|react-native-maps\|react-native-svg" \
  --include="*.tsx" --include="*.ts" --include="*.js" --include="*.jsx" \
  --exclude-dir=node_modules --exclude-dir=.expo .)
```

### Version checks

```bash
node -e "
const p = require('./package.json');
const deps = { ...p.dependencies, ...p.devDependencies };
const check = (name, note) => console.log(name + ': ' + (deps[name] || 'not installed') + '  ' + note);
check('@shopify/flash-list', '← MUST be 2.0.2 for SDK 54 (New Arch only)');
check('@gorhom/bottom-sheet', '← MUST be 5.1.8+ for Reanimated v4');
check('nativewind', '← MUST be 4.2.1+ (NOT 4.2.0, NOT < 4.2.0)');
check('react-native-mmkv', '← v3+ for New Arch');
check('@react-native-async-storage/async-storage', '← stay on 2.2.0, NOT v3');
check('react-native-vision-camera', '← v4 still valid; v5 available');
check('react-native-maps', '← 1.20.1 expected');
check('react-native-svg', '← 15.12.1 expected');
"
```

### [CRITICAL] nativewind < 4.2.0 — all className styling silently breaks

This is the most dangerous silent regression in the SDK 53→54 hop.
Reanimated v4 (required by SDK 54) conflicts with nativewind < 4.2.0 at the
Babel plugin level. Result: every `className` prop renders with no styles applied.
**No error, no warning** — the UI just appears completely unstyled.

```bash
# Check installed version
node -e "const p=require('./package.json'); console.log('nativewind:', p.dependencies?.['nativewind'] || p.devDependencies?.['nativewind'] || 'not installed')"

# Find all files using className (scope of impact)
echo "$THIRD_PARTY_FILES" | xargs grep -n "className="
grep -rln "className=" \
  --include="*.tsx" --include="*.jsx" \
  src/ app/ components/ screens/ lib/ 2>/dev/null | wc -l
```

Fix: `npm install nativewind@^4.2.1 tailwindcss@3.4.17`  
⚠️ Do NOT use `tailwindcss@4.x` — incompatible with nativewind v4.

### [CRITICAL] @shopify/flash-list v1 → v2 — runtime crash on New Arch

FlashList v2 is New Arch only. v1 on New Arch crashes at runtime:
`"FlashList v2.x has been designed to be new architecture only and will not run on old architecture"`

```bash
echo "$THIRD_PARTY_FILES" | xargs grep -n \
  "from '@shopify/flash-list'\|<FlashList\|MasonryFlashList\|FlashListRef"
```

v1 → v2 API changes you must fix after upgrading:
- Remove `estimatedItemSize` and `estimatedListSize` props (automatic in v2)
- `MasonryFlashList` → `<FlashList masonry>`
- Remove any `CellContainer` imports → use `View`
- Remove `onBlankArea`, `disableHorizontalListHeightMeasurement`, `disableAutoLayout` props
- Update ref type: `FlashList<T>` → `FlashListRef<T>`

```bash
# Find deprecated v1 API usage
echo "$THIRD_PARTY_FILES" | xargs grep -n \
  "estimatedItemSize\|estimatedListSize\|MasonryFlashList\|CellContainer\|onBlankArea\|disableHorizontalListHeightMeasurement\|disableAutoLayout\|FlashList<"
```

Fix: `npx expo install @shopify/flash-list`

### [CRITICAL] @gorhom/bottom-sheet < 5.1.8 — Reanimated v4 crash

Reanimated v4 (SDK 54 default) introduced worklets-package split. bottom-sheet < 5.1.8
was built against Reanimated v3 APIs that no longer exist. Result: crash on any
gesture interaction with the bottom sheet.

```bash
echo "$THIRD_PARTY_FILES" | xargs grep -n \
  "from '@gorhom/bottom-sheet'\|BottomSheet\b\|BottomSheetModal\b\|BottomSheetView\b\|BottomSheetScrollView\b"
```

Fix: `npm install @gorhom/bottom-sheet@^5.1.8`

### [HIGH] @react-native-firebase — iOS build failure (modular headers)

React Native 0.81 + Swift pods + Firebase = build failure:
```
The Swift pod FirebaseCrashlytics depends upon GoogleUtilities which does not define modules.
```

```bash
echo "$THIRD_PARTY_FILES" | xargs grep -n \
  "from '@react-native-firebase/"
```

Workaround — add to app.json `expo.plugins`:
```json
["expo-build-properties", {
  "ios": {
    "extraPodspecDependencies": {
      "CLANG_ALLOW_NON_MODULAR_INCLUDES_IN_FRAMEWORK_MODULES": "YES"
    }
  }
}]
```

Or if using a custom Podfile, add the `post_install` hook from `third-party-packages.md`.

### [HIGH] react-native-vision-camera — v4 archived

v4 is archived (no more fixes). If you must stay on v4 for SDK 54, it works but
you cannot get security fixes. Plan migration to v5.

```bash
echo "$THIRD_PARTY_FILES" | xargs grep -n "from 'react-native-vision-camera'"
```

v5 requires Nitro Modules: `npm install react-native-vision-camera@^5 react-native-nitro-modules react-native-nitro-image`

### [MEDIUM] react-native-svg 15.12.1 — `onPress` never fires on real Android

`onPress` on `<Path>` and other SVG primitives never fires on real Android devices
(works on emulator). Silent UX regression — no error.

```bash
echo "$THIRD_PARTY_FILES" | xargs grep -n \
  "onPress\s*=\|onPressIn\s*=\|onPressOut\s*=" | grep -v "node_modules"
```

If SVG elements have `onPress` handlers and the app targets Android physical devices:
document the known bug and consider using an absolute-positioned `TouchableOpacity`
over the SVG element as a workaround.

### [MEDIUM] moti — Reanimated v4 compatibility unconfirmed

moti's official docs reference Reanimated v2/v3. Reanimated v4 (SDK 54 default)
has API changes that moti may not have accounted for. Test all animated components
thoroughly before shipping.

```bash
echo "$THIRD_PARTY_FILES" | xargs grep -n "from 'moti'"
```

### 3rd party summary — SDK 54

| Package | Required action | Risk if skipped |
|---|---|---|
| nativewind | `npm install nativewind@^4.2.1` | ALL className styling silently broken |
| @shopify/flash-list | `npx expo install` (v1 → v2) | Runtime crash on New Arch |
| @gorhom/bottom-sheet | `npm install @gorhom/bottom-sheet@^5.1.8` | Crash on gesture interaction |
| @react-native-firebase (iOS) | Add modular headers workaround | EAS iOS build failure |
| react-native-vision-camera | Plan migration to v5 | No security fixes on v4 |
| react-native-svg + Android onPress | Document bug / workaround | Silent unresponsive touch targets |
| moti | Test all animated components | Unknown Reanimated v4 regressions |
