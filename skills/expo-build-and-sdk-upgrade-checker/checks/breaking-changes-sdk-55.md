# Breaking Changes: SDK 54 → 55

**React Native:** 0.81 → 0.83  
**React:** 19.1.0 → 19.2.0  
**expo-router:** ~6.0.x → ~55.0.x (unified versioning)  
**react-native-reanimated:** ~4.1.x → ~4.3.x  
**react-native-worklets:** ~0.5.x → ~0.8.x  
**New Architecture:** MANDATORY — Legacy Architecture permanently removed

> If still on Legacy Architecture in SDK 54, complete the New Arch migration first.
> Attempting SDK 55 on Legacy Arch produces a build-time error.

---

## Phase A — Fast import audit

```bash
# expo-av — CRITICAL, must be zero
AV_FILES=$(grep -rln "from 'expo-av'\|from \"expo-av\"\|require.*expo-av" \
  --include="*.tsx" --include="*.ts" --include="*.js" --include="*.jsx" \
  src/ app/ components/ hooks/ screens/ lib/ 2>/dev/null \
  || grep -rln "from 'expo-av'\|from \"expo-av\"" \
  --include="*.tsx" --include="*.ts" --include="*.js" \
  --exclude-dir=node_modules --exclude-dir=.expo .)

# expo-video — check for removed props
VIDEO_FILES=$(grep -rln "from 'expo-video'\|from \"expo-video\"" \
  --include="*.tsx" --include="*.ts" --include="*.js" \
  src/ app/ components/ hooks/ screens/ lib/ 2>/dev/null \
  || grep -rln "from 'expo-video'" \
  --include="*.tsx" --include="*.ts" \
  --exclude-dir=node_modules --exclude-dir=.expo .)

# expo-router — check for removed types and props
ROUTER_FILES=$(grep -rln "from 'expo-router'\|from \"expo-router\"" \
  --include="*.tsx" --include="*.ts" --include="*.js" \
  src/ app/ components/ hooks/ screens/ lib/ 2>/dev/null \
  || grep -rln "from 'expo-router'" \
  --include="*.tsx" --include="*.ts" \
  --exclude-dir=node_modules --exclude-dir=.expo .)

# expo-blur
BLUR_FILES=$(grep -rln "from 'expo-blur'\|from \"expo-blur\"" \
  --include="*.tsx" --include="*.ts" \
  src/ app/ components/ screens/ lib/ 2>/dev/null \
  || grep -rln "from 'expo-blur'" \
  --include="*.tsx" --include="*.ts" \
  --exclude-dir=node_modules --exclude-dir=.expo .)

# expo-clipboard
CLIPBOARD_FILES=$(grep -rln "from 'expo-clipboard'\|from \"expo-clipboard\"" \
  --include="*.tsx" --include="*.ts" \
  src/ app/ components/ hooks/ screens/ lib/ 2>/dev/null \
  || grep -rln "from 'expo-clipboard'" \
  --include="*.tsx" --include="*.ts" \
  --exclude-dir=node_modules --exclude-dir=.expo .)

# expo-video-thumbnails — deprecated package
VT_FILES=$(grep -rln "from 'expo-video-thumbnails'\|from \"expo-video-thumbnails\"" \
  --include="*.tsx" --include="*.ts" --include="*.js" \
  src/ app/ components/ hooks/ screens/ lib/ 2>/dev/null \
  || grep -rln "from 'expo-video-thumbnails'" \
  --include="*.tsx" --include="*.ts" \
  --exclude-dir=node_modules --exclude-dir=.expo .)

# @expo/ui component renames
EXPO_UI_FILES=$(grep -rln "from '@expo/ui'\|from \"@expo/ui\"" \
  --include="*.tsx" --include="*.ts" \
  src/ app/ components/ screens/ lib/ 2>/dev/null \
  || grep -rln "from '@expo/ui'" \
  --include="*.tsx" --include="*.ts" \
  --exclude-dir=node_modules --exclude-dir=.expo .)
```

---

## Phase B — Per-issue targeted scans

---

### expo-av — CRITICAL (runtime crash in Expo Go and production)

`expo-av` is removed from Expo Go and the SDK entirely. Any import causes an
immediate module resolution failure: "Cannot find module 'expo-av'" or a runtime
crash if bundled via a stale native build.

**These must be zero before building.**

---

#### [CRITICAL] `expo-av` Video usage

```bash
echo "$AV_FILES" | xargs grep -n \
  "import.*\bVideo\b.*expo-av\|from 'expo-av'.*Video\|ResizeMode\.\|<Video\b\|\bVideo\.presentFullscreenPlayer\|\bVideo\.dismissFullscreenPlayer"
```

**Failure mode:** "Unable to resolve module 'expo-av'" at Metro; or native crash
if using a stale dev client.

Migration:
```tsx
// Before
import { Video, ResizeMode } from 'expo-av';
<Video source={{ uri }} resizeMode={ResizeMode.CONTAIN} useNativeControls />

// After
import { VideoView, useVideoPlayer } from 'expo-video';
const player = useVideoPlayer({ uri }, p => { p.loop = false; });
<VideoView player={player} contentFit="contain" nativeControls />
```

---

#### [CRITICAL] `expo-av` Audio usage

```bash
echo "$AV_FILES" | xargs grep -n \
  "import.*\bAudio\b.*expo-av\|Audio\.Sound\.\|Audio\.setAudioModeAsync\|Audio\.requestPermissionsAsync\|Audio\.getPermissionsAsync\|Audio\.Recording\."
```

Migration:
```tsx
// Before
import { Audio } from 'expo-av';
const { sound } = await Audio.Sound.createAsync(require('./sound.mp3'));
await Audio.setAudioModeAsync({ allowsRecordingIOS: true });

// After
import { useAudioPlayer, setAudioModeAsync } from 'expo-audio';
const player = useAudioPlayer(require('./sound.mp3'));
await setAudioModeAsync({ allowsRecordingIOS: true });
```

---

#### [CRITICAL] Any remaining `expo-av` import

Catch-all for any other usage:

```bash
echo "$AV_FILES" | xargs grep -n "from 'expo-av'\|from \"expo-av\"\|require.*expo-av"
```

Zero results required before proceeding.

---

### expo-video API change — MEDIUM

---

#### [MEDIUM] `allowsFullscreen` prop removed

`allowsFullscreen` on `<VideoView>` is removed. Prop is silently ignored in SDK 54
but in SDK 55 it produces a TS error: `TS2322: Type '{ allowsFullscreen: boolean }'
is not assignable`.

```bash
echo "$VIDEO_FILES" | xargs grep -n "allowsFullscreen"
```

Fix:
```tsx
// Before
<VideoView player={player} allowsFullscreen />
// After
<VideoView player={player} fullscreenOptions={{ enable: true }} />
```

---

### expo-router — MEDIUM

---

#### [MEDIUM] `ExpoRequest` / `ExpoResponse` removed from `expo-router/server`

Produces TS2305 "Module 'expo-router/server' has no exported member 'ExpoRequest'".

```bash
echo "$ROUTER_FILES" | xargs grep -n "ExpoRequest\|ExpoResponse"
```

Fix: use the standard Web globals `Request` and `Response` directly.
```tsx
// Before
import { ExpoRequest, ExpoResponse } from 'expo-router/server';
export async function GET(req: ExpoRequest): Promise<ExpoResponse> { ... }

// After
export async function GET(req: Request): Promise<Response> { ... }
```

---

#### [MEDIUM] `Stack.Screen.Title` — deprecated alias removed in v7 (SDK 56)

```bash
echo "$ROUTER_FILES" | xargs grep -n "Stack\.Screen\.Title"
```

Fix: rename to `Stack.Title`.

---

#### [MEDIUM] `reset` prop on `<Tabs>` — renamed to `resetOnFocus`

The `reset` prop is renamed. Old name silently ignored — tab does not reset on
focus, a behavioral regression with no error.

```bash
echo "$ROUTER_FILES" | xargs grep -n "<Tabs[^>]*\breset\b\|<Tabs[^>]*\sreset="
```

Fix: rename prop to `resetOnFocus`.

---

### expo-blur — LOW

---

#### [LOW] `experimentalBlurMethod` renamed to `blurMethod`

Produces TS2322 "Property 'experimentalBlurMethod' does not exist" in strict mode;
silently ignored otherwise.

```bash
echo "$BLUR_FILES" | xargs grep -n "experimentalBlurMethod"
```

Fix: rename to `blurMethod`.

---

### expo-clipboard — LOW

---

#### [LOW] `content` property removed from clipboard change event

The `content` property on clipboard listener callbacks is removed. Accessing it
returns `undefined` silently.

```bash
echo "$CLIPBOARD_FILES" | xargs grep -n \
  "addClipboardListener\|onClipboardChange\|clipboardEvent\|\.content\b"
```

Inspect each match: if the callback accesses `event.content`, replace with
`Clipboard.getStringAsync()` inside the callback instead.

---

### expo-video-thumbnails deprecated

---

#### [MEDIUM] `expo-video-thumbnails` package deprecated

```bash
echo "$VT_FILES" | xargs grep -n \
  "from 'expo-video-thumbnails'\|getThumbnailAsync"
```

Fix: use `generateThumbnailsAsync` from `expo-video` instead.
```tsx
// Before
import { getThumbnailAsync } from 'expo-video-thumbnails';
// After
import { generateThumbnailsAsync } from 'expo-video';
```

---

### @expo/ui component renames — if used

---

#### [HIGH] Renamed component names — TS2305 / React "Unknown element" warning

```bash
echo "$EXPO_UI_FILES" | xargs grep -n \
  "\bDateTimePicker\b\|\bSwitch\b\|\bCircularProgress\b\|\bLinearProgress\b"
```

| Old name | New name | Failure mode |
|---|---|---|
| `DateTimePicker` | `DatePicker` | TS2305 or runtime "Unknown element" |
| `Switch` | `Toggle` | TS2305 (also conflicts with RN's `Switch`) |
| `CircularProgress` | `ProgressView` | TS2305 |
| `LinearProgress` | `ProgressView` | TS2305 |

---

### New Architecture mandatory — CRITICAL

---

#### [CRITICAL] `newArchEnabled: false` still present

SDK 55 ignores and removes this option. If your app has not been migrated to
New Architecture, it will fail to build or crash at startup.

```bash
grep -n "newArchEnabled" app.json app.config.js app.config.ts 2>/dev/null
```

If `newArchEnabled: false` is found: stop the SDK 55 upgrade. Return to SDK 54,
set `newArchEnabled: true`, fix all New Arch issues, ship a build, then upgrade.

---

### app.json removed fields — check config files directly

```bash
# notification field removed (must be in expo-notifications plugin config)
grep -n '"notification"' app.json app.config.js app.config.ts 2>/dev/null

# edgeToEdgeEnabled removed — edge-to-edge mandatory on Android 16+
grep -n "edgeToEdgeEnabled" app.json app.config.js app.config.ts 2>/dev/null

# newArchEnabled option removed entirely
grep -n "newArchEnabled" app.json app.config.js app.config.ts 2>/dev/null
```

**Failure mode for `notification` field:** Field silently ignored, notification
configuration (icon, color, sounds) not applied — production regression with no
error.

---

### package.json scripts — `eas update` flag change

---

#### [LOW] `eas update` without `--environment` flag

`eas update` now requires `--environment` to specify the target environment.
Check package.json scripts for bare `eas update` calls.

```bash
grep -n "eas update" package.json
```

Fix: add `--environment preview` or `--environment production` to the command.

---

### Summary table

| Pattern | Failure mode | Severity |
|---|---|---|
| Any `from 'expo-av'` import | "Cannot find module" Metro crash or native crash | CRITICAL |
| `newArchEnabled: false` in config | Build failure or startup crash on SDK 55 | CRITICAL |
| `allowsFullscreen` on `VideoView` | TS2322 TypeScript error | MEDIUM |
| `ExpoRequest` / `ExpoResponse` imports | TS2305 "no exported member" | MEDIUM |
| `Stack.Screen.Title` | Crash in SDK 56 | MEDIUM |
| `reset=` on `<Tabs>` | Silent behavioral regression (tab never resets) | MEDIUM |
| `expo-video-thumbnails` import | Deprecated package, future removal | MEDIUM |
| `DateTimePicker`/`Switch`/`CircularProgress`/`LinearProgress` from `@expo/ui` | TS2305 or "Unknown element" | HIGH |
| `experimentalBlurMethod=` | TS2322 or silently ignored | LOW |
| `event.content` in clipboard listener | `undefined` silently | LOW |
| `"notification"` in app.json root | Config silently ignored | MEDIUM |
| `edgeToEdgeEnabled` in app.json | Field removed, silently ignored | LOW |
| `eas update` without `--environment` | CLI error "environment required" | LOW |

---

## Third-party packages — SDK 54 → 55

See `checks/third-party-packages.md` for the full compatibility matrix and migration notes.
SDK 55 mandates New Architecture — any package not yet on Fabric/TurboModules will
crash or fail to build.

### Phase A — 3rd party import audit

```bash
THIRD_PARTY_FILES=$(grep -rln \
  "@gorhom/bottom-sheet\|@shopify/flash-list\|react-native-mmkv\|react-native-maps\|@react-native-firebase\|react-native-purchases\|react-native-vision-camera\|moti\b\|nativewind\|@react-native-async-storage\|react-native-ui-lib" \
  --include="*.tsx" --include="*.ts" --include="*.js" --include="*.jsx" \
  src/ app/ components/ hooks/ screens/ lib/ 2>/dev/null \
  || grep -rln \
  "@gorhom/bottom-sheet\|@shopify/flash-list\|react-native-mmkv\|react-native-maps\|@react-native-firebase\|react-native-purchases\|react-native-vision-camera\|moti\b\|nativewind\|@react-native-async-storage" \
  --include="*.tsx" --include="*.ts" --include="*.js" --include="*.jsx" \
  --exclude-dir=node_modules --exclude-dir=.expo .)
```

### Version checks

```bash
node -e "
const p = require('./package.json');
const deps = { ...p.dependencies, ...p.devDependencies };
const check = (name, note) => console.log(name + ': ' + (deps[name] || 'not installed') + '  ' + note);
check('@shopify/flash-list', '← MUST be 2.0.2 (v1 = runtime crash)');
check('react-native-mmkv', '← MUST be v3+ (v2 = startup crash)');
check('@react-native-async-storage/async-storage', '← MUST be 2.2.0 (NOT v3)');
check('@gorhom/bottom-sheet', '← 5.1.8+ required');
check('nativewind', '← 4.2.1+ required');
check('react-native-maps', '← 1.27.2; Google Maps iOS config plugin broken');
check('react-native-vision-camera', '← v5 (v4 archived)');
check('react-native-purchases', '← 10.x; iOS 26 startup crash known');
check('react-native-ui-lib', '← known Android Gradle issue');
"
```

### [CRITICAL] @shopify/flash-list v1 still installed — runtime crash

If v1 is still present (wasn't upgraded in the 53→54 hop), it crashes immediately
on launch: `"FlashList v2.x has been designed to be new architecture only"`

```bash
echo "$THIRD_PARTY_FILES" | xargs grep -n "from '@shopify/flash-list'"
node -e "const p=require('./package.json'); console.log(p.dependencies?.['@shopify/flash-list']||'not installed')"
```

Fix: `npx expo install @shopify/flash-list` (installs 2.0.2)  
Then fix all v1 → v2 API changes listed in the SDK 53→54 section.

### [CRITICAL] react-native-mmkv v2 — startup crash on New Arch

`"react-native-mmkv 3.x.x requires TurboModules"` — app crashes before any
JavaScript runs.

```bash
echo "$THIRD_PARTY_FILES" | xargs grep -n \
  "from 'react-native-mmkv'\|new MMKV\(\|MMKV\."
node -e "const p=require('./package.json'); console.log('mmkv:', p.dependencies?.['react-native-mmkv']||'not installed')"
```

Fix: `npm install react-native-mmkv@^3`

If upgrading to v4 (NitroModules): additional API changes apply.
- `new MMKV()` → `createMMKV()`
- `.delete('key')` → `.remove('key')`
- Add `react-native-nitro-modules` dependency

⚠️ Data loss risk on iOS App Groups when migrating v2 → v3. Test thoroughly.

### [CRITICAL] @react-native-async-storage v3 — build failure

v3 is incompatible with SDK 54+. If v3 was installed by mistake:

```bash
node -e "const p=require('./package.json'); console.log(p.dependencies?.['@react-native-async-storage/async-storage']||'not installed')"
```

If v3.x.x: `npx expo install @react-native-async-storage/async-storage` to downgrade to 2.2.0.

### [CRITICAL] react-native-maps — Google Maps iOS EAS build failure

1.27.2 (SDK 55 bundled version) has a broken iOS config plugin for Google Maps:
```
[ios.appDelegate]: withIosAppDelegateBaseMod: Cannot add Google Maps to the project's
AppDelegate because it's malformed.
```

```bash
echo "$THIRD_PARTY_FILES" | xargs grep -n \
  "from 'react-native-maps'\|<MapView\|PROVIDER_GOOGLE"
```

If Google Maps provider is used on iOS: this is a hard build blocker with no
clean fix as of SDK 55 release. Options:
1. Use Apple Maps provider on iOS (`PROVIDER_DEFAULT`)
2. Check the react-native-maps GitHub for the latest patch status
3. Consider `expo-maps` (alpha, iOS 17+ only)

Android Maps and Apple Maps on iOS are unaffected.

### [HIGH] @react-native-firebase — iOS build failure continues

Firebase iOS build failures from SDK 54 persist in SDK 55. If the
`post_install` / modular headers workaround wasn't applied in the previous hop,
apply it now. Also watch for the Expo 55.0.10 specific issue:

```bash
echo "$THIRD_PARTY_FILES" | xargs grep -n "from '@react-native-firebase/"
```

Known issue with `expo` 55.0.10: use `55.0.9` or check for a newer patch.
Workaround: add `CLANG_ALLOW_NON_MODULAR_INCLUDES_IN_FRAMEWORK_MODULES = YES`
via `expo-build-properties` plugin.

### [HIGH] react-native-purchases — iOS 26 + New Arch crash

With iOS 26 + New Architecture, RevenueCat crashes before JavaScript runs:
`SIGABRT/SIGSEGV` in `ObjCTurboModule::performVoidMethodInvocation`.

```bash
echo "$THIRD_PARTY_FILES" | xargs grep -n \
  "from 'react-native-purchases'\|Purchases\.\|PurchasesPackage\|PurchasesOffering"
```

If the project targets iOS: test on iOS 26 beta before releasing. Monitor the
react-native-purchases GitHub for a fix. No confirmed workaround as of May 2026.

### [HIGH] react-native-vision-camera v4 — archived, no New Arch fixes

v4 received no Fabric/TurboModule updates and is archived. On mandatory New Arch
(SDK 55) some v4 frame processor features are broken.

```bash
echo "$THIRD_PARTY_FILES" | xargs grep -n "from 'react-native-vision-camera'"
node -e "const p=require('./package.json'); console.log(p.dependencies?.['react-native-vision-camera']||'not installed')"
```

Fix: migrate to v5. See migration notes in `third-party-packages.md`.

### [MEDIUM] moti — Reanimated v4 + mandatory New Arch

moti has not confirmed Reanimated v4 compatibility. With New Arch now mandatory,
any moti animation that uses Reanimated internals may fail silently or crash.

```bash
echo "$THIRD_PARTY_FILES" | xargs grep -n "from 'moti'\|useAnimationState\|MotiView\|MotiText\|MotiImage"
```

Test every animated screen before shipping. If moti is broken, `@legendapp/motion`
or direct Reanimated v4 APIs are alternatives.

### [MEDIUM] react-native-ui-lib — Android Gradle task failure

```bash
echo "$THIRD_PARTY_FILES" | xargs grep -n "from 'react-native-ui-lib'"
```

Known Android Gradle error:
```
Task ':uilib-native:packageDebugResources' uses this output of task
':react-native-ui-lib:generateDebugResValues' without declaring an explicit dependency.
```

Add explicit task dependency in Android Gradle config or check the latest release
for a fix.

### [LOW] nativewind — verify still on 4.2.1+

Confirm nativewind wasn't accidentally downgraded in this hop:
```bash
node -e "const p=require('./package.json'); console.log('nativewind:', p.dependencies?.['nativewind']||p.devDependencies?.['nativewind']||'not installed')"
```

### 3rd party summary — SDK 55

| Package | Status | Risk |
|---|---|---|
| @shopify/flash-list | MUST be v2 | v1 = runtime crash |
| react-native-mmkv | MUST be v3+ | v2 = startup crash |
| @react-native-async-storage | MUST be 2.2.0 | v3 = build failure |
| react-native-maps (Google/iOS) | BROKEN — config plugin | EAS build failure |
| @react-native-firebase (iOS) | Workaround required | EAS build failure |
| react-native-purchases (iOS 26) | Known crash | Startup SIGABRT |
| react-native-vision-camera | Migrate to v5 | Archived, no fixes |
| moti | Test carefully | Unknown Reanimated v4 issues |
| react-native-ui-lib | Android Gradle fix needed | Build warning/failure |
| nativewind | Confirm 4.2.1+ | Silent unstyled UI if wrong version |
