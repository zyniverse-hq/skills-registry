# Third-Party Package Compatibility Report

**Project:** `<slug>`  **Expo SDK:** `<from>` → `<to>`  **Generated:** `<YYYY-MM-DD>`
**Trigger:** `<pre-upgrade | pre-EAS | PR review>`

> Covers packages NOT managed by `npx expo install` (not in Expo's bundledNativeModules).
> Expo-managed packages are reported in the Dependency Mismatch Report.

## Verdict

> **`<BLOCK | PROCEED WITH FIXES | CLEAR>`** — `<one-line rationale>`

| Severity | Count |
|---|---|
| CRITICAL | `<n>` |
| HIGH | `<n>` |
| MEDIUM | `<n>` |
| LOW | `<n>` |

## Installed versions vs SDK `<to>` requirements

| Package | Installed | Required for SDK `<to>` | Status |
|---|---|---|---|
| @gorhom/bottom-sheet | `<version>` | `<required>` | ☐ OK ☐ UPDATE |
| @shopify/flash-list | `<version>` | `<required>` | ☐ OK ☐ UPDATE |
| nativewind | `<version>` | `<required>` | ☐ OK ☐ UPDATE |
| react-native-mmkv | `<version>` | `<required>` | ☐ OK ☐ UPDATE |
| @react-native-async-storage | `<version>` | `<required>` | ☐ OK ☐ UPDATE |
| @react-native-firebase | `<version>` | `<required>` | ☐ OK ☐ UPDATE |
| react-native-vision-camera | `<version>` | `<required>` | ☐ OK ☐ UPDATE |
| react-native-maps | `<version>` | `<required>` | ☐ OK ☐ UPDATE |
| @shopify/react-native-skia | `<version>` | `<required>` | ☐ OK ☐ UPDATE |
| @tanstack/react-query | `<version>` | `<required>` | ☐ OK ☐ UPDATE |
| zustand | `<version>` | `<required>` | ☐ OK ☐ UPDATE |
| moti | `<version>` | `<required>` | ☐ OK ☐ UPDATE |

> Add or remove rows for packages actually present in this project.

## CRITICAL — build or launch blockers

| Package | Installed | Issue | Fix |
|---|---|---|---|
| | | | |

## HIGH — crash or build failure risk

| Package | Installed | Issue | Fix |
|---|---|---|---|
| | | | |

## MEDIUM — silent regression or known bug

| Package | Issue | Workaround / Fix |
|---|---|---|
| | | |

## LOW — deprecation / future risk

| Package | Note |
|---|---|
| | |

## New Architecture compatibility check

> SDK `<to>` requires New Architecture: **`<YES — mandatory | YES — default | NO — opt-in>`**

| Package | Fabric/TurboModule support | Action needed |
|---|---|---|
| | | |

## detect-risky-dependencies.js output

```
<paste full script output here>
```

## API migration scope (Phase A scan results)

> Files that import affected packages, found via Phase A fast import audit.

| Package | Files found | Breaking patterns in Phase B |
|---|---|---|
| | | |

## Remediation commands (in order)

```bash
# Expo-pinned packages — always use expo install
npx expo install <package-list>

# Non-SDK-pinned packages — use npm/yarn with explicit versions
npm install <package>@<version>

# Metro config workarounds (e.g. Firebase)
# metro.config.js: config.resolver.unstable_enablePackageExports = false

# Clean install
rm -rf node_modules && rm -f package-lock.json && npm install
npx expo start -c
```

## Post-remediation validation

- [ ] `node scripts/detect-risky-dependencies.js .` — no CRITICAL/HIGH
- [ ] `npx expo-doctor` — clean
- [ ] `npx expo install --check` — no mismatches
- [ ] Runtime smoke: all screens using affected packages tested
- [ ] EAS preview build succeeds: `eas build --profile preview --platform ios`

## Notes

- Reference file: `checks/third-party-packages.md` for the full SDK 52–55 matrix
- Packages not listed above: `<any other packages inspected>`
- Anything that could not be resolved statically: `<...>`
