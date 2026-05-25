# Check: expo-doctor Output Analysis

How to interpret `npx expo-doctor` and `npx expo install --check` output and
convert each warning into a severity-tagged, actionable finding.

## How to gather input

```bash
npx expo-doctor            # holistic project diagnostics
npx expo install --check   # dependency version alignment vs the pinned SDK
```

Both are read-only and **must be run as part of every health check**. Capture
their full stdout/stderr and parse it below. If a command cannot run (network
unavailable, npx not found), record that failure explicitly in the report —
never silently skip it. Include the raw `npx expo-doctor` summary line
("X/Y checks passed. Z checks failed.") and every package mismatch table from
`expo install --check` verbatim in the report's expo-doctor section.

## Mapping doctor checks to severity

| expo-doctor finding | Severity | Why |
| --- | --- | --- |
| "Expected package X@A but found B" (core/managed pkg) | CRITICAL | Build/runtime breakage |
| Incompatible dependency version warning | HIGH | Likely crash or build fail |
| "No metro config / invalid config" | HIGH | Bundling fails on EAS |
| Unsupported package on managed workflow | HIGH | Needs prebuild/native (out of managed scope) |
| Project uses deprecated config field | MEDIUM | Works now, breaks next SDK |
| Multiple lockfiles detected | HIGH | Non-deterministic installs |
| "react-native-* should be installed via expo install" | MEDIUM | Version drift risk |
| Optional/peer warnings, advisory only | LOW | Hygiene |

## Common warnings and what they mean

- **"Expected X@~1.2.0 — found 1.5.0"**: a managed package was upgraded
  outside `expo install`. Fix with `npx expo install --fix`.
- **"The following packages should be updated for best compatibility"**:
  classic post-SDK-upgrade drift; run `expo install --fix`.
- **"This package requires native configuration / not supported in Expo Go"**:
  the dependency needs a config plugin or is bare-only. In managed workflow,
  either find an Expo-compatible alternative or add the config plugin (see
  `dependency-alignment.md`). Do **not** recommend native edits.
- **"Multiple package-lock.json / yarn.lock found"**: HIGH — keep one.
- **"Metro config issues"**: ensure `metro.config.js` extends
  `expo/metro-config`; never hand-roll for managed projects.

## Warning patterns to escalate

- Any doctor failure mentioning `expo`, `react`, `react-native`,
  `expo-router`, `react-native-screens`, `react-native-reanimated`,
  `react-native-safe-area-context` → treat as CRITICAL/HIGH; these gate the
  build and navigation.
- "Native module X not found" after `expo install --fix` → likely needs a
  config plugin or is incompatible with managed workflow.

## Recommended fixes

```bash
npx expo install --fix        # resolves the majority of doctor warnings
npx expo-doctor               # re-run to confirm clean
```

If `expo-doctor` still reports failures after `--fix`:

1. Isolate the offending package.
2. Check `dependency-alignment.md` for known-bad combinations.
3. If it requires native code, declare it out of managed scope and present
   the Expo-compatible alternative.

## Example output

```
expo-doctor summary → 2 issues

[CRITICAL] expo-router version mismatch
  expo-doctor: "Expected expo-router@~3.5.x, found 3.4.1"
  Cause: SDK upgraded, router left behind.
  Fix: npx expo install --fix

[MEDIUM] Deprecated config field "expo.ios.config.googleMapsApiKey"
  Replace with the react-native-maps config plugin props.
  Action: update app.json plugins block before SDK 52.

Result: BLOCK build until CRITICAL resolved.
```
