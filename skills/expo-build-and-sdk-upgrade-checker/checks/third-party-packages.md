# Third-Party Package Compatibility: SDK 52 → 55

Quick-reference matrix for packages commonly used in Expo managed projects.
Load this file when planning any SDK upgrade to identify mandatory version bumps
and known bugs before touching a single package.

---

## Version matrix

| Package | SDK 52 | SDK 53 | SDK 54 | SDK 55 |
|---|---|---|---|---|
| react-native-gesture-handler | ~2.20.2 | ~2.24.0 | ~2.28.0 | ~2.30.0 |
| react-native-screens | ~4.4.0 | ~4.11.1 | ~4.16.0 | ~4.23.0 |
| react-native-safe-area-context | 4.12.0 | **5.4.0** ← major | ~5.6.0 | ~5.6.2 |
| react-native-svg | 15.8.0 | 15.11.2 | 15.12.1 | 15.15.3 |
| react-native-webview | 13.12.5 | 13.13.5 | 13.15.0 | 13.16.0 |
| react-native-maps | 1.18.0 | 1.20.1 | 1.20.1 | 1.27.2 ⚠️ |
| lottie-react-native | 7.1.0 | 7.2.2 | ~7.3.1 | ~7.3.4 |
| @shopify/flash-list | 1.7.3 | 1.7.6 | **2.0.2** ← New Arch only | 2.0.2 |
| @react-native-async-storage | 1.23.1 | **2.1.2** ← major | 2.2.0 | 2.2.0 |
| @gorhom/bottom-sheet | 4.x ⚠️ | **5.0.x** ← | **5.1.8+** ← reanimated v4 | 5.1.8+ |
| nativewind | 4.x | 4.x | **4.2.1+** ← critical | 4.2.1+ |
| react-native-mmkv | 2.x (Old Arch) / 3.x (New Arch) | 3.x | 3.x or 4.x | **3.x or 4.x** (v2 crashes) |
| @tanstack/react-query | 4.x or 5.x | **5.x** for React 19 | 5.x | 5.x |
| zustand | 4.x or 5.x | **5.x** for React 19 | 5.x | 5.x |
| react-native-vision-camera | 4.x | 4.x | 4.x or 5.x | **5.x** (v4 archived) |
| @shopify/react-native-skia | 1.x | **2.0+** for React 19 | 2.x | 2.x |
| react-native-paper | 5.x | 5.x | 5.x | 5.x |
| react-hook-form | 7.x | 7.x | 7.x | 7.x |
| @react-native-firebase/* | 20.x | 21.x+ | 21.x+ ⚠️ iOS | 21.x+ ⚠️ iOS |
| react-native-purchases | 9.x or 10.x | 10.x | 10.x | 10.x ⚠️ iOS 26 |
| moti | 0.29.x | 0.20.x ⚠️ web | test carefully | test carefully |

⚠️ = known active bug, see per-SDK section below.

---

## Install rule

Always use `npx expo install <package>` for packages that ship with Expo SDK
(gesture-handler, screens, safe-area-context, svg, webview, maps, lottie, flash-list,
async-storage). This pins the Expo-verified version.

For packages NOT in Expo's bundledNativeModules, use `npm install` with the
explicit version shown above.

```bash
# Packages that must be manually versioned (not SDK-pinned)
npm install @gorhom/bottom-sheet@^5.1.8
npm install nativewind@^4.2.1 tailwindcss@3.4.17   # NOT tailwindcss@4.x
npm install react-native-mmkv@^3                    # or @^4 + react-native-nitro-modules
npm install @tanstack/react-query@^5
npm install zustand@^5
npm install @shopify/react-native-skia@^2.0
```

---

## New Architecture blockers for SDK 55

SDK 55 removes the Legacy Architecture option entirely. These packages will
crash or fail to build if not addressed:

| Package | Error type | Exact error / symptom |
|---|---|---|
| @shopify/flash-list v1 | Runtime crash | "FlashList v2.x has been designed to be new architecture only and will not run on old architecture" |
| react-native-mmkv v2 | Runtime error | "react-native-mmkv 3.x.x requires TurboModules" |
| @react-native-async-storage v3 | Build failure | Not compatible with SDK 54+ — stay on 2.2.0 |
| react-native-maps (Google Maps iOS) | EAS build failure | "[ios.appDelegate]: withIosAppDelegateBaseMod: Cannot add Google Maps to the project's AppDelegate because it's malformed" |
| @react-native-firebase (Analytics/Crashlytics) iOS | EAS build failure | "The Swift pod FirebaseCrashlytics depends upon GoogleUtilities which does not define modules" |
| react-native-purchases (iOS 26) | Runtime crash | SIGABRT/SIGSEGV before JavaScript runs |
| react-native-vision-camera v4 | Archived, no fixes | Use v5 instead |

---

## Per-SDK notable issues

### SDK 52
- `@gorhom/bottom-sheet` v4 on iOS New Arch: bottom sheet laggy, fails to fully open
- `react-native-maps` on iOS New Arch: app crashes on re-render after navigation
- `react-native-mmkv` v3+ throws if New Arch is not enabled

### SDK 53
- `react-native-safe-area-context` jumps 4.12.0 → 5.4.0 (major version — run `npx expo install`)
- `@react-native-async-storage` jumps 1.23.1 → 2.1.2 (major version — run `npx expo install`)
- `@react-native-firebase` + Metro `package.json exports`: add `unstable_enablePackageExports: false` to `metro.config.js` to fix import failures
- `@shopify/react-native-skia` must be v2.0+ for React 19 compatibility
- `lottie-react-native`: `.lottie` dotLottie format files don't render on Android in Expo Go
- `react-native-svg`: Android build compile time significantly increased
- `moti` 0.20.0: web crash (`__extends of _tslib.default is undefined`) with RN 0.79

### SDK 54
- **nativewind < 4.2.0**: All className styling silently breaks — no error, UI appears completely unstyled
- **@shopify/flash-list v1 → v2**: Runtime crash on Old Arch; v2 is New Arch only
- **@gorhom/bottom-sheet < 5.1.8**: Incompatible with Reanimated v4 — crashes
- `@react-native-firebase` iOS: Swift pod modular headers build failure (RN 0.81)
- `react-native-screens` 4.16.0 with `useFrameworks: 'static'`: iOS build failure (missing headers)
- `react-native-maps` Android: custom `<Marker>` children invisible or flickering
- `react-native-svg` 15.12.1: `onPress` on Path elements never fires on real Android device

### SDK 55
- `react-native-maps` 1.27.2: Google Maps iOS config plugin regex breaks EAS build entirely
- `@react-native-firebase` iOS issues continue
- `react-native-purchases` + iOS 26 + New Arch: SIGABRT crash on launch
- `moti`: Reanimated v4 compatibility unconfirmed — test before committing to SDK 55

---

## Key package-specific migration notes

### @gorhom/bottom-sheet v4 → v5

v5 rewrites the gesture solution for Gesture Handler v2. Breaking changes:
- `enableDynamicSizing` now defaults to `true` (was `false`) — sheets will unexpectedly resize. Set `enableDynamicSizing={false}` during migration to maintain v4 behavior.
- `stackBehavior` default changed to `switch`

```bash
npm install @gorhom/bottom-sheet@^5.1.8
npx expo install react-native-reanimated react-native-gesture-handler
```

### @shopify/flash-list v1 → v2

v2 is New Architecture only — Old Arch is a hard runtime crash.

Breaking API changes:
- `estimatedItemSize` / `estimatedListSize` props removed (automatic sizing)
- `MasonryFlashList` deprecated → use `<FlashList masonry>` prop
- `CellContainer` no longer exported → use `View`
- `onBlankArea`, `disableHorizontalListHeightMeasurement`, `disableAutoLayout` props removed
- Ref type: `FlashList<T>` → `FlashListRef<T>`

```bash
npx expo install @shopify/flash-list
```

### nativewind < 4.2.0 (SDK 54+)

Reanimated v4 (required for SDK 54) causes a Babel plugin conflict with nativewind < 4.2.0.
Result: all `className` styling silently produces no styles — UI appears unstyled with no errors.

```bash
npm install nativewind@^4.2.1 tailwindcss@3.4.17
# Never tailwindcss@4.x with nativewind
```

### react-native-mmkv v2 → v3

v3 is New Arch only (pure CxxTurboModule). No callback-based API changes.
v4 adds NitroModules and renames some APIs:
- `new MMKV()` → `createMMKV()`
- `storage.delete('key')` → `storage.remove('key')`
- Info.plist `AppGroup` → `AppGroupIdentifier`

⚠️ Data loss risk on iOS with App Groups when migrating v2 → v3.

### @react-native-async-storage v3 — do NOT upgrade on Expo

v3 is incompatible with SDK 54+. Stay on v2.2.0.
`npx expo install @react-native-async-storage/async-storage` pins correctly to 2.2.0.

### @tanstack/react-query v4 → v5

All hook overloads collapsed to single options object:
```tsx
// Before (v4)
useQuery(['key'], fetchFn, { staleTime: 5000 })
// After (v5)
useQuery({ queryKey: ['key'], queryFn: fetchFn, staleTime: 5000 })
```
`isLoading` → `isPending`; `status: 'loading'` → `status: 'pending'`

### @react-native-firebase — Metro exports workaround (SDK 53+)

Add to `metro.config.js`:
```js
const { getDefaultConfig } = require('expo/metro-config');
const config = getDefaultConfig(__dirname);
config.resolver.unstable_enablePackageExports = false;
return config;
```

### react-native-vision-camera v4 → v5

v4 is archived. v5 requires Nitro Modules (New Arch + RN 0.78+).

Breaking changes (v4 → v5):
- `format` prop + `useCameraFormat()` / `formats` API removed → use Constraints API
- `photo={true}` / `video={true}` props removed → use `usePhotoOutput()` / `useVideoOutput()` hooks
- Photos no longer written to disk automatically — returned as in-memory objects
- Frame processors use `react-native-worklets` via Nitro

```bash
npm install react-native-vision-camera@^5 react-native-nitro-modules react-native-nitro-image
```
