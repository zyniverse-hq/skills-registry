# Check: iOS-Specific Managed Workflow Risks

iOS build reliability concerns that are controllable **without leaving the
managed workflow** (no Xcode/Podfile edits).

## Validation rules

1. **Bundle identifier** (`ios.bundleIdentifier`) must be present, reverse-DNS,
   and stable. Missing on a build profile = CRITICAL (EAS iOS build fails).
2. **Build number / version** (`ios.buildNumber`, `version`) must be a valid
   format; rely on `cli.appVersionSource` + EAS auto-increment rather than
   manual drift (MEDIUM if hand-managed inconsistently).
3. **Required permission usage strings**: any module needing iOS privacy
   permissions (camera, location, photos, microphone, tracking) must declare
   `NSxxxUsageDescription` via `ios.infoPlist` or the module's config plugin.
   Missing string for a used capability = HIGH (App Store rejection / crash).
4. **`expo-build-properties`** is the managed-safe way to set iOS deployment
   target / static frameworks / use-frameworks. Pinning an unsupported
   `ios.deploymentTarget` (below SDK minimum) = HIGH.
5. **New Architecture / Fabric** (`newArchEnabled`) must be consistent with
   what every native-backed dependency supports for the SDK. Enabling it with
   an incompatible library = HIGH (build or runtime failure).
6. **Hermes** is the managed default; explicitly switching iOS to JSC via
   build properties without reason = MEDIUM (loses Expo support path).
7. **Push entitlements / associated domains**: if using `expo-notifications`
   or universal links, the entitlements must be declared in app config
   (`ios.entitlements`, `ios.associatedDomains`). Missing = HIGH for the
   relevant feature.
8. **Asset/icon requirements**: `ios.icon` (or shared `icon`) must exist and
   be a square non-transparent PNG; bad icon = HIGH (submission rejection).
9. **Config plugins order**: plugins that modify Info.plist/entitlements
   should be deterministic; duplicate/conflicting plugins = MEDIUM.
10. **No committed `ios/` directory** in a managed project. If present and
    tracked, the project is drifting toward bare workflow → HIGH; recommend
    removing it or explicitly adopting prebuild knowingly.

## Common problems

- Camera/photo library used (e.g. `expo-image-picker`) but no
  `NSCameraUsageDescription` / `NSPhotoLibraryUsageDescription` → runtime
  crash on first use and review rejection.
- `newArchEnabled: true` with a library lacking Fabric support for that SDK.
- Deployment target set below the SDK's iOS minimum via build properties.
- `bundleIdentifier` differs between `app.json` and an EAS profile override.
- Transparent or non-square app icon → "Invalid binary" from App Store.
- `expo-tracking-transparency` used without `NSUserTrackingUsageDescription`.

## Warning patterns

- EAS iOS log: "No bundle identifier" / provisioning profile mismatch.
- App Store Connect: "Missing purpose string in Info.plist".
- Runtime: app crashes immediately after tapping a permission-gated feature.
- Build fails resolving a pod that requires New Architecture toggle.

## Recommended fixes (managed-safe)

Add purpose strings via app config (no native edits):

```jsonc
// app.json
{
  "expo": {
    "ios": {
      "bundleIdentifier": "com.acme.app",
      "infoPlist": {
        "NSCameraUsageDescription": "Used to scan documents.",
        "NSPhotoLibraryUsageDescription": "Used to attach photos."
      }
    },
    "plugins": [
      ["expo-build-properties", { "ios": { "deploymentTarget": "15.1" } }]
    ]
  }
}
```

- Prefer each module's **config plugin** props for permission strings when
  the module provides them (e.g. `expo-image-picker` plugin options).
- Manage `buildNumber` via EAS (`cli.appVersionSource: "remote"` +
  `autoIncrement`) instead of hand-editing.
- Keep `newArchEnabled` aligned with dependency support for the pinned SDK.

## Example output

```
[HIGH] expo-image-picker used but NSPhotoLibraryUsageDescription missing
  iOS will crash on first picker open and App Store will reject.
  Fix: add ios.infoPlist.NSPhotoLibraryUsageDescription in app.json.

[HIGH] newArchEnabled:true but react-native-maps@<x> lacks Fabric on SDK 51
  iOS build/runtime risk.
  Fix: disable newArchEnabled or upgrade the dependency to a Fabric build.

[CRITICAL] ios.bundleIdentifier missing
  EAS iOS build cannot create a provisioning profile.
  Fix: set expo.ios.bundleIdentifier.
```
