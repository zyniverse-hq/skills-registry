---
name: expo-build-and-sdk-upgrade-checker
description: Analyzes Expo Managed Workflow projects for build failures, dependency mismatches, EAS configuration problems, and SDK upgrade risks — generates a prioritized health report with exact fix commands.
license: MIT
compatibility: >
  Requires Node.js and Expo CLI (npx expo) available in PATH. EAS CLI (eas) required
  for EAS build configuration checks. Designed for Claude Code. Uses scripts/ bundled
  in the skill folder for check rulebooks. Tested with Expo SDK 49-52.
metadata:
  version: "1.0.0"
  author: Om Chavan
  email: om.chavan@zysk.tech
  category: pre-deploy-safety
  tags: "expo, react-native, eas-build, sdk-upgrade, dependency-health"
  product: zysk
  sprint: "1"
  tested_with: claude-sonnet-4-6
---

# Expo Build & SDK Upgrade Checker

> Analyzes Expo Managed Workflow projects for build failures, dependency mismatches, EAS configuration problems, and SDK upgrade risks — generates a prioritized health report with exact fix commands.

## When to use

- Activate when: the user wants to check if their Expo project is safe to build or release
- Activate when: the user is upgrading or planning to upgrade the Expo SDK
- Activate when: the user reports EAS Build failures, dependency mismatches, or expo-doctor warnings
- Activate when: the user says "upgrade Expo SDK", "check Expo compatibility", "analyze expo-doctor", "fix EAS build issue", "validate Expo dependencies", "check iOS build readiness", "review package.json for Expo issues", "Expo Router compatibility", "dependency mismatch", "EAS build failed", or "is my Expo project safe to build"
- Do NOT activate when: the project uses Expo Bare Workflow requiring edits to committed `ios/` or `android/` native directories (Xcode, Gradle, Swift, Kotlin — those are out of scope)

## Prerequisites

- [ ] An Expo Managed Workflow project with a `package.json` and `app.json` / `app.config.js`
- [ ] `eas.json` present (recommended — EAS checks are skipped if absent)
- [ ] Node.js installed so the analyzer scripts in `scripts/` can run

## Steps

### Step 1: Discover the project

1. Locate and read `package.json` (prefer repo root).
2. Locate and read `app.json` **or** `app.config.js` / `app.config.ts`.
3. Locate and read `eas.json` if present.
4. Confirm this is a **managed** project — no tracked `ios/` or `android/` directories with native source. If native dirs exist and are committed, flag using `checks/ios-managed-risks.md` and continue in managed-analysis mode only.

Use `Glob` for discovery (`**/package.json`, `**/app.{json,config.*}`, `**/eas.json`) and `Read` for file contents.

### Step 2: Run the analyzers

Run the four read-only helper scripts from the `scripts/` folder, then run the two live Expo CLI checks:

```bash
node <skill>/scripts/analyze-package-json.js <projectRoot>
node <skill>/scripts/check-sdk-alignment.js <projectRoot>
node <skill>/scripts/validate-expo-config.js <projectRoot>
node <skill>/scripts/detect-risky-dependencies.js <projectRoot>

npx expo-doctor
npx expo install --check
```

Capture the full output of all six commands. If either CLI command fails (offline, not installed), note it explicitly in the report — do not silently omit it.

### Step 3: Apply the check rulebooks (load on demand)

Load only the file relevant to what the analyzers found — do not load all of them upfront:

| Concern | File |
|---|---|
| SDK ↔ React Native ↔ React version mapping | `checks/sdk-compatibility.md` |
| Interpreting expo-doctor / expo install --check | `checks/expo-doctor-analysis.md` |
| Expo-managed package version drift, Expo Router | `checks/dependency-alignment.md` |
| eas.json profiles, channels, runtime version | `checks/eas-validation.md` |
| iOS-specific managed risks | `checks/ios-managed-risks.md` |
| SDK upgrade procedure and multi-hop sequence | `checks/upgrade-checklist.md` |
| SDK 51→52 breaking changes + TSX + 3rd-party | `checks/breaking-changes-sdk-52.md` |
| SDK 52→53 breaking changes + TSX + 3rd-party | `checks/breaking-changes-sdk-53.md` |
| SDK 53→54 breaking changes + TSX + 3rd-party | `checks/breaking-changes-sdk-54.md` |
| SDK 54→55 breaking changes + TSX + 3rd-party | `checks/breaking-changes-sdk-55.md` |
| 3rd-party version matrix + New Architecture blockers | `checks/third-party-packages.md` |

For any SDK upgrade request: load `checks/upgrade-checklist.md` first to determine the hop sequence, then load only the breaking-change files for those hops. Never load all breaking-change files at once.

### Step 4: SDK upgrade availability check (health-check mode)

After the analyzers and rulebooks have run (Steps 2–3), compare the detected SDK major against the latest known SDK (currently **55**). If the project is behind, add this finding at LOW severity:

```
[LOW] SDK UPGRADE AVAILABLE
Current: SDK <X> | Latest: SDK 55 | Hops required: <n>
Hop sequence: <X>→<X+1>→...→55
Ask for an "upgrade plan" to get the full per-hop checklist, code-change
scope, and TSX migration commands for each hop.
```

Do **not** run TSX scans, load breaking-change files, or produce the upgrade checklist during a health check — that belongs in Step 6 (upgrade mode only).

### Step 5: Generate the health report

Produce a findings report using the relevant template from `templates/`. Every finding must carry a severity level, a one-line explanation, and an exact recommended command or config change. Order findings CRITICAL → HIGH → MEDIUM → LOW.

**Severity levels:**

| Level | Meaning | Action |
|---|---|---|
| CRITICAL | Build will fail or release is unsafe | Block — fix before any EAS build |
| HIGH | Likely failure or runtime crash on device | Fix before next build |
| MEDIUM | Works now but fragile or deprecated | Fix this cycle |
| LOW | Hygiene / future-proofing | Track, fix opportunistically |

**Managed-safe recovery commands (never recommend native edits):**

```bash
npx expo install --check               # report misaligned packages
npx expo install --fix                 # realign — preserves devDependencies placement
npx expo install -- --save-dev <pkg>   # add new dev dependency (npm/pnpm)
npx expo install -- --dev <pkg>        # add new dev dependency (yarn)
npx expo-doctor                        # full project health validation
rm -rf node_modules && npm install     # clean dependency state
npx expo start -c                      # clear Metro / Expo caches
```

### Step 6: Upgrade mode (when explicitly requested)

If the user asks for an upgrade plan, load `checks/upgrade-checklist.md` and the breaking-change files for each hop in the sequence. Run the two-phase TSX scan described in the checklist. Generate the filled `templates/sdk-upgrade-checklist.md`.

## Output

- **Format:** Markdown health report delivered inline in the conversation
- **Location:** Inline response; upgrade checklists may also be saved as a file if the user requests
- **Example:** A prioritized findings list — one CRITICAL (React Native version mismatch with exact fix command), two MEDIUM (deprecated packages), one LOW (SDK 52 available, 3 hops to SDK 55)

## Example

**User says:** "Is my Expo project safe to push to EAS Build?"

**Claude does:** Reads `package.json`, `app.json`, and `eas.json`; runs the four analyzer scripts plus `npx expo-doctor` and `npx expo install --check`; loads only the relevant check rulebooks; produces a health report ordered by severity with exact fix commands for each finding.

**Result:** A prioritized report — e.g., one CRITICAL finding (React Native version mismatch), two MEDIUM findings (deprecated packages), and one LOW finding (SDK 52 available, 3 hops to SDK 55 with upgrade plan offer).

## Notes

- Managed Workflow only — bare workflow native edits (`ios/`, `android/`, Xcode, Gradle) are explicitly out of scope; state this and stop if the user needs native changes
- No `eas.json` → EAS checks are skipped; report notes it and recommends `eas build:configure`
- Dynamic `app.config.ts` files may be only partially parsed statically; report flags unresolved fields
- Monorepo: analyze the app package root, not the workspace root; watch for hoisted/duplicate React or React Native versions (duplicate = CRITICAL)
- Multiple lockfiles in the same project is itself a HIGH finding
- Scripts erroring "cannot find package.json" → confirm `<projectRoot>` argument points to the directory containing `package.json`
- `expo prebuild` regenerates native folders — only mention it if the user explicitly opted into prebuild, and warn it converts the project toward bare workflow
- Reference files: `checks/` — validation rulebooks | `scripts/` — read-only Node analyzers | `templates/` — report scaffolds | `examples/` — worked scenarios
