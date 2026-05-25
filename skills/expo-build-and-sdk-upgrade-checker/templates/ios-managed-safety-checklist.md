# iOS Managed Workflow Safety Checklist

**Project:** `<slug>`  **SDK:** `<major>`  **Generated:** `<YYYY-MM-DD>`

> Managed workflow only. No Xcode / Podfile / native edits — all items below
> are controlled through `app.json` / `app.config.*` and config plugins.

## Identity & versioning

- [ ] `ios.bundleIdentifier` set, reverse-DNS, stable across profiles
- [ ] App `version` valid; `buildNumber` managed via EAS (`appVersionSource` remote + autoIncrement)
- [ ] Bundle id is **not** overridden inconsistently in an EAS profile

## Permissions (declare only what's used)

- [ ] Camera → `NSCameraUsageDescription` (if expo-camera / image-picker)
- [ ] Photo library → `NSPhotoLibraryUsageDescription`
- [ ] Location → `NSLocationWhenInUseUsageDescription`
- [ ] Microphone → `NSMicrophoneUsageDescription`
- [ ] Tracking → `NSUserTrackingUsageDescription` (if expo-tracking-transparency)
- [ ] Each string is meaningful (App Review reads these)

## Capabilities & entitlements

- [ ] Push: `expo-notifications` configured + entitlements if used
- [ ] Universal links: `ios.associatedDomains` set if deep-linking via https
- [ ] Background modes declared via config plugin if a module needs them

## Build configuration (managed-safe)

- [ ] `expo-build-properties` used for `ios.deploymentTarget` (≥ SDK minimum)
- [ ] Hermes left as default (no unintended JSC override)
- [ ] `newArchEnabled` consistent with every native-backed dependency for this SDK
- [ ] No conflicting/duplicate config plugins

## Assets

- [ ] App icon present, square, non-transparent PNG
- [ ] Splash screen via `expo-splash-screen` config (not native edits)

## Workflow integrity

- [ ] No committed `ios/` directory (project remains managed)
- [ ] `expo prebuild` not run unintentionally

## Result

> **`<SAFE | NOT SAFE>`** for iOS EAS build — blockers: `<...>`
