# ANALYSIS — expo-build-and-sdk-upgrade-checker

> Generated against the [agentskills.io](https://agentskills.openml.io) standard.

---

## Overall Verdict

**Partially compliant.** The skill has an excellent, well-structured body with clear step-by-step instructions, strong trigger keywords, and good edge-case coverage. However, it fails on several frontmatter requirements: the `license` field is absent, the `compatibility` field is missing despite having clear environment prerequisites (Node.js, Expo CLI), and several non-standard top-level fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`) are placed directly in the frontmatter instead of being nested under `metadata:` as the spec requires. Additionally, the scripts and reference files cited in the body are not bundled in the skill folder.

---

## Spec Compliance Checklist

| Check | Status | Detail |
|---|---|---|
| `name` field format | ✅ PASS | `expo-build-and-sdk-upgrade-checker` — lowercase, hyphens only, 34 chars, no leading/trailing hyphens, exactly matches folder name |
| `description` present and non-empty | ✅ PASS | 197 chars, well within 1-1024 range |
| `description` describes what it does | ✅ PASS | Clearly states it analyzes Expo Managed Workflow projects and generates a health report |
| `description` describes when to use it | ✅ PASS | Mentions build failures, dependency mismatches, EAS configuration problems, and SDK upgrade risks — strong trigger keywords |
| `license` field | ❌ FAIL | Not present |
| `compatibility` field | ❌ FAIL | Not present — skill explicitly requires Node.js, Expo CLI, and npx; these prerequisites should be declared here |
| `metadata` field structure | ❌ FAIL | `version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with` are non-standard fields placed at the top level of frontmatter; they must be nested under `metadata:` |
| `allowed-tools` field | — | Not present (optional) |
| Token budget (body) | ✅ PASS | ~1950 tokens — well under the 5000-token recommendation |
| Line budget (body) | ✅ PASS | ~175 body lines — well under the 500-line limit |
| `scripts/` directory | ❌ FAIL | Skill body references four scripts in `scripts/`, but the directory does not exist in the skill folder |
| `references/` directory | — | Not referenced; not applicable |
| `assets/` directory | — | Not referenced; not applicable |
| Body — step-by-step instructions | ✅ PASS | Six clearly numbered steps with specific actions and tool calls per step |
| Body — examples | ✅ PASS | Concrete end-to-end example with user trigger, Claude actions, and expected result |
| Body — edge cases | ✅ PASS | Covers bare workflow, missing eas.json, dynamic app.config.ts, monorepo setups, multiple lockfiles, offline CLI, and expo prebuild |

---

## What the Skill Gets Right

- The `name` field is correctly formatted and exactly matches the folder name.
- The `description` is concise, specific, and packed with trigger keywords — both tool-side ("build failures", "dependency mismatches", "EAS configuration") and user-phrase-side ("upgrade Expo SDK", "EAS build failed", "is my Expo project safe to build").
- The body follows a clean six-step progressive flow: discover, analyze, apply rulebooks, check upgrade availability, report, upgrade mode.
- On-demand loading of check rulebooks is explicitly called out (load only what is relevant), which is good for token efficiency.
- The severity table (CRITICAL / HIGH / MEDIUM / LOW) is well-defined with concrete meanings and actions.
- Edge cases are thorough and practically useful (monorepo hoisting, multiple lockfiles, offline CLI, partial parse of dynamic config).
- The "When to use" and "Do NOT activate when" sections provide clear activation boundaries for agent routing.
- Body size is well within both line (~175) and token (~1950) budgets, leaving plenty of room.

---

## Violations (Must Fix)

### 1. Non-standard fields at the top level of frontmatter

The spec states: "Non-standard frontmatter fields MUST be nested under `metadata:`, not at top-level." The following fields are non-standard and appear at the top level: `version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`.

**Current (wrong):**
```yaml
---
name: expo-build-and-sdk-upgrade-checker
description: ...
version: 1.0.0
author: Om Chavan
email: om.chavan@zysk.tech
category: pre-deploy-safety
tags:
  - expo
  - react-native
  - eas-build
  - sdk-upgrade
  - dependency-health
product: zysk
sprint: 1
tested_with: claude-sonnet-4-6
---
```

**Fix:**
```yaml
---
name: expo-build-and-sdk-upgrade-checker
description: Analyzes Expo Managed Workflow projects for build failures, dependency mismatches, EAS configuration problems, and SDK upgrade risks — generates a prioritized health report with exact fix commands.
license: MIT
compatibility: Node.js >= 18, Expo CLI (npx expo), EAS CLI (npx eas) — internet access required for npx expo-doctor and npx expo install --check
metadata:
  version: 1.0.0
  author: Om Chavan
  email: om.chavan@zysk.tech
  category: pre-deploy-safety
  tags:
    - expo
    - react-native
    - eas-build
    - sdk-upgrade
    - dependency-health
  product: zysk
  sprint: 1
  tested_with: claude-sonnet-4-6
---
```

### 2. Missing `license` field

The `license` field is absent. For a skill intended for reuse and sharing, omitting `license` leaves consumers with no clarity on usage rights.

**Fix:** Add `license: MIT` (or the applicable license) to the frontmatter as shown in the fix above.

### 3. Missing `compatibility` field

The skill has clear external environment dependencies: Node.js is required to run the four analyzer scripts, and `npx expo-doctor` / `npx expo install --check` require Expo CLI and internet access. These prerequisites are documented in the body under "Prerequisites" but are not declared in the frontmatter `compatibility` field where agent orchestrators look for environment gating.

**Fix:** Add `compatibility` to the frontmatter (max 500 chars):
```yaml
compatibility: Node.js >= 18, Expo CLI (npx expo), EAS CLI (npx eas) — internet access required for npx expo-doctor and npx expo install --check
```

### 4. Scripts referenced but not bundled in the skill folder

The body instructs the agent to run four Node.js scripts from `scripts/`:
- `scripts/analyze-package-json.js`
- `scripts/check-sdk-alignment.js`
- `scripts/validate-expo-config.js`
- `scripts/detect-risky-dependencies.js`

The spec requires: "Scripts must be bundled in `scripts/` subdirectory inside skill folder, not referenced externally." These scripts do not exist in the skill folder. Without them, Step 2 cannot execute as written.

**Fix:** Either bundle all four scripts in `skills/expo-build-and-sdk-upgrade-checker/scripts/`, or rewrite Step 2 to have the agent perform the analysis directly using `Read`, `Glob`, and `Grep` tools instead of delegating to external scripts.

### 5. Check files and templates referenced but not bundled

The body references multiple files in `checks/` and `templates/` subdirectories (e.g., `checks/sdk-compatibility.md`, `checks/expo-doctor-analysis.md`, `templates/sdk-upgrade-checklist.md`). None of these directories exist in the skill folder. The spec requires all referenced files to be bundled within the skill folder.

**Fix:** Create and populate the `checks/`, `templates/`, and `examples/` subdirectories inside the skill folder with the referenced files, or remove the references if those files are not intended to be bundled.

---

## What's More Than Needed (Consider Restructuring)

The "When to use" section fourth bullet lists 11 specific user phrases inline in a single bullet. This is useful for trigger matching but could be split into individual bullets for readability or condensed into the `description` field as additional keywords. This is a minor style suggestion, not a spec violation.

---

## What's Missing (Must Add)

### 1. `license` field in frontmatter
Add a `license` field at the top level of frontmatter (e.g., `license: MIT`).

### 2. `compatibility` field in frontmatter
Declare the environment prerequisites (Node.js version, Expo CLI, internet access) so orchestrators can gate activation appropriately.

### 3. `scripts/` directory with bundled analyzer scripts
The four `.js` analyzer scripts referenced in Step 2 must exist inside the skill folder at `skills/expo-build-and-sdk-upgrade-checker/scripts/`. Without them, Step 2 is unexecutable as written.

### 4. `checks/` and `templates/` directories with bundled reference files
All 11 rulebook files referenced in Step 3 and the template files referenced in Steps 5-6 must be bundled inside the skill folder. Currently the skill folder contains only `SKILL.md`.

---

## Summary Table

| Area | Status | Detail |
|---|---|---|
| `name` field | ✅ Pass | Correctly formatted, 34 chars, matches folder name exactly |
| `description` field | ✅ Pass | 197 chars, strong trigger keywords, covers what and when |
| `license` field | ❌ Missing | Not present in frontmatter |
| `compatibility` field | ❌ Missing | Not present despite Node.js and Expo CLI being required |
| `metadata` structure | ❌ Wrong | 8 non-standard fields at the top level instead of nested under `metadata:` |
| Token budget | ✅ Pass | ~1950 tokens — well under the 5000-token recommendation |
| Line budget | ✅ Pass | ~175 body lines — well under the 500-line limit |
| Body structure | ✅ Excellent | Six-step progressive flow, severity table, trigger list, edge cases, worked example |
| Self-containment / portability | ❌ Fails | Four analyzer scripts, 11 rulebook files, and templates are referenced but not bundled in the skill folder |
