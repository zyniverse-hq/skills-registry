# Check: EAS Build Configuration Validation

Validates `eas.json` build profiles and their interaction with the managed
app config so EAS Build runs predictably.

## Validation rules

1. **`eas.json` exists** for projects that build on EAS. Missing = MEDIUM
   (EAS uses defaults; recommend `eas build:configure`).
2. **CLI version constraint** (`cli.version`) should be present and satisfiable
   (LOW/MEDIUM).
3. **Build profiles** (`development`, `preview`, `production`) should exist
   and be internally consistent.
4. **`developmentClient: true`** profiles must have `expo-dev-client`
   installed (HIGH if missing — the build is unusable).
5. **`distribution`** must be valid: `internal` (ad-hoc/simulator) or
   `store`. Production should be `store` (MEDIUM if `internal`).
6. **iOS `simulator: true`** produces a simulator-only build — never for
   production/store (HIGH if on the production profile).
7. **Runtime version policy** must be coherent with `expo-updates`:
   `runtimeVersion` (or `runtimeVersion.policy`) in app config should align
   with the channel used by the EAS profile. Mismatch → OTA updates won't
   reach the build (HIGH).
8. **`channel`** in each profile should map to an EAS Update channel if
   `expo-updates` is configured (MEDIUM if absent while updates enabled).
9. **`node` / `image`** pins should be supported EAS images; very old image
   pins are MEDIUM (deprecation) and HIGH if past EOL.
10. **Env / secrets**: referenced `env` vars and `EXPO_PUBLIC_*` usage should
    be defined for the profile; secrets must not be committed in `eas.json`
    (HIGH if a secret value is inline).

## Common problems

- `production` profile inherits `developmentClient: true` via `extends` →
  ships a dev client to the store. CRITICAL.
- `ios.simulator: true` on `preview`/`production` → `.app` that cannot be
  submitted. HIGH.
- `runtimeVersion` set to a fixed string but app code changed native-affecting
  deps → OTA payload incompatible. HIGH.
- No `channel` but `expo-updates` configured → updates published to a channel
  nothing subscribes to. MEDIUM/HIGH.
- Secret API keys hard-coded in `eas.json` env block → leak. HIGH.
- `cli.appVersionSource` unset while using `autoIncrement` expectations →
  inconsistent build numbers. MEDIUM.

## Warning patterns

- EAS log: "No development build available" → dev profile without
  `expo-dev-client`.
- EAS log: "Invalid eas.json" / schema error → malformed profile.
- Store rejection: "simulator binary" → `simulator: true` leaked to release.
- Update never applies on device → runtimeVersion/channel mismatch.

## Recommended fixes

```bash
eas build:configure                  # scaffold/repair eas.json
npx expo install expo-dev-client     # if any profile uses developmentClient
eas build --profile preview --platform ios --non-interactive   # smoke test
```

Profile hygiene:

- Keep `production` minimal; do not `extends` a development profile.
- `production.ios` must NOT set `simulator: true`.
- Pair `channel` with `runtimeVersion` policy (`appVersion` or `sdkVersion`)
  consistently across profiles.

## Example output

```
[CRITICAL] production profile extends "development" (developmentClient:true)
  Store build would embed the dev client.
  Fix: give production its own profile without developmentClient.

[HIGH] ios.simulator:true on "preview" profile
  Produces a non-submittable simulator build.
  Fix: remove simulator:true (or move to a dedicated simulator profile).

[HIGH] runtimeVersion "1.0.0" fixed, but expo-updates channel "production"
  OTA updates will not match this build's runtime.
  Fix: use runtimeVersion.policy "appVersion" and align channel.

[MEDIUM] eas.json missing cli.version pin
  Fix: add "cli": { "version": ">= 13.0.0" }
```
