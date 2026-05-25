# Dependency Mismatch Report

**Project:** `<slug>`  **Expo SDK:** `<major>`  **Generated:** `<YYYY-MM-DD>`
**Trigger:** `<pre-commit | pre-EAS | PR review | upgrade>`

## Verdict

> **`<BLOCK | PROCEED WITH FIXES | CLEAR>`** — `<one-line rationale>`

| Severity | Count |
| --- | --- |
| CRITICAL | `<n>` |
| HIGH | `<n>` |
| MEDIUM | `<n>` |
| LOW | `<n>` |

## expo-doctor live output

```
<paste full npx expo-doctor stdout here>
```

**Summary:** `<X/Y checks passed. Z checks failed.>`

`npx expo install --check` mismatches:

| package | expected | found |
| --- | --- | --- |
| | | |

> If either command could not run, state the reason here.

## CRITICAL — must fix before any build

| Package(s) | Found | Expected | Issue | Fix |
| --- | --- | --- | --- | --- |
| | | | | |

## HIGH — fix before next build

| Package(s) | Found | Expected | Issue | Fix |
| --- | --- | --- | --- | --- |
| | | | | |

## MEDIUM — fix this cycle

| Item | Issue | Fix |
| --- | --- | --- |
| | | |

## LOW — hygiene

| Item | Note |
| --- | --- |
| | |

## Recommended remediation (in order)

```bash
npx expo install --check
npx expo install --fix
npx expo-doctor
# re-run skill scripts to confirm clean
```

## Notes

- Source files inspected: `package.json`, `<app config>`, `eas.json`
- Package manager / lockfile: `<...>`
- Anything that could not be statically resolved: `<...>`
