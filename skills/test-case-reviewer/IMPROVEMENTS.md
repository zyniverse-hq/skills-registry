# IMPROVEMENTS — test-case-reviewer

> Improvement plan derived from SKILL.md + ANALYSIS.md audit against the agentskills.openml.io spec.

---

## Quick Summary

| | Before | After |
|---|---|---|
| Spec compliance | Partially compliant | Fully compliant |
| Critical violations | 4 | 0 |
| Agent discoverability | Medium | High |
| Portability | Fails | Pass |

---

## Improvement 1 — Nest all non-standard frontmatter fields under `metadata:`

### What needs to change

Eight custom fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`) are declared at the top level of the frontmatter. The agentskills spec requires every non-standard field to be nested under a `metadata:` block. Top-level placement makes the frontmatter invalid and may cause parsers to silently drop these fields or reject the skill entirely.

### Before
```yaml
---
name: test-case-reviewer
description: This skill should be used when the user asks to "review test cases"...
version: 1.0.0
author: Rachayya Choukimath
email: rachayya.choukimath@zysk.tech
category: qa-testing
tags:
  - test-case-review
  - coverage-analysis
  - qa-automation
  - spec-traceability
  - excel-report
product: zysk
sprint: 1
tested_with: claude-sonnet-4-6
---
```

### After
```yaml
---
name: test-case-reviewer
description: This skill should be used when the user asks to "review test cases"...
license: MIT
compatibility: Windows with Python 3.14+ and py launcher (C:\Windows\py.exe). Requires openpyxl 3.1.5 (pre-installed). Output is an Excel .xlsx file. Claude claude-sonnet-4-6 or later recommended.
metadata:
  version: 1.0.0
  author: Rachayya Choukimath
  email: rachayya.choukimath@zysk.tech
  category: qa-testing
  tags:
    - test-case-review
    - coverage-analysis
    - qa-automation
    - spec-traceability
    - excel-report
  product: zysk
  sprint: 1
  tested_with: claude-sonnet-4-6
---
```

### Impact if implemented
- **Agent behaviour:** Skill registries and orchestration layers that validate frontmatter will now parse correctly — no fields silently dropped or rejected.
- **Discoverability:** `category`, `tags`, and `tested_with` become queryable through standard metadata lookups, making the skill surfaceable in category-filtered searches (e.g., `qa-testing`).
- **Portability:** Spec-compliant frontmatter is portable across any registry that follows the agentskills standard — not just the original author's setup.
- **Risk reduced:** Prevents silent parse failures where a registry consumes the file but discards all custom fields because they are not wrapped correctly.

### Existing use (before fix)
Today, when the skills registry parses `SKILL.md`, the eight custom fields sit at the root YAML level alongside `name` and `description`. Any parser enforcing the agentskills spec will either reject the skill as malformed or silently ignore the non-standard top-level keys. The `category: qa-testing` tag — which is the primary mechanism for filtering skills by domain — is not reachable through a spec-compliant metadata lookup. An agent searching for QA-testing skills by category may never surface this skill at all, even though its body is highly detailed and well-structured.

### Improved use (after fix)
After the fix, the frontmatter is fully spec-compliant. The registry can index `category`, `tags`, `tested_with`, and `version` through the standard `metadata` path. An agent or orchestration layer looking for `qa-testing` skills will find `test-case-reviewer` immediately. The `tested_with: claude-sonnet-4-6` field is now also visible at parse time, allowing orchestrators to route requests to the correct model tier without reading the body.

---

## Improvement 2 — Add the required `license` field

### What needs to change

The `license` field is mandatory per the agentskills spec and is entirely absent from the frontmatter. Without it, the skill is considered incomplete by any spec-enforcing validator, and redistribution terms are undefined for anyone consuming the skill from the registry.

### Before
```yaml
---
name: test-case-reviewer
description: This skill should be used when the user asks to "review test cases"...
version: 1.0.0
author: Rachayya Choukimath
# license field is absent
---
```

### After
```yaml
---
name: test-case-reviewer
description: This skill should be used when the user asks to "review test cases"...
license: MIT
metadata:
  version: 1.0.0
  author: Rachayya Choukimath
  ...
---
```

### Impact if implemented
- **Agent behaviour:** No direct change to runtime behaviour, but validators and CI pipelines that gate on spec compliance will now pass for this skill.
- **Discoverability:** Skills with a declared license are treated as publishable by registry tooling — this skill becomes eligible for inclusion in public or shared registries.
- **Portability:** Any team picking up this skill knows immediately that it is MIT-licensed and can be used, modified, and redistributed without legal ambiguity.
- **Risk reduced:** Eliminates the compliance gap that causes automated spec checkers to report this skill as failing the required-fields audit.

### Existing use (before fix)
Today, any CI pipeline or spec validator running against the skills registry will flag `test-case-reviewer` as non-compliant because the `license` field is missing. If the registry enforces a required-fields check before indexing, the skill may be excluded from the live registry entirely. Teams wanting to reuse or adapt the skill have no declared terms to rely on.

### Improved use (after fix)
Adding `license: MIT` takes one line. Once present, the skill passes the required-fields check, can be indexed by registry tooling, and is unambiguously reusable. The fix has zero impact on skill execution but closes the compliance gap and makes the skill publishable.

---

## Improvement 3 — Add the `compatibility` field for environment prerequisites

### What needs to change

The skill has hard, non-negotiable environment requirements: Windows OS, the `py` launcher at `C:\Windows\py.exe`, Python 3.14.1, and openpyxl 3.1.5. These are documented in the "Excel Generation" section deep in the body — but not in the frontmatter where agents can inspect them before deciding whether to activate the skill. An agent running on Linux or macOS will activate this skill, proceed through all review steps, generate the Python script, and then fail at Step 8 when `py` is not found. The failure is silent until execution time.

### Before
```markdown
<!-- No compatibility field in frontmatter. Requirements buried in body: -->

| Setting | Value |
|---|---|
| Executable | `py` (Windows Python Launcher — `C:\Windows\py.exe`) |
| Python version | 3.14.1 |
| openpyxl version | 3.1.5 — already installed |
```

### After
```yaml
---
name: test-case-reviewer
description: ...
license: MIT
compatibility: Windows with Python 3.14+ and py launcher (C:\Windows\py.exe). Requires openpyxl 3.1.5 (pre-installed). Output is an Excel .xlsx file. Claude claude-sonnet-4-6 or later recommended.
metadata:
  ...
---
```

### Impact if implemented
- **Agent behaviour:** An orchestration layer or agent can read the `compatibility` field before activation and refuse to run the skill on an incompatible platform, producing a clear error instead of a late-stage execution failure.
- **Discoverability:** Platform-aware skill selectors can filter out `test-case-reviewer` for non-Windows environments automatically, preventing wasted execution time.
- **Portability:** Portability does not improve (the skill is Windows-only by design), but the constraint is now declared explicitly — which is the correct approach for a platform-specific skill.
- **Risk reduced:** Eliminates the failure mode where an agent on Linux/macOS runs all 12 review steps, writes the full Python script, and then crashes at `py "gen_tc_review.py"` with no clear explanation.

### Existing use (before fix)
Today, the environment requirements are discoverable only by reading through to the "Excel Generation" section near the bottom of SKILL.md. An agent on a non-Windows machine — or a developer new to the skill — has no frontmatter signal to warn them. The skill will happily proceed through all review and fix steps (which may take significant time on a large test case file), write `gen_tc_review.py` to disk, and then fail at the `py` execution step with a "command not found" error. The user receives no Excel file and no actionable error message from the skill itself.

### Improved use (after fix)
With `compatibility` declared in the frontmatter, an agent or platform layer can detect the Windows-only requirement at skill selection time and either refuse to activate on an incompatible platform or warn the user before any work begins. The skill's environment contract is visible at a glance without reading the full body. This is especially valuable for teams evaluating the skill for inclusion in a multi-platform pipeline.

---

## Improvement 4 — Replace the hardcoded machine-specific execution path

### What needs to change

Step 8 in both the "Steps" section and the "Automated Execution Flow" section contains a hardcoded path that is specific to the original author's machine:

```
py "C:/Users/Rachayya/CPN_Path/gen_tc_review.py"
```

This path embeds a specific Windows username (`Rachayya`) and a project-specific subfolder (`CPN_Path`). On any other machine — including other machines owned by the same author — this path will not exist and the execution step will fail with a "file not found" error. The skill already handles the output Excel file location correctly using `os.getcwd()`, making the hardcoded script path an inconsistency as well as a portability failure.

### Before
```markdown
<!-- In "Steps" section, Step 8: -->
8. **Execute** using the Bash tool: `py "C:/Users/Rachayya/CPN_Path/gen_tc_review.py"`

<!-- In "Automated Execution Flow" section, Step 8: -->
8. **Execute** using the Bash tool: `py "C:/Users/Rachayya/CPN_Path/gen_tc_review.py"`
```

### After
```markdown
<!-- In "Steps" section, Step 8: -->
8. **Execute** the generated script using the Bash tool: `py "gen_tc_review.py"`
   (The script is written to `os.getcwd()` — no hardcoded path needed.)

<!-- In "Automated Execution Flow" section, Step 8: -->
8. **Execute** the generated script using the Bash tool: `py "gen_tc_review.py"`
   (The script is written to `os.getcwd()` — no hardcoded path needed.)
```

### Impact if implemented
- **Agent behaviour:** The Bash tool call in Step 8 will succeed on any Windows machine with the `py` launcher installed, not just on the original author's machine with the specific `CPN_Path` folder.
- **Discoverability:** No change to discoverability.
- **Portability:** This is the primary portability fix. Any team using this skill on their own machine will get a working execution step rather than an immediate path-not-found failure.
- **Risk reduced:** Eliminates the failure mode where the skill completes all review work (Steps 1–7) and writes the full Python script, then fails silently at the execution step because the hardcoded path does not exist on the current machine.

### Existing use (before fix)
Today, when an agent executes Step 8, it runs `py "C:/Users/Rachayya/CPN_Path/gen_tc_review.py"`. On any machine other than Rachayya's original development machine, this path does not exist. The Bash tool returns a "file not found" error. The agent has already completed all review steps, built all four Excel sheets in memory, and written the Python script to `os.getcwd()` — but the Excel file is never produced because the execution path is wrong. The user receives no output and no explanation of what went wrong.

### Improved use (after fix)
After the fix, Step 8 runs `py "gen_tc_review.py"`, which resolves against the current working directory — the same directory where Step 7 wrote the script using the Write tool. The execution succeeds on any Windows machine with `py` installed. The Excel file is produced consistently. The fix also makes the skill self-consistent: the script write path and the script execution path both use `os.getcwd()`, eliminating a confusing asymmetry.

---

## Improvement 5 — Remove duplicate execution steps to reduce token bloat

### What needs to change

The "Steps" section and the "Automated Execution Flow" section both contain the same 9-step numbered sequence. The content is nearly identical across both sections, with the "Automated Execution Flow" section adding "DO NOT" guidance that is not present in "Steps". This duplication contributes approximately 50 lines and 400 tokens of pure redundancy. The skill is already close to the 5,000-token body limit (~4,964 tokens estimated), and the duplicate section pushes it to the edge of the warning threshold.

### Before
```markdown
## Steps

Execute all steps in order without pausing or prompting the user.

1. **Parse spec files** (if provided) ...
2. **Read** all test cases ...
3. **Map spec-to-TC and TC-to-spec** ...
4. **Review** every TC against all 12 criteria ...
5. **Build evaluations** ...
6. **Apply all fixes** ...
7. **Write `gen_tc_review.py`** ...
8. **Execute** using the Bash tool: `py "C:/Users/Rachayya/CPN_Path/gen_tc_review.py"`
9. **Output** the filename only ...

[... Review Sequence (Steps 0-13) ...]

## Automated Execution Flow

Execute all steps in sequence. Do NOT pause, prompt, or ask the user anything between steps. Do NOT check Python version, openpyxl installation, or any package. Do NOT output findings as terminal text.

1. **Parse all spec files** (if provided) ...
2. **Read** all test cases ...
3. **Map spec-to-TC and TC-to-spec** ...
4. **Review** every TC against all 12 criteria ...
5. **Build evaluations** ...
6. **Apply all fixes** ...
7. **Write `gen_tc_review.py`** ...
8. **Execute** using the Bash tool: `py "C:/Users/Rachayya/CPN_Path/gen_tc_review.py"`
9. **Output** the filename only ...
```

### After
```markdown
## Steps

Execute all steps in sequence. Do NOT pause, prompt, or ask the user anything between steps. Do NOT check Python version, openpyxl installation, or any package. Do NOT output findings as terminal text.

1. **Parse spec files** (if provided) — extract all requirement units, merge into one list, tag each with source file name, assign Spec IDs, classify as High / Medium / Low business risk.
2. **Read** all test cases from the provided file.
3. **Map spec-to-TC and TC-to-spec** — assign Covered / Partially Covered / Not Covered to each spec requirement. Flag orphan TCs. Compute coverage %.
4. **Review** every TC against all 12 criteria. Run all audit steps (Steps 5–11 in the Review Sequence). Identify Blocker and Minor failures only.
5. **Build evaluations** — assign B1/B2… (blocker fail), M1/M2… (minor fail) only. No pass rows.
6. **Apply all fixes** — produce corrected 11-column test case tuples. Compute per-TC quality gate results, Review Status, Readiness, Reviewer Comments, Required Corrections, and Defects for Sheet 4.
7. **Write `gen_tc_review.py`** using the Write tool — fully populated, no placeholders. All four sheets included.
8. **Execute** the generated script using the Bash tool: `py "gen_tc_review.py"`
9. **Output** the filename only. Nothing else.

<!-- Remove the entire "Automated Execution Flow" section — its DO NOT guidance moves into the intro line of "Steps" -->
```

### Impact if implemented
- **Agent behaviour:** No change to execution behaviour — both sections describe the same sequence. The merged single section is unambiguous and easier to follow.
- **Discoverability:** No change to discoverability.
- **Portability:** No direct portability impact.
- **Risk reduced:** Reduces estimated token count from ~4,964 to ~4,564, moving the skill comfortably below the 5,000-token warning threshold and creating headroom for future additions (e.g., a worked example).

### Existing use (before fix)
Today, the skill has two nearly identical 9-step sequences separated by the Review Sequence section. The "Steps" section lacks the DO NOT guidance; the "Automated Execution Flow" section lacks the Review Sequence cross-reference. An agent reading both sections sequentially gets no additional information from the second pass — it is purely repeated content. The near-5,000-token body also means any future improvement (adding an example, expanding a reference, clarifying a step) risks pushing the skill over the token limit.

### Improved use (after fix)
After merging, the skill has one canonical execution sequence that includes both the step descriptions and the DO NOT guards. The token count drops by roughly 400 tokens, the body is shorter and clearer, and there is headroom to add a worked example (see Improvement 6) without hitting the token limit.

---

## Improvement 6 — Add a worked example to the body

### What needs to change

The "When to use" section lists 9 trigger phrases and clearly describes what activates this skill. However, there is no concrete example showing what the user provides, what the skill does with it, and what output file is produced. The agentskills spec flags the absence of worked examples as a warning. A minimal 5-10 line example block would significantly improve agent confidence and reduce misactivation.

### Before
```markdown
## When to use

- Activate when: the user asks to "review test cases", "check test case quality", or "validate test case coverage"
- Activate when: the user asks to "review test cases against requirements" or "check for missing test scenarios"
- Activate when: the user asks to "review test case format", "verify test case completeness", or "check automation readiness"
- Activate when: the user provides a test case file (`.xlsx`, `.csv`, or inline table) and requests a review
- Activate when: the user needs quality review, coverage analysis, spec traceability, or format validation of any test case suite
- Do NOT activate when: the user only wants to generate new test cases without reviewing existing ones
- Do NOT activate when: the user is asking general QA methodology questions without providing test cases to review
```

### After
```markdown
## When to use

- Activate when: the user asks to "review test cases", "check test case quality", or "validate test case coverage"
- Activate when: the user asks to "review test cases against requirements" or "check for missing test scenarios"
- Activate when: the user asks to "review test case format", "verify test case completeness", or "check automation readiness"
- Activate when: the user provides a test case file (`.xlsx`, `.csv`, or inline table) and requests a review
- Activate when: the user needs quality review, coverage analysis, spec traceability, or format validation of any test case suite
- Do NOT activate when: the user only wants to generate new test cases without reviewing existing ones
- Do NOT activate when: the user is asking general QA methodology questions without providing test cases to review

## Example

**User input:**
> "Review my test cases against the spec. Here are the files: `login_testcases.xlsx` and `login.feature`."

**What the skill does:**
1. Parses `login.feature` — extracts Scenario titles as spec requirements (e.g., `SR-001: Valid login`, `SR-002: Invalid password`).
2. Reads all test cases from `login_testcases.xlsx`.
3. Maps each TC to a spec requirement; flags TCs with no matching requirement as orphans.
4. Reviews every TC across all 12 criteria — identifies Blockers (e.g., missing expected result) and Minors (e.g., vague test data).
5. Applies fixes — rewrites vague steps, adds missing preconditions, corrects automation readiness classification.
6. Writes and executes `gen_tc_review.py`.

**Output:**
```
Excel file saved: ReviewAndFixed_LOGIN_20240815_143022.xlsx
```
The file contains four sheets: Review Feedback, Fixed Test Cases, Spec Coverage Matrix, and TC Review Status.
```

### Impact if implemented
- **Agent behaviour:** An agent reading the "When to use" section now has a concrete reference point — it can match the user's phrasing and file types against the example and confirm activation is correct.
- **Discoverability:** Examples are the highest-signal content for agent skill selection. A worked example that shows `.xlsx` + `.feature` as inputs directly matches the most common real-world usage pattern.
- **Portability:** No direct portability impact.
- **Risk reduced:** Reduces misactivation — agents considering this skill for tasks like "generate new test cases" or "explain test case best practices" will see the example does not match and correctly skip activation.

### Existing use (before fix)
Today, an agent deciding whether to activate `test-case-reviewer` has 9 trigger phrases and a purpose statement to work with — but no concrete picture of what a real interaction looks like. Agents that rely on example-matching for skill selection will be less confident activating this skill compared to skills that show explicit input-output examples. The risk is both under-activation (agent skips the skill when it should use it) and over-activation (agent uses the skill for a pure test generation task).

### Improved use (after fix)
With a worked example in place, an agent or orchestration layer can match the user's message ("review my test cases against the spec") against the example pattern, confirm the input types (`.xlsx` + `.feature`), and activate the skill with high confidence. The expected output filename format is also visible, so downstream steps that parse the filename for further processing have a reference to work from.

---

## Priority Order

| Priority | Improvement | Effort | Impact |
|---|---|---|---|
| 1 | Fix `metadata:` structure for all non-standard frontmatter fields | Low | Critical |
| 2 | Replace hardcoded `C:/Users/Rachayya/CPN_Path/` execution path | Low | Critical |
| 3 | Add required `license` field | Low | Critical |
| 4 | Add `compatibility` field for Windows/py/openpyxl prerequisites | Low | High |
| 5 | Remove duplicate "Automated Execution Flow" steps section | Low | Medium |
| 6 | Add a worked example to the "When to use" section | Medium | Medium |

---

## Before vs After: Full Skill Experience

### Before (current state)

A developer or team picks up `test-case-reviewer` from the skills registry and tries to use it in a new project on their own machine. The first sign of trouble is at skill registration: the `license` field is absent and all eight custom metadata fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`) sit at the root YAML level instead of under `metadata:`. Any spec-enforcing validator flags the skill as non-compliant and either rejects it from the index or silently drops the category and tag data. The skill may not appear in a `qa-testing` category search at all.

For teams that load the skill anyway — bypassing validation — the experience degrades further at runtime. There is no `compatibility` field to warn non-Windows users, so a developer on macOS or Linux activates the skill, waits through the full 12-step review sequence (which may process dozens of test cases), and then hits a hard failure at Step 8: `py "C:/Users/Rachayya/CPN_Path/gen_tc_review.py"`. The path does not exist on their machine. The entire review — all the spec parsing, TC mapping, evaluation, and fix generation — is discarded with no output and no actionable error. Windows users on the same team experience the same failure because their username is not `Rachayya` and their project is not in `CPN_Path`. The hardcoded path breaks the skill for 100% of users except the original author on the original machine.

Reading the skill body also reveals a structural inefficiency: the 9-step execution sequence is written out twice — once in "Steps" and again in "Automated Execution Flow" — adding approximately 50 lines and 400 tokens of repeated content. With the body already estimated at ~4,964 tokens, the skill is a single minor addition away from exceeding the 5,000-token warning threshold. Any future improvement risks pushing it over the limit.

### After (all improvements applied)

After all six improvements are applied, `test-case-reviewer` is a fully spec-compliant, portable, and discoverable skill. The frontmatter now correctly nests all eight custom fields under `metadata:`, declares `license: MIT`, and surfaces the Windows/py/openpyxl prerequisites in a `compatibility` field. A registry validator passes the skill on all required-fields checks. A `qa-testing` category search returns the skill. An orchestration layer running on Linux reads `compatibility` before activation and immediately routes the request to a Windows agent — or informs the user that the skill requires the Windows `py` launcher — rather than failing 13 steps in.

At runtime, Step 8 executes `py "gen_tc_review.py"` — resolving against `os.getcwd()`, the same directory where the Write tool placed the script in Step 7. The execution succeeds on any Windows machine with `py` installed, regardless of username or project folder name. The Excel file is produced consistently: `ReviewAndFixed_<ModuleCode>_<YYYYMMDD_HHMMSS>.xlsx` in the `Testcases/` subfolder of the current working directory. The duplicate "Automated Execution Flow" section has been removed, consolidating all DO NOT guidance into the single "Steps" section header and dropping the estimated token count to approximately 4,564 — comfortably below the warning threshold. A worked example in the "When to use" section gives agents a concrete input-output reference, reducing both misactivation and activation hesitation. The skill is now ready for shared registry publication and use across any team on a Windows development environment.
