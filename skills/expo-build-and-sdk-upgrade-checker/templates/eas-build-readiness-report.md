# EAS Build Readiness Report

**Project:** `<slug>`  **SDK:** `<major>`  **Profile:** `<preview | production>`
**Platform:** iOS (managed)  **Generated:** `<YYYY-MM-DD>`

## Go / No-Go

> **`<GO | NO-GO>`** for `eas build --profile <profile> --platform ios`
> Rationale: `<one line>`

## Readiness matrix

| Area | Status | Detail |
| --- | --- | --- |
| Expo SDK ↔ RN ↔ React aligned | ☐ pass ☐ fail | |
| expo-doctor clean | ☐ pass ☐ fail | |
| Dependency alignment (expo install --check) | ☐ pass ☐ fail | |
| Expo Router triad aligned | ☐ pass ☐ fail | |
| Reanimated Babel plugin last | ☐ pass ☐ fail | |
| app config valid (slug, scheme, bundleId) | ☐ pass ☐ fail | |
| iOS permission strings present | ☐ pass ☐ fail | |
| eas.json profile sane (no dev client / simulator in prod) | ☐ pass ☐ fail | |
| runtimeVersion / channel coherent | ☐ pass ☐ fail | |
| Single lockfile committed | ☐ pass ☐ fail | |

## expo-doctor output

```
<paste full npx expo-doctor stdout here>
```

**Summary:** `<X/Y checks passed. Z checks failed.>`

Package mismatches from `npx expo install --check` (if any):

| package | expected | found |
| --- | --- | --- |
| | | |

> If either command could not run, state the reason here instead of leaving this section blank.

## Blocking issues (CRITICAL/HIGH)

| Severity | Issue | Fix |
| --- | --- | --- |
| | | |

## Non-blocking (MEDIUM/LOW)

| Severity | Issue | Fix |
| --- | --- | --- |
| | | |

## Pre-build commands run

```bash
npx expo install --check
npx expo-doctor
node scripts/analyze-package-json.js .
node scripts/check-sdk-alignment.js .
node scripts/validate-expo-config.js .
node scripts/detect-risky-dependencies.js .
```

## Recommendation

`<Resolve listed CRITICAL/HIGH, re-run checks, then trigger the preview build
before production.>`
