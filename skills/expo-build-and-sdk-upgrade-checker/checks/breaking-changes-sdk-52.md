# Breaking Changes: SDK 51 → 52

**React Native:** 0.74 → 0.76  
**React:** 18.2.0 → 18.3.1  
**expo-router:** ~3.5.x → ~4.0.x  
**react-native-reanimated:** ~3.10.x → ~3.16.x  
**New Architecture:** opt-in for existing projects (default only for new projects)

---

## Phase A — Fast import audit

Run once to get the file list. Feed these results into every Phase B command below.

```bash
# Store matched file list
ROUTER_FILES=$(grep -rln "from 'expo-router'\|from \"expo-router\"" \
  --include="*.tsx" --include="*.ts" --include="*.js" --include="*.jsx" \
  src/ app/ components/ hooks/ screens/ lib/ 2>/dev/null \
  || grep -rln "from 'expo-router'\|from \"expo-router\"" \
  --include="*.tsx" --include="*.ts" --include="*.js" --include="*.jsx" \
  --exclude-dir=node_modules --exclude-dir=.expo .)

CAMERA_FILES=$(grep -rln "expo-camera\|expo-barcode-scanner" \
  --include="*.tsx" --include="*.ts" --include="*.js" --include="*.jsx" \
  src/ app/ components/ hooks/ screens/ lib/ 2>/dev/null \
  || grep -rln "expo-camera\|expo-barcode-scanner" \
  --include="*.tsx" --include="*.ts" --include="*.js" --include="*.jsx" \
  --exclude-dir=node_modules --exclude-dir=.expo .)

AV_FILES=$(grep -rln "from 'expo-av'\|from \"expo-av\"" \
  --include="*.tsx" --include="*.ts" --include="*.js" --include="*.jsx" \
  src/ app/ components/ hooks/ screens/ lib/ 2>/dev/null \
  || grep -rln "from 'expo-av'\|from \"expo-av\"" \
  --include="*.tsx" --include="*.ts" --include="*.js" --include="*.jsx" \
  --exclude-dir=node_modules --exclude-dir=.expo .)
```

If a variable is empty, skip all Phase B patterns for that group.

---

## Phase B — Per-issue targeted scans

Each command below pipes Phase A results into a focused grep.  
Output format: `file:line:content` — exact location of every problem.

---

### expo-router 4.0

---

#### [HIGH] `Href<T>` generic removed — TypeScript error `TS2315`

`Href` is no longer generic. Any `Href<'/route'>`, `useRouter<Route>()`,
`Link<Props>`, `router.push<Route>()` produces TS2315 "Type is not generic."

```bash
echo "$ROUTER_FILES" | xargs grep -n \
  "Href<\|useRouter<\|router\.push<\|router\.replace<\|router\.navigate<\|<Link<\|useLocalSearchParams<\|useGlobalSearchParams<\|useSegments<"
```

Fix: remove the type parameter. Use typed route strings directly.

```tsx
// Before
const href: Href<'/profile'> = '/profile';
const params = useLocalSearchParams<{ id: string }>();

// After
const href: Href = '/profile';
const params = useLocalSearchParams<{ id: string }>();  // ← params generic is fine, it's Href that changed
```

---

#### [HIGH] `import type { Router, Route }` — renamed, removed in v5

`Router` → `ImperativeRouter`, `Route` → `RoutePath`. Aliases exist in v4 but
produce a deprecation warning and are removed in v5 (SDK 53 hop).

```bash
echo "$ROUTER_FILES" | xargs grep -n \
  "import.*\bRouter\b.*expo-router\|import.*\bRoute\b.*expo-router\|:\s*Router\b\|:\s*Route\b"
```

**Failure mode:** No error in SDK 52, but will break in the 52→53 hop.  
Fix: rename to `ImperativeRouter` / `RoutePath` now.

---

#### [HIGH] `router.navigate()` — silent behavioral regression

`router.navigate()` now always pushes a new screen. The old behavior (pop back
to an existing screen) is gone. This is a **runtime behavioral change** — no
compile error, no warning. Every call must be audited.

```bash
echo "$ROUTER_FILES" | xargs grep -n "router\.navigate("
```

For each result: if the intent was "go back to an existing screen in the stack,"
replace with `router.dismissTo('/route')`. If the intent was "push," no change needed.

---

#### [MEDIUM] Direct `@react-navigation/*` imports — may fail under v7

expo-router 4 uses React Navigation v7 internally. Direct imports from
`@react-navigation/native`, `@react-navigation/stack`, etc. may conflict.

```bash
grep -rn "from '@react-navigation/" \
  --include="*.tsx" --include="*.ts" --include="*.js" \
  --exclude-dir=node_modules .
```

**Failure mode:** Version conflict warnings; potentially duplicate navigator state.  
Fix: source all navigation primitives from `expo-router` instead.

---

### expo-camera

---

#### [CRITICAL] `expo-camera/legacy` removed — Module not found

`expo-camera/legacy` no longer exists in SDK 52. Import will fail at Metro
bundling: `Cannot resolve module 'expo-camera/legacy'`.

```bash
echo "$CAMERA_FILES" | xargs grep -n \
  "from 'expo-camera/legacy'\|from \"expo-camera/legacy\"\|from 'expo-camera/next'\|from \"expo-camera/next\""
```

Fix:
```tsx
// Before
import { Camera } from 'expo-camera/legacy';
// After
import { CameraView } from 'expo-camera';
```

---

#### [HIGH] `Camera` component (non-legacy) — should migrate to `CameraView`

Even the non-legacy `Camera` is deprecated. Any JSX use of `<Camera` or
`Camera.requestPermissionsAsync` (old API) should move to `CameraView` +
permission hooks.

```bash
echo "$CAMERA_FILES" | xargs grep -n \
  "import.*\bCamera\b.*expo-camera\|<Camera\b\|Camera\.requestPermissionsAsync\|Camera\.getCameraPermissionsAsync\|Camera\.Constants"
```

**Failure mode:** Deprecation warning in SDK 52; removed in a future SDK.

Fix:
```tsx
import { CameraView, useCameraPermissions } from 'expo-camera';
const [permission, requestPermission] = useCameraPermissions();
```

---

#### [HIGH] `onBarCodeScanned` prop renamed — prop silently ignored

Old prop: `onBarCodeScanned` (capital C). New prop: `onBarcodeScanned` (lowercase c).
The old prop is silently ignored — no error, no scan callback fires.

```bash
echo "$CAMERA_FILES" | xargs grep -n "onBarCodeScanned"
```

Fix: rename to `onBarcodeScanned`.

---

#### [CRITICAL] `expo-barcode-scanner` removed — Module not found

Package removed entirely. Use `CameraView` with `onBarcodeScanned` instead.

```bash
echo "$CAMERA_FILES" | xargs grep -n \
  "from 'expo-barcode-scanner'\|from \"expo-barcode-scanner\"\|require.*expo-barcode-scanner"
```

---

### expo-av

---

#### [MEDIUM] `expo-av` Video component deprecated

`Video` from `expo-av` works in SDK 52 but produces a deprecation warning.
Will be removed in SDK 55. Begin migration to `expo-video`.

```bash
echo "$AV_FILES" | xargs grep -n \
  "import.*\bVideo\b.*expo-av\|<Video\b\|ResizeMode\."
```

Fix:
```tsx
import { VideoView, useVideoPlayer } from 'expo-video';
const player = useVideoPlayer(source);
<VideoView player={player} contentFit="contain" />
```

---

### Platform minimums — check app.json

If `expo-build-properties` sets explicit minimums below the new floors, the
build will be rejected.

```bash
grep -n "deploymentTarget\|minSdkVersion\|compileSdkVersion\|targetSdkVersion" \
  app.json app.config.js app.config.ts 2>/dev/null
```

**New minimums:** iOS 15.1, Android minSdk 24, compileSdk/targetSdk 35.

---

### Summary table

| Pattern | Failure mode | Severity |
|---|---|---|
| `Href<T>` generics | TS2315 TypeScript error | HIGH |
| `Router`/`Route` type imports | Removed in v5 | MEDIUM (now), HIGH (next hop) |
| `router.navigate(` | Silent wrong-screen push | HIGH |
| `expo-camera/legacy` import | Metro bundle failure | CRITICAL |
| `Camera` (non-CameraView) usage | Deprecation now, removal later | HIGH |
| `onBarCodeScanned` prop | Silent no-op (callback never fires) | HIGH |
| `expo-barcode-scanner` import | Metro bundle failure | CRITICAL |
| `expo-av` Video/ResizeMode | Deprecation now, crash in SDK 55 | MEDIUM |

---

## Third-party packages — SDK 51 → 52

See `checks/third-party-packages.md` for the full compatibility matrix and migration notes.

### Phase A — 3rd party import audit

```bash
THIRD_PARTY_FILES=$(grep -rln \
  "@gorhom/bottom-sheet\|@shopify/flash-list\|react-native-maps\|react-native-mmkv\|nativewind" \
  --include="*.tsx" --include="*.ts" --include="*.js" --include="*.jsx" \
  src/ app/ components/ hooks/ screens/ lib/ 2>/dev/null \
  || grep -rln \
  "@gorhom/bottom-sheet\|@shopify/flash-list\|react-native-maps\|react-native-mmkv\|nativewind" \
  --include="*.tsx" --include="*.ts" --include="*.js" --include="*.jsx" \
  --exclude-dir=node_modules --exclude-dir=.expo .)
```

### Version checks (run in project root)

```bash
node -e "
const p = require('./package.json');
const deps = { ...p.dependencies, ...p.devDependencies };
const check = (name, note) => console.log(name + ': ' + (deps[name] || 'not installed') + '  ' + note);
check('@gorhom/bottom-sheet', '← v5.x required for stable New Arch support');
check('@shopify/flash-list', '← 1.7.3 expected for SDK 52');
check('react-native-maps', '← 1.18.0; New Arch on iOS is buggy at any version');
check('react-native-mmkv', '← v3+ requires New Arch; v2 safe on Old Arch only');
check('nativewind', '← must be v4.x');
check('react-native-gesture-handler', '← ~2.20.2 expected');
check('react-native-safe-area-context', '← 4.12.0 expected');
"
```

### [HIGH] @gorhom/bottom-sheet v4 — laggy / fails to open on iOS New Arch

If `newArchEnabled: true` (default for new SDK 52 projects) and bottom-sheet is v4:
bottom sheet is laggy or fails to fully open on iOS. No JavaScript error — silent UX breakage.

```bash
echo "$THIRD_PARTY_FILES" | xargs grep -n \
  "from '@gorhom/bottom-sheet'\|BottomSheet\b\|BottomSheetModal\b"
```

Check installed version. If v4 and New Arch is enabled, upgrade:
```bash
npm install @gorhom/bottom-sheet@^5.1.8
```

Post-upgrade: add `enableDynamicSizing={false}` to all `<BottomSheet>` and
`<BottomSheetModal>` instances to preserve v4 sizing behavior during migration.

### [HIGH] react-native-maps — crashes on iOS New Arch

On iOS with `newArchEnabled: true`, map re-renders after navigation crash the app.
No safe fix at SDK 52 — either keep New Arch disabled for this project or avoid
re-rendering maps after navigation.

```bash
echo "$THIRD_PARTY_FILES" | xargs grep -n \
  "from 'react-native-maps'\|<MapView\|<Marker\|<Polyline\|<Polygon"
```

If found and New Arch is on: flag as HIGH risk. Document the limitation in the report.

### [HIGH] react-native-mmkv v3+ — throws if New Arch is not enabled

v3+ is New Arch only. If the project hasn't opted into New Arch (`newArchEnabled: false`
or not set) and mmkv v3+ is installed, the app crashes at startup:
`"react-native-mmkv 3.x.x requires TurboModules"`

```bash
node -e "const p=require('./package.json'); const v=p.dependencies?.['react-native-mmkv']||p.devDependencies?.['react-native-mmkv']; console.log('mmkv version:', v||'not installed')"
grep -n "newArchEnabled" app.json app.config.js app.config.ts 2>/dev/null
```

If mmkv is v3+ and `newArchEnabled` is false or absent: CRITICAL mismatch.

### 3rd party summary — SDK 52

| Package | Required version | Risk if not updated |
|---|---|---|
| @gorhom/bottom-sheet | v5.x (if New Arch on) | Silent laggy/broken sheet on iOS |
| react-native-maps | 1.18.0 (pinned by expo) | iOS crash on map re-render with New Arch |
| react-native-mmkv | v2 (Old Arch) or v3+ (New Arch) | Startup crash if version/arch mismatch |
| nativewind | 4.x (not 2.x) | Build or styling failure |
| All Expo-pinned packages | run `npx expo install` | Silent version drift |
