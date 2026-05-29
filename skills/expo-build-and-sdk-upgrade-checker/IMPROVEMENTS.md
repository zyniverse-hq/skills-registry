# IMPROVEMENTS — expo-build-and-sdk-upgrade-checker

> Improvement plan derived from SKILL.md + ANALYSIS.md audit against the agentskills.openml.io spec.

---

## Quick Summary

| | Before | After |
|---|---|---|
| Spec compliance | Partially compliant | Fully compliant |
| Critical violations | 5 | 0 |
| Agent discoverability | Medium | High |
| Portability | Fails | Pass |

---

## Improvement 1 — Move Non-Standard Frontmatter Fields Under `metadata:`

### What needs to change

Eight non-standard fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`) are declared at the top level of the YAML frontmatter. The spec requires all non-standard fields to be nested under a single `metadata:` key. Top-level placement causes spec-compliant parsers to reject or ignore these fields entirely.

### Before
```yaml
---
name: expo-build-and-sdk-upgrade-checker
description: Analyzes Expo Managed Workflow projects for build failures, dependency mismatches, EAS configuration problems, and SDK upgrade risks — generates a prioritized health report with exact fix commands.
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

### After
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

### Impact if implemented
- **Agent behaviour:** Spec-compliant orchestrators will correctly parse and index all metadata fields; currently they are silently dropped or cause parse errors.
- **Discoverability:** Tag-based search (`eas-build`, `sdk-upgrade`, `dependency-health`) becomes functional in registries that index the `metadata.tags` path.
- **Portability:** Other teams can consume structured metadata programmatically without bespoke parsing workarounds.
- **Risk reduced:** Prevents silent metadata loss in any registry tooling that validates against the spec schema.

### Existing use (before fix)
Today, when an orchestrator or registry tool ingests this skill file, it encounters `version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, and `tested_with` as unexpected top-level YAML keys. Strict parsers reject the frontmatter outright. Lenient parsers silently discard those fields. As a result, the tag-based routing that would match `eas-build` or `sdk-upgrade` queries never fires, and authorship / version metadata is invisible to tooling that relies on `metadata.tags` or `metadata.version`.

### Improved use (after fix)
Once all non-standard fields are nested under `metadata:`, any registry or orchestration layer that follows the spec will correctly read `metadata.tags`, surface the skill in `eas-build` and `sdk-upgrade` filtered searches, and display `metadata.author` and `metadata.version` on the skill detail page. The frontmatter becomes a single source of truth that both human reviewers and automated tools can rely on without custom handling.

---

## Improvement 2 — Add Missing `license` Field

### What needs to change

The `license` field is absent from the frontmatter. The spec requires it as a top-level field. Without it, consumers have no clarity on usage rights, and registry validators will flag the skill as non-compliant.

### Before
```yaml
---
name: expo-build-and-sdk-upgrade-checker
description: Analyzes Expo Managed Workflow projects for build failures, dependency mismatches, EAS configuration problems, and SDK upgrade risks — generates a prioritized health report with exact fix commands.
version: 1.0.0
author: Om Chavan
# No license field present
---
```

### After
```yaml
---
name: expo-build-and-sdk-upgrade-checker
description: Analyzes Expo Managed Workflow projects for build failures, dependency mismatches, EAS configuration problems, and SDK upgrade risks — generates a prioritized health report with exact fix commands.
license: MIT
compatibility: Node.js >= 18, Expo CLI (npx expo), EAS CLI (npx eas) — internet access required for npx expo-doctor and npx expo install --check
metadata:
  version: 1.0.0
  author: Om Chavan
  ...
---
```

### Impact if implemented
- **Agent behaviour:** No direct runtime change, but registry validators stop flagging this skill as incomplete, allowing it to be published and indexed without manual overrides.
- **Discoverability:** Skills with a valid `license` field are listed in open registries; unlicensed skills are often quarantined or require manual approval.
- **Portability:** Other teams and organisations can immediately determine whether they are legally permitted to fork, adapt, or redistribute this skill.
- **Risk reduced:** Eliminates the ambiguity that forces downstream consumers to assume "all rights reserved" and avoid using the skill in production pipelines.

### Existing use (before fix)
Any developer who encounters this skill in a shared registry sees no license declaration. Legal and compliance teams at organisations that enforce open-source due diligence will block adoption until the license is confirmed. Automated registry validators mark the skill as "incomplete" and may exclude it from published listings, reducing the reach of the skill entirely.

### Improved use (after fix)
Adding `license: MIT` (or the appropriate SPDX identifier) immediately unblocks adoption. Registry validators pass the frontmatter check, the skill appears in public listings, and consumers can integrate it into internal tooling without a compliance review cycle. The one-line addition has outsized impact relative to effort.

---

## Improvement 3 — Add Missing `compatibility` Field

### What needs to change

The skill requires Node.js (to run the four analyzer scripts in `scripts/`), Expo CLI (`npx expo-doctor`, `npx expo install --check`), and internet access. These prerequisites are documented in the body under "Prerequisites" but are absent from the frontmatter `compatibility` field. Agent orchestrators read `compatibility` to gate skill activation — without it, the skill may be invoked in environments where it will silently fail at Step 2.

### Before
```yaml
---
name: expo-build-and-sdk-upgrade-checker
description: Analyzes Expo Managed Workflow projects for build failures, dependency mismatches, EAS configuration problems, and SDK upgrade risks — generates a prioritized health report with exact fix commands.
# No compatibility field
---
```

Body section (currently the only place prerequisites are declared):
```markdown
## Prerequisites

- [ ] An Expo Managed Workflow project with a `package.json` and `app.json` / `app.config.js`
- [ ] `eas.json` present (recommended — EAS checks are skipped if absent)
- [ ] Node.js installed so the analyzer scripts in `scripts/` can run
```

### After
```yaml
---
name: expo-build-and-sdk-upgrade-checker
description: Analyzes Expo Managed Workflow projects for build failures, dependency mismatches, EAS configuration problems, and SDK upgrade risks — generates a prioritized health report with exact fix commands.
license: MIT
compatibility: Node.js >= 18, Expo CLI (npx expo), EAS CLI (npx eas) — internet access required for npx expo-doctor and npx expo install --check
metadata:
  ...
---
```

### Impact if implemented
- **Agent behaviour:** Orchestrators can programmatically check whether Node.js >= 18 and the Expo CLI are available before invoking the skill, and surface a meaningful error if prerequisites are unmet rather than failing silently mid-execution.
- **Discoverability:** Skills with a `compatibility` field appear in environment-filtered searches (e.g., "skills that work with Node 20 in a CI container").
- **Portability:** Teams running in restricted environments (no internet, Node 16, no global Expo CLI) know upfront that this skill will not work as-is and can adapt it.
- **Risk reduced:** Prevents silent Step 2 failures where `npx expo-doctor` exits with a non-zero code because the CLI is not installed, producing no output and leaving the health report empty.

### Existing use (before fix)
An agent invoked in a Node 16 CI environment, or in an air-gapped build system, proceeds through Steps 1 and 2 without any upfront warning. When `node scripts/analyze-package-json.js` fails because the `scripts/` directory is missing (see Improvement 4), or when `npx expo-doctor` fails because there is no internet access, the agent has no spec-declared signal to fall back on. It may produce a partial report, silently omit Step 2 findings, or crash. The developer receives an incomplete health report with no explanation.

### Improved use (after fix)
With `compatibility` declared in the frontmatter, an orchestrator can check the environment before the skill runs and either abort with a clear "Node.js >= 18 required" message or downgrade gracefully to static analysis only. The developer gets an actionable error rather than a confusing empty report.

---

## Improvement 4 — Bundle the Four Analyzer Scripts in `scripts/`

### What needs to change

Step 2 instructs the agent to run four Node.js scripts:
- `scripts/analyze-package-json.js`
- `scripts/check-sdk-alignment.js`
- `scripts/validate-expo-config.js`
- `scripts/detect-risky-dependencies.js`

None of these files exist in the skill folder (`skills/expo-build-and-sdk-upgrade-checker/`). The spec requires all referenced scripts to be bundled inside the skill folder. Without them, Step 2 is completely unexecutable as written, and the agent must either invent the analysis logic on the fly (inconsistent results) or skip Step 2 entirely (incomplete report).

### Before
```markdown
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
```
(No `scripts/` directory exists in the skill folder.)

### After

Option A (preferred): Create and bundle the four scripts. Example structure for `scripts/analyze-package-json.js`:

```javascript
#!/usr/bin/env node
// analyze-package-json.js
// Reads <projectRoot>/package.json and reports:
//   - expo SDK version
//   - react-native version
//   - react version
//   - presence of eas.json
//   - multiple lockfiles
const path = require('path');
const fs = require('fs');

const projectRoot = process.argv[2];
if (!projectRoot) { console.error('Usage: node analyze-package-json.js <projectRoot>'); process.exit(1); }

const pkgPath = path.join(projectRoot, 'package.json');
if (!fs.existsSync(pkgPath)) { console.error('ERROR: package.json not found at', pkgPath); process.exit(1); }

const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
const deps = { ...pkg.dependencies, ...pkg.devDependencies };

console.log('=== analyze-package-json ===');
console.log('expo:', deps['expo'] || 'NOT FOUND');
console.log('react-native:', deps['react-native'] || 'NOT FOUND');
console.log('react:', deps['react'] || 'NOT FOUND');
console.log('expo-router:', deps['expo-router'] || 'not present');

const lockfiles = ['package-lock.json','yarn.lock','pnpm-lock.yaml']
  .filter(f => fs.existsSync(path.join(projectRoot, f)));
console.log('lockfiles:', lockfiles.join(', ') || 'none');
if (lockfiles.length > 1) console.log('WARNING: multiple lockfiles detected');
```

Option B (fallback, if bundling scripts is not feasible): Rewrite Step 2 to use `Read`, `Glob`, and `Grep` tools directly instead of delegating to external scripts, and remove all `node <skill>/scripts/*.js` references from the body.

### Impact if implemented
- **Agent behaviour:** Step 2 executes as documented; the agent gets structured, deterministic output from each analyzer before applying the rulebooks in Step 3.
- **Discoverability:** No direct discoverability impact, but a skill that executes correctly gets higher ratings and more reuse.
- **Portability:** Any agent that clones this skill folder gets a fully self-contained, runnable skill with no external dependencies beyond Node.js.
- **Risk reduced:** Eliminates the current silent failure where the agent reaches Step 2, finds no scripts, improvises its own analysis, and produces inconsistent health reports across runs.

### Existing use (before fix)
Today, when an agent follows Step 2 and attempts `node <skill>/scripts/analyze-package-json.js <projectRoot>`, the command fails immediately with `Error: Cannot find module` or a "no such file" error. The agent either reports the failure and aborts Step 2, or silently continues to Step 3 without any analyzer output. In the latter case, Steps 3–5 operate on incomplete data, and the generated health report may miss CRITICAL findings entirely — for example, a React Native version mismatch that would cause an EAS Build failure goes unreported.

### Improved use (after fix)
Once the four scripts are bundled, Step 2 runs deterministically. `analyze-package-json.js` extracts the SDK, React Native, and React versions; `check-sdk-alignment.js` compares them against the known compatibility matrix; `validate-expo-config.js` checks `app.json` / `app.config.js` fields; and `detect-risky-dependencies.js` flags known problematic packages. The agent enters Step 3 with structured, reliable data, and the final health report accurately reflects the project's true state.

---

## Improvement 5 — Bundle `checks/`, `templates/`, and `examples/` Subdirectories

### What needs to change

The skill body references 11 rulebook files in `checks/`, at least 2 template files in `templates/`, and an `examples/` directory. None of these directories exist in the skill folder. The spec requires all referenced files to be bundled within the skill folder. Without them, Steps 3, 5, and 6 cannot be executed as written, and the on-demand loading mechanism described in the Step 3 table is non-functional.

### Before
```markdown
### Step 3: Apply the check rulebooks (load on demand)

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
```
(No `checks/`, `templates/`, or `examples/` directories exist in the skill folder.)

### After

Create the following directory structure inside `skills/expo-build-and-sdk-upgrade-checker/`:

```
skills/expo-build-and-sdk-upgrade-checker/
├── SKILL.md
├── scripts/
│   ├── analyze-package-json.js
│   ├── check-sdk-alignment.js
│   ├── validate-expo-config.js
│   └── detect-risky-dependencies.js
├── checks/
│   ├── sdk-compatibility.md
│   ├── expo-doctor-analysis.md
│   ├── dependency-alignment.md
│   ├── eas-validation.md
│   ├── ios-managed-risks.md
│   ├── upgrade-checklist.md
│   ├── breaking-changes-sdk-52.md
│   ├── breaking-changes-sdk-53.md
│   ├── breaking-changes-sdk-54.md
│   ├── breaking-changes-sdk-55.md
│   └── third-party-packages.md
├── templates/
│   ├── health-report.md
│   └── sdk-upgrade-checklist.md
└── examples/
    └── worked-scenario-sdk-upgrade.md
```

Each `checks/*.md` file should contain the corresponding validation rulebook content (SDK compatibility tables, expo-doctor output patterns, eas.json schema rules, breaking change lists per SDK hop, etc.).

### Impact if implemented
- **Agent behaviour:** Step 3's on-demand loading mechanism becomes functional — the agent can `Read` `checks/sdk-compatibility.md` when a version mismatch is detected, rather than generating rulebook content from training data (which may be outdated for SDK 54 and 55).
- **Discoverability:** A fully self-contained skill with populated subdirectories signals maturity and completeness to registry curators and developers browsing the skill folder.
- **Portability:** Any team can clone the skill folder and have a fully working, self-contained Expo health checker without needing external documentation sources.
- **Risk reduced:** Prevents the agent from hallucinating SDK compatibility tables or breaking-change lists when the `checks/` files are absent, which would produce incorrect fix commands in the health report.

### Existing use (before fix)
When the agent reaches Step 3 and attempts to load `checks/sdk-compatibility.md`, the file does not exist. The agent either reports a file-not-found error and skips the rulebook step, or — more dangerously — generates its own SDK compatibility table from training data. Training data may be outdated for SDK 54 and 55, leading to incorrect version mappings, wrong fix commands, and a health report that confidently gives bad advice. For example, a React Native version listed as compatible in a stale training dataset may have been pinned to a different patch by Expo's actual SDK 54 release.

### Improved use (after fix)
With all 11 rulebook files bundled, the agent reads the authoritative, human-curated compatibility tables and breaking-change lists from disk. SDK version mapping decisions are grounded in the actual content of `checks/sdk-compatibility.md`, not in potentially stale training weights. The upgrade checklist generated in Step 6 references the exact per-hop migration steps in `checks/upgrade-checklist.md`, and the `templates/sdk-upgrade-checklist.md` scaffold ensures consistent output formatting across every run.

---

## Priority Order

| Priority | Improvement | Effort | Impact |
|---|---|---|---|
| 1 | Move non-standard frontmatter fields under `metadata:` + add `license` + add `compatibility` | Low | Critical |
| 2 | Bundle the four analyzer scripts in `scripts/` | Medium | Critical |
| 3 | Bundle `checks/`, `templates/`, and `examples/` subdirectories | High | High |
| 4 | Add `license` field (standalone if not done with Priority 1) | Low | High |
| 5 | Add `compatibility` field (standalone if not done with Priority 1) | Low | Medium |

---

## Before vs After: Full Skill Experience

### Before (current state)

A developer working on an Expo SDK 52 project asks their agent: "Is my Expo project safe to push to EAS Build?" The agent finds the skill, reads `SKILL.md`, and begins executing. Step 1 completes successfully — `package.json`, `app.json`, and `eas.json` are located and read. Step 2 immediately breaks: the agent attempts to run `node <skill>/scripts/analyze-package-json.js` and finds that the `scripts/` directory does not exist. Depending on the agent's error-handling behaviour, it either aborts and reports a confusing "no such file" error, or silently skips the four analyzer scripts and proceeds with no structured data. Step 3 is equally broken: the agent tries to load `checks/sdk-compatibility.md` and finds no `checks/` directory. It falls back to generating compatibility tables from training data — which may be outdated for SDK 54/55 — and produces a health report based on stale, potentially incorrect information.

Meanwhile, the frontmatter issues compound the problem silently. The eight non-standard fields at the top level are rejected or ignored by the registry parser, so the skill never appears in searches for `eas-build` or `sdk-upgrade` tags. The missing `license` field causes compliance teams to block adoption. The missing `compatibility` field means the orchestrator never warns the developer that Node.js >= 18 and internet access are required — so in a CI environment running Node 16 or in an air-gapped build system, the skill invocation fails without a clear explanation. The developer receives either a broken report, a partial report built on stale data, or a confusing error — none of which is the "prioritized health report with exact fix commands" the skill promises.

### After (all improvements applied)

Once all five improvements are applied, the same developer query triggers a reliable, end-to-end execution path. The frontmatter is fully spec-compliant: `license: MIT` is present, `compatibility` declares the Node.js and Expo CLI requirements, and all eight metadata fields are correctly nested under `metadata:`. Registry indexing picks up all tags (`eas-build`, `sdk-upgrade`, `dependency-health`), and orchestrators can gate activation based on environment capabilities before the skill even starts.

At runtime, Step 2 runs all four bundled analyzer scripts from `skills/expo-build-and-sdk-upgrade-checker/scripts/`. Each script reads the project files deterministically and outputs structured findings: the SDK version, React Native version, React version, lockfile count, and any immediate red flags. Step 3 loads only the relevant rulebooks from the bundled `checks/` directory — for a SDK 52 project, that means `checks/sdk-compatibility.md` and `checks/expo-doctor-analysis.md` — grounding every severity judgement in authoritative, curated content rather than training-data approximations. The final health report, scaffolded from `templates/health-report.md`, is correctly ordered CRITICAL → HIGH → MEDIUM → LOW with exact, copy-paste-ready fix commands. If the developer follows up with "give me the upgrade plan to SDK 55," Step 6 loads `checks/upgrade-checklist.md` and the three breaking-change files for the 52→53→54→55 hop sequence, generating a filled `templates/sdk-upgrade-checklist.md` that the developer can save and track. The skill delivers exactly what it promises — every time, in every environment where Node.js >= 18 and the Expo CLI are available.
