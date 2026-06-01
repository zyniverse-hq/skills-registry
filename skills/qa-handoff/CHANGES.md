# QA Handoff Skill — Change Report

**Skill:** `qa-handoff`
**Version before:** 1.0.0
**Version after:** 1.1.0
**Date:** 28 May 2026
**Branch:** `improved-skills`

---

## Overview

A full production-readiness review was conducted on the `qa-handoff` skill. The review identified **17 issues** across four severity levels — Critical, High, Medium, and Minor. All 17 were fixed in this update.

**Files changed:**
- `skills/qa-handoff/SKILL.md` — updated (60 lines added)
- `skills/qa-handoff/references/smoke-test.md` — updated (name replaced)
- `skills/qa-handoff/references/setup.md` — **new file created**

---

## What Was Broken (Before This Update)

| Severity | Count | What it meant in practice |
|---|---|---|
| 🔴 Critical | 3 | Skill would fail on first use — non-functional out of the box |
| 🟠 High | 5 | Skill would produce wrong results or fail unpredictably |
| 🟡 Medium | 5 | Skill worked but with friction, inconsistency, or data quality issues |
| 🔵 Minor | 4 | Polish gaps — unprofessional or hard to maintain |
| **Total** | **17** | |

---

## Critical Fixes

### C1 — Configuration placeholders were never documented

**Problem:** The skill contained `<your-org>`, `<your-repo>`, `<dev-url>`, `<prod-url>`, `<your-project-id>`, `<secondary-project-id>`, `<your-status-field-id>`, and `<ready-for-qa-option-id>` scattered across five files with no instructions on how or where to fill them in.

**Impact before fix:** Every GitHub command would fail. No QA issues could be created. Project boards could not be updated. The skill was completely non-functional for any new user.

**What was fixed:**
- Created `references/setup.md` with a table listing every placeholder, what it means, and how to find its real value
- Added GraphQL queries to help users look up their project board IDs
- Added a global find-replace instruction so users can fill all placeholders at once

---

### C2 — No first-time setup guide existed

**Problem:** The skill assumed `gh` CLI was installed, authenticated, and the repo configured. There was no onboarding document, no checklist, and no verification step.

**Impact before fix:** New users would hit cryptic errors with no guidance. Setup was entirely undocumented — users had to reverse-engineer what was needed by reading error messages.

**What was fixed:**
- Created `references/setup.md` with a 6-step setup checklist:
  1. Install and authenticate the GitHub CLI
  2. Fill in all configuration placeholders
  3. Update the URL mapping table for the project
  4. Add a link to dev test accounts
  5. Add `.gitignore` entry
  6. Run a dry-run verification to confirm everything works
- Added a "First-time setup" section to `SKILL.md` pointing to this guide
- Noted clearly: **one-time step — after setup, no further configuration needed**

---

### C3 — QA assignee username could leak into Git history

**Problem:** The skill saves the QA tester's GitHub username to `.qa-assignee.local` and says it is "gitignored" — but never instructs the user to actually add the entry to `.gitignore`. If skipped, the file gets committed and the username is in the repo's permanent history.

**Impact before fix:** Team member PII (GitHub username) could end up committed to the repository, violating data hygiene and potentially compliance requirements.

**What was fixed:**
- `references/setup.md` Step 5 includes the exact `.gitignore` entry (`**/.qa-assignee.local`) and the git commands to add and commit it
- Added a guardrail to `SKILL.md`: *"On first use, verify `**/.qa-assignee.local` is in `.gitignore` before saving the assignee"*

---

## High Fixes

### H1 — No check that `gh` CLI is installed and authenticated

**Problem:** The skill called `gh` commands immediately with no pre-flight check.

**Impact before fix:** If `gh` was not installed or not logged in, every command would fail with a confusing error. Users had no clear next step.

**What was fixed:**
- `references/setup.md` Step 1 includes `gh --version`, `gh auth login`, and a verification command (`gh api user --jq '.login'`) with an explicit note: *"If this fails, the skill cannot create issues. Fix authentication before proceeding."*

---

### H2 — `report-templates.md` was missing from the supporting files index

**Problem:** `SKILL.md` listed four supporting reference files at the top but omitted `references/report-templates.md`, which is loaded in Step 8 to format the final batch report.

**Impact before fix:** Anyone reading or maintaining the skill would miss this file entirely. Future edits could accidentally break the report format without realising the file existed.

**What was fixed:**
- Added `references/report-templates.md` to the supporting files index in `SKILL.md` with a description: *"Step 8 batch report templates (Mode A/B/C + dry-run)"*

---

### H3 — URL mapping table was hardcoded for one project with no customisation guide

**Problem:** The file-path-to-URL mapping table in Step 5 used TMS-specific folder paths (`src/app/(authenticated)/(app)/exams/`) with no label indicating it was project-specific and no instructions for adapting it.

**Impact before fix:** If the skill was reused on a different project, QA testers would be sent to wrong URLs. The test plans would be misleading.

**What was fixed:**
- Added a callout above the URL mapping table: *"Project-specific: this table reflects the TMS folder structure. Update it for your project — see references/setup.md Step 3"*
- `references/setup.md` Step 3 explains how to update the table

---

### H4 — Draft pull requests were not explicitly excluded from sweeps

**Problem:** The skill did not document whether draft PRs could appear in sweep results.

**Impact before fix:** Teams unfamiliar with GitHub's behaviour might worry that draft PRs could get QA issues filed against them, or be confused when they don't appear.

**What was fixed:**
- Added an explicit note in Step 0.5a: *"Draft PRs: automatically excluded — `--state merged` only returns fully merged PRs. A PR in draft state cannot be merged."*
- Added a guardrail entry confirming the same for Mode B (Step 1's `state != "MERGED"` check catches any draft passed by number)

---

### H5 — Labels reference file was not bundled with the skill

**Problem:** The guardrails said *"pick labels from the existing 25-label set in `docs/LABELS.md`"* — but this file lives in the target project, not in the skill itself. If the file didn't exist, the skill had no fallback.

**Impact before fix:** On repos without `docs/LABELS.md`, the skill might try to use labels that don't exist, causing `gh issue create` to fail or create unexpected new labels.

**What was fixed:**
- Updated the guardrail: *"If `docs/LABELS.md` does not exist in the target repo, fall back to `type: test` only. Do NOT attempt to create new labels."*
- `type: test` is already in the Step 7c command, so this fallback requires no extra action

---

## Medium Fixes

### M1 — Dates displayed in machine format, not human-readable

**Problem:** GitHub returns `mergedAt` as an ISO timestamp (`2026-05-16T14:23:11Z`). The skill inserted this directly into issue bodies and test plans without formatting it.

**Impact before fix:** QA issues would show dates like `2026-05-16T14:23:11Z` — confusing and unprofessional.

**What was fixed:**
- Added a format instruction to both the Step 5 template and the Step 7a body template: `<mergedAt — format as "16 May 2026", not ISO timestamp>`

---

### M2 — No warning when the backlog exceeded 30 pull requests

**Problem:** Sweep mode fetches the last 30 merged PRs. If more than 30 PRs needed handoffs, the oldest were silently skipped with no warning.

**Impact before fix:** PRs could be missed entirely without anyone knowing.

**What was fixed:**
- Step 0.5a now instructs: *"If the result set is exactly 30, warn the user that older unhandled PRs may exist and suggest re-running with `--limit 50`"*
- Step 0.5d reinforces this: if the filtered result was empty but the raw fetch hit exactly 30, append the limit warning

---

### M3 — QA test accounts and credentials were not referenced anywhere

**Problem:** Test plans told QA to "sign in as a premium user" or "sign in as an admin" but gave no indication of where to find those accounts.

**Impact before fix:** New QA team members (or those returning after a break) would have to ask a developer for credentials, defeating the purpose of a self-contained handoff.

**What was fixed:**
- Added a `**Test accounts:**` line to the Pre-conditions section of the Step 5 template, with a placeholder pointing to `references/setup.md` Step 4
- `setup.md` Step 4 prompts the team to add a link to their password manager or wiki once — it propagates to every future handoff

---

### M4 — Variant selection was ambiguous for multi-category pull requests

**Problem:** The variant selection rules were clear for simple PRs but vague for PRs that hit multiple categories. The guidance ("use the more user-visible variant and borrow sub-sections from others") was a principle, not an example.

**Impact before fix:** Two runs on the same PR might pick different variants, producing inconsistently structured test plans.

**What was fixed:**
- Added a multi-category combination table to Step 4.5 with five concrete scenarios:
  - New feature + auth changes → Variant 2 + Permission checks from Variant 6
  - Bug fix + UI change → Variant 3 + Visual check from Variant 4
  - Refactor + server action → Variant 1 + Correctness check from Variant 5
  - New feature + external integration → Variant 2 + failure handling from Variant 8
  - B2B feature + permission gate → Variant 7 + free-user check from Variant 6

---

### M5 — No guidance for GitHub API slowness or rate limits

**Problem:** The skill made multiple `gh api` calls per PR with no mention of what to do if GitHub was slow, under maintenance, or rate-limited.

**Impact before fix:** A rate-limited or hanging run would leave the user with no recovery path, potentially with some issues filed and others not.

**What was fixed:**
- Added rate-limit recovery steps to `references/setup.md` (check limit, wait for reset, re-run targeting only failed PRs)
- Added a guardrail entry in `SKILL.md`: *"If commands hang or fail with HTTP 403, check `gh api rate_limit --jq '.rate'` and wait for reset. Batch failures are partial — Step 8 lists which PRs failed."*

---

## Minor Fixes

### N1 — Real team member's name in smoke test example

**Problem:** The smoke test procedure used `Rochanay` as the example GitHub username — an apparent real person's name.

**What was fixed:**
- Replaced all three occurrences of `Rochanay` in `references/smoke-test.md` with the neutral placeholder `qa-tester`

---

### N2 — No version changelog

**Problem:** The skill was at v1.0.0 with no history of what that version contained.

**What was fixed:**
- Added a `## Changelog` table at the end of `SKILL.md` with entries for v1.0.0 (initial release) and v1.1.0 (this update, with a summary of all changes)

---

### N3 — Dry-run leftover files were not explained

**Problem:** Running with `--dry-run` intentionally leaves markdown files in `docs/qa-handoffs/`. There was no instruction for cleaning them up.

**What was fixed:**
- Added cleanup commands to Step 7b:
  ```bash
  rm docs/qa-handoffs/PR-<N>.md       # single PR
  rm docs/qa-handoffs/*.md            # full batch
  ```
- Added a note that Step 8a runs this automatically when `--dry-run` is dropped

---

### N4 — Skill trigger phrases were too limited

**Problem:** The description only listed 4 trigger phrases. Users who phrased their request differently might not activate the skill.

**What was fixed:**
- Added 7 new trigger phrases to the `description` frontmatter field:
  - `"create a test plan for this PR"`
  - `"prepare testing instructions"`
  - `"hand off to QA"`
  - `"write QA checklist"`
  - `"QA this PR"`
  - `"file a QA issue"`
  - `"PR is ready for testing"`

---

## Summary of All Changes by File

### `SKILL.md` (modified)

| Change | Fixes |
|---|---|
| Version bumped to 1.1.0 | — |
| 7 new trigger phrases added to `description` | N4 |
| `references/setup.md` added to supporting files index | C2 |
| `references/report-templates.md` added to supporting files index | H2 |
| "First-time setup" section added (points to `setup.md`) | C2 |
| Step 0.5a: batch-limit warning + draft PR exclusion note | M2, H4 |
| Step 0.5b: `--state all` note made more prominent | — |
| Step 0.5d: reinforced batch-limit warning | M2 |
| Step 4.5: multi-category combination table added | M4 |
| Step 5 `mergedAt`: format instruction added | M1 |
| Step 5 URL table: project-specific callout added | H3 |
| Step 5 Pre-conditions: test accounts reference line added | M3 |
| Step 7a body template: `mergedAt` format instruction added | M1 |
| Step 7b: dry-run cleanup commands added | N3 |
| Guardrail: labels fallback for missing `docs/LABELS.md` | H5 |
| Guardrail: `.qa-assignee.local` gitignore requirement | C3 |
| Guardrail: draft PR exclusion confirmation | H4 |
| Guardrail: GitHub API rate-limit recovery guidance | M5 |
| Changelog section added | N2 |

### `references/setup.md` (new file)

| Section | Fixes |
|---|---|
| Step 1 — Install and authenticate `gh` CLI | H1 |
| Step 2 — Fill configuration placeholders (full table + GraphQL queries) | C1 |
| Step 3 — Update URL mapping table for the project | H3 |
| Step 4 — Add test accounts reference | M3 |
| Step 5 — Add `.gitignore` entry | C3 |
| Step 6 — Verify the setup with a dry-run | C2 |
| Rate-limit and slowness recovery | M5 |

### `references/smoke-test.md` (modified)

| Change | Fixes |
|---|---|
| Replaced `Rochanay` with `qa-tester` (3 occurrences) | N1 |

---

## Impact Summary

| Area | Before | After |
|---|---|---|
| First-time usability | Fails immediately — no setup guide, placeholders never documented | 6-step setup guide with verification; works on first run |
| Data safety | QA assignee username could end up in Git history | `.gitignore` entry required before first save |
| Reliability | Silent failures on rate limits; no recovery path | Rate-limit check + partial-failure recovery documented |
| Test plan quality | Dates in ISO format; ambiguous variant for multi-category PRs | Human-readable dates; 5 concrete multi-category examples |
| QA onboarding | "Sign in as admin" with no credentials reference | Every handoff links to team's test account store |
| Trigger accuracy | 4 phrases | 11 phrases — covers more natural-language variations |
| Maintainability | `report-templates.md` invisible in index; no changelog | All reference files indexed; full changelog at end of skill |
| Large backlogs | Silent truncation at 30 PRs | Explicit warning when limit is hit |

---

*All 17 identified issues resolved. Skill is production-ready for team use.*
