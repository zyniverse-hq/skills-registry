# Example: iOS Managed Workflow Issue (missing permission strings)

## Scenario

App uses `expo-image-picker`. Works in Expo Go, but the production iOS build
crashes the moment the user taps "Choose photo", and App Review rejects the
binary for a missing purpose string.

## Input — package.json + app.json

```json
// package.json
{ "dependencies": { "expo": "~51.0.0", "expo-image-picker": "~15.0.5" } }
```

```json
// app.json
{
  "expo": {
    "slug": "acme",
    "scheme": "acme",
    "ios": { "bundleIdentifier": "com.acme.app" }
  }
}
```

## Analysis (via validate-expo-config.js + ios-managed-risks.md)

```
[HIGH] MISSING_PERMISSION_STRING
  expo-image-picker installed but NSPhotoLibraryUsageDescription /
  NSCameraUsageDescription not declared (no expo-image-picker plugin config).
  iOS crashes on first use; App Store rejects the binary.
```

## Fix — managed-safe (app config only, no Xcode)

Option A — config plugin props (preferred):

```json
{
  "expo": {
    "plugins": [
      ["expo-image-picker", {
        "photosPermission": "Attach photos to your reports.",
        "cameraPermission": "Capture photos for your reports."
      }]
    ]
  }
}
```

Option B — explicit Info.plist strings:

```json
{
  "expo": {
    "ios": {
      "infoPlist": {
        "NSPhotoLibraryUsageDescription": "Attach photos to your reports.",
        "NSCameraUsageDescription": "Capture photos for your reports."
      }
    }
  }
}
```

```bash
node scripts/validate-expo-config.js .   # expect HIGH cleared
eas build --profile preview --platform ios --non-interactive
```

## Lesson

Every iOS capability a module touches needs a purpose string declared in app
config or the module's config plugin — never via native Xcode edits in managed
workflow. Missing strings = runtime crash **and** App Review rejection.
