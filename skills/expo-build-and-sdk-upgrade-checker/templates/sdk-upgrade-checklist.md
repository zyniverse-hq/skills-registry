# Expo SDK Upgrade Checklist

**Project:** `<app name / slug>`  
**Full upgrade path:** SDK `<from>` → SDK `<to>`  
**Hop sequence:** `<e.g. 52→53, 53→54, 54→55>`  
**Date:** `<YYYY-MM-DD>`  **Engineer:** `<name>`

> One major hop at a time. Each hop below is a separate branch and a separate
> EAS preview build. Do not start the next hop until the current one is merged
> and green.

---

## Version snapshot

| Package | Start (SDK `<from>`) | End (SDK `<to>`) |
|---|---|---|
| expo | | |
| react-native | | |
| react / react-dom | | |
| expo-router | | |
| react-native-screens | | |
| react-native-safe-area-context | | |
| react-native-reanimated | | |
| react-native-worklets | | |

---

# HOP 1: SDK `<A>` → SDK `<B>`

**Branch:** `chore/expo-sdk-<B>`

## Pre-flight

- [ ] Clean working tree; hop branch created
- [ ] Baseline `npx expo-doctor` is **clean**
- [ ] Baseline `npx expo install --check` is **clean**
- [ ] Breaking-change file loaded: `checks/breaking-changes-sdk-<B>.md`

## TSX scan results (before touching packages)

Grep commands from `breaking-changes-sdk-<B>.md` run against source tree.

| Pattern grepped | Files/lines found | Action needed |
|---|---|---|
| | | |

> Zero findings = no code changes needed for this hop.  
> List every file:line that needs editing before marking this section complete.

## Package upgrade steps

- [ ] `npx expo install expo@^<B>`
- [ ] `npx expo install --fix`
- [ ] Verified dev tooling stayed in `devDependencies` (nothing leaked)
- [ ] `react-native-worklets` installed (required for SDK 54+): `npx expo install react-native-worklets`
- [ ] Babel plugin verified in `babel.config.js` (reanimated or worklets plugin last, if manually set)
- [ ] `metro.config.js` still extends `expo/metro-config`

## Code changes applied

- [ ] All CRITICAL patterns from TSX scan fixed (removed/replaced)
- [ ] All MEDIUM patterns from TSX scan fixed (deprecated APIs replaced)
- [ ] `app.json` config field changes applied (removed/renamed fields)

Describe changes made:
```
<list each file changed and what was changed>
```

## Validation

- [ ] Clean install: `rm -rf node_modules && rm -f package-lock.json && npm install`
- [ ] Cache cleared: `npx expo start -c`
- [ ] `node scripts/analyze-package-json.js .` — no CRITICAL/HIGH
- [ ] `node scripts/check-sdk-alignment.js .` — RN/React aligned
- [ ] `node scripts/validate-expo-config.js .` — config/EAS clean
- [ ] `node scripts/detect-risky-dependencies.js .` — no CRITICAL/HIGH
- [ ] `npx expo-doctor` — **clean** (`<X>/18 checks passed, 0 failed`)
- [ ] `npx expo install --check` — **no mismatches**
- [ ] Runtime smoke: cold start, Router navigation, permission screens, deep links
- [ ] EAS preview build (iOS) succeeds: `eas build --profile preview --platform ios`
- [ ] Preview build smoke-tested on real device
- [ ] `runtimeVersion` incremented if native-affecting deps changed

## Breaking changes encountered this hop

| Change | Impact | Action taken |
|---|---|---|
| | | |

## Hop 1 sign-off

- [ ] All CRITICAL/HIGH resolved
- [ ] EAS preview build verified on device
- [ ] Branch merged

**Decision:** ☐ GO  ☐ NO-GO — notes: `<...>`

---

# HOP 2: SDK `<B>` → SDK `<C>`

*(Copy the hop template above for each additional hop. Each hop starts from the
merged result of the previous hop.)*

---

## Final sign-off (all hops complete)

- [ ] All hops merged and green
- [ ] Final `npx expo-doctor` clean on `SDK <to>`
- [ ] Final EAS preview build verified on device
- [ ] Production build approved

**Decision:** ☐ GO  ☐ NO-GO — notes: `<...>`
