---
name: test-case-reviewer
description: This skill should be used when the user asks to "review test cases", "review existing test cases against feature specs", "check test case quality", "validate test case coverage", "review test cases against requirements", "check for missing test scenarios", "review test case format", "verify test case completeness", "check automation readiness", or needs quality review, coverage analysis, spec traceability, or format validation of any test case suite. Supports reviewing against one or more feature specification or requirement files. To generate new test cases from a spec, use test-case-generator.
metadata:
  version: 1.0.1
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

# Test Case Review Skill

> Review test cases for quality, coverage, spec traceability, and automation readiness — outputs a structured Excel report with fixes applied automatically.

## When to use

- Activate when: the user asks to "review test cases", "check test case quality", or "validate test case coverage"
- Activate when: the user asks to "review test cases against requirements" or "check for missing test scenarios"
- Activate when: the user asks to "review test case format", "verify test case completeness", or "check automation readiness"
- Activate when: the user provides a test case file (`.xlsx`, `.csv`, or inline table) and requests a review
- Activate when: the user needs quality review, coverage analysis, spec traceability, or format validation of any test case suite
- Do NOT activate when: the user only wants to generate new test cases without reviewing existing ones
- Do NOT activate when: the user is asking general QA methodology questions without providing test cases to review

## Purpose

Review test cases for requirement coverage, clarity, correctness, defect-detection value, maintainability, automation readiness, and release risk. Be specific and rigorous. Call out gaps directly and recommend concrete fixes. Apply all fixes autonomously — do not request clarification.

When the user provides test cases for structured review, produce one Excel file with four sheets:

- **Sheet 1 — Review Feedback:** 10-row summary block + 7-column evaluation table (Blocker and Minor fails only — no pass rows) + auto-computed verdict.
- **Sheet 2 — Fixed Test Cases:** all corrected test cases in the standard 11-column format.
- **Sheet 3 — Spec Coverage Matrix:** spec requirements mapped to coverage status, linked TC IDs, and gap notes. Generated only when one or more feature/requirement files are provided.
- **Sheet 4 — TC Review Status:** per-TC quality gate results (Execution Ready, Client Deliverable, Production Ready), Review Status, Readiness, Reviewer Comments, Required Corrections, and Defects. Always generated — one row per TC.

End-to-end automated. No terminal output of findings. No prompts to the user. No environment checks. The Excel file is the only output.

---

## Inputs

### Primary inputs (use all that are provided):

| Input | Format | Used for |
|---|---|---|
| Feature / requirement file(s) | `.feature` (Gherkin), `.md` (spec), `.txt` (numbered AC list), user story doc — one or more files accepted | Spec requirement list — source of truth for traceability. When multiple files are provided, merge all into one numbered requirement list and tag each with its source file name. |
| Test cases file | `.xlsx`, `.csv`, inline table | Test cases to review |

### Supporting inputs (optional):

API schema, UI flows, security design, performance budget, test type, or target environment.

If no spec file is provided, skip Steps 0, 3, 3b, and Sheet 3. Label the review "Structural Review Only — No Spec Traceability."

---

## Steps

Execute all steps in order without pausing or prompting the user.

1. **Parse spec files** (if provided) — extract all requirement units, merge into one list, tag each with source file name, assign Spec IDs, classify as High / Medium / Low business risk.
2. **Read** all test cases from the provided file.
3. **Map spec-to-TC and TC-to-spec** — assign Covered / Partially Covered / Not Covered to each spec requirement. Flag orphan TCs. Compute coverage %.
4. **Review** every TC against all 12 criteria. Run all audit steps (Steps 5–11 in the Review Sequence below). Identify Blocker and Minor failures only.
5. **Build evaluations** — assign B1/B2… (blocker fail), M1/M2… (minor fail) only. No pass rows.
6. **Apply all fixes** — produce corrected 11-column test case tuples. Compute per-TC quality gate results, Review Status, Readiness, Reviewer Comments, Required Corrections, and Defects for Sheet 4.
7. **Write `gen_tc_review.py`** using the Write tool — fully populated, no placeholders. All four sheets included. See `references/python-template.md` for the complete script template.
8. **Execute** using the Bash tool: `python3 gen_tc_review.py`
9. **Output** the filename only. Nothing else.

See **Review Sequence** below for the detailed step-by-step review instructions.

---

## Review Sequence

Follow all steps in order. Do not skip steps.

**Step 0 — Parse all spec files (when provided)**
Extract every requirement unit from each provided file. BDD `.feature`: each `Scenario:` or `Scenario Outline:` title. Markdown spec: each `### AC-NNN` heading or numbered AC bullet. User story doc: each acceptance criterion bullet. Plain text: each numbered or bulleted requirement line. When multiple files are provided, merge all into one numbered list and tag each requirement with its source file name. Assign Spec IDs (use document IDs if present; otherwise `SR-001`, `SR-002`, …). Classify each as High / Medium / Low business risk.

**Step 1 — Identify the test scope**
Identify the feature, module, API, user flow, or release area being tested.

**Step 2 — Extract or infer acceptance criteria**
Extract from the merged spec list (Step 0) or infer from the test cases themselves when no spec was provided.

**Step 3 — Spec-to-TC mapping (when spec is provided)**
For each spec requirement, find all TCs that cover it. Assign: Covered (at least one TC fully validates including negative/boundary where warranted), Partially Covered (happy path only — negative or boundary missing), Not Covered (no TC addresses this requirement).

**Step 3b — TC-to-spec orphan detection (when spec is provided)**
For each TC, confirm it traces to at least one spec requirement. A TC with no matching spec requirement is an Orphan TC — flag as Minor.

**Step 4 — Structural review per TC**
Review each TC against all 12 criteria in the Controlled Criterion List (see `references/sheet-specifications.md`). While reviewing, also detect and flag under the most relevant criterion: vague wording, hidden assumptions, chained state dependencies, non-deterministic behavior, and unmeasurable expected results. **Skip the Spec Traceability criterion (criterion 12) when no spec file was provided — do not flag orphan TCs or missing traceability under this criterion in that case.**

**Step 5 — Test type coverage audit and depth check**
Verify the suite covers all required test types. Missing types: Blocker if Functional, Negative, or E2E is absent for a non-trivial feature; Minor if Smoke, Sanity, Integration, System, Boundary/Edge, Security, UI/UX, State/Workflow, or NFR is absent. Also verify depth — a high-risk area covered by only 1 TC where 3+ are warranted is a risk signal.

| Test Type | What to look for |
|---|---|
| Functional | Happy-path TCs validating core feature behavior end-to-end |
| Negative | TCs submitting invalid input, breaching rules, or triggering rejection/error |
| Boundary / Edge case | TCs at value limits (min, max, min-1, max+1), empty, null, zero, overflow |
| Smoke | Lightweight TC verifying the feature works at a basic level |
| Sanity | TCs verifying no regression in closely related existing features |
| Integration | TCs validating cross-system data flow, API-to-UI sync, or third-party calls |
| E2E (End-to-End) | At least one TC tracing the full user journey from entry to final observable state |
| System | TCs verifying complete system response including all components (DB, API, UI) |
| Security | TCs for auth, permission, token, and data-exposure scenarios |
| UI/UX | TCs for labels, layout, error messages, empty states, navigation |
| State / Workflow | TCs verifying state transitions, data persistence, multi-step progression |
| NFR | TCs for performance, concurrency, atomicity, reliability |

**Step 6 — Risk-based prioritization audit**
For each spec requirement, use the business risk classification from Step 0. High risk: must have Functional + Validation + Error Handling + State/Workflow TCs — flag if fewer than 3 TCs covering different categories. Medium risk: must have Functional + Validation TCs minimum. Low risk: Functional TC minimum.

**Step 7 — Negative coverage ratio check**
For each module or feature, count positive TCs (Functional) vs negative TCs (Validation + Error Handling). A ratio below 1:1 is a risk signal — flag the module and list the missing negative scenarios.

**Step 8 — Duplicate intent detection**
Flag any two TCs that test the same behavior with only surface-level variation. Consolidate duplicates into one parameterized TC with a test data table.

**Step 9 — Precondition dependency chain detection**
Flag any TC whose precondition requires a previous TC to have executed. These are execution-order dependencies that make the suite fragile and block parallel execution.

**Step 10 — Test data completeness audit**
For every TC marked `Automatable`, verify test data is fully specified with exact values. Flag any TC with vague data containing "valid", "any", "some", "appropriate", or similar non-specific descriptors.

**Step 11 — E2E flow coverage check**
Verify the suite covers at least one complete user journey end-to-end for each major workflow. Flag workflows with no E2E coverage.

**Step 12 — Classify automation readiness and quality gates**
For each TC: evaluate automation candidacy using the six conditions below. Classify as Automation-ready / Manual-only / Partially Automatable. Verify the existing Automation Readiness column value — flag misclassifications. Evaluate each TC against the three quality gates: Execution-ready, Client-deliverable, Production-ready. Determine Review Status: Rejected (Blockers present) / Needs Fix (Minors only) / Approved (no issues).

**Automation Candidacy Conditions — a TC is a good automation candidate when it is:**

| # | Condition | Description |
|---|---|---|
| 1 | **Stable** | Requirements and UI/API behavior are not changing frequently. |
| 2 | **Repeatable** | It can run multiple times with consistent results. |
| 3 | **High-value** | It covers critical business, user, security, or revenue-impacting functionality. |
| 4 | **Low-flaky** | It does not heavily depend on unstable timing, random behavior, third-party instability, OTP, CAPTCHA, or unreliable environments. |
| 5 | **Clearly assertable** | Pass/fail conditions can be validated objectively. |
| 6 | **Maintainable** | Automation effort and long-term maintenance cost are reasonable. |

**Decision Rule:** If a TC fails 2 or more of the above conditions, classify it as `Not Automatable`. Keep it manual, flag it for redesign, stabilize its dependencies, or recommend moving validation to a lower testing layer (API or unit test).

**Selection Priority — automate first:**
- Stable flows
- Frequently executed flows
- High business impact scenarios
- Regression and smoke validations
- Flows with clear assertions and reusable components

**Avoid or delay automation for:**
- Frequently changing features
- Highly flaky scenarios
- Low-value validations
- Visual-only checks
- Heavy manual dependency flows

> Automation must be selective, practical, and value-driven — not coverage-driven. A smaller stable automation suite is far more valuable than a large unstable suite nobody trusts. It is NOT mandatory that all test cases be automated.

**Step 13 — Build evaluations and produce output**
Assign B/M codes per TC per criterion for all failures only. Do not generate pass rows. Determine the overall suite Verdict (see `references/quality-gates.md`). Apply all fixes. Produce the Excel file.

---

## Automated Execution Flow

Execute all steps in sequence. Do NOT pause, prompt, or ask the user anything between steps. Do NOT check Python version, openpyxl installation, or any package. Do NOT output findings as terminal text.

1. **Parse all spec files** (if provided) — extract all requirement units, merge into one list, tag each with source file name, assign Spec IDs, classify as High / Medium / Low business risk.
2. **Read** all test cases from the provided file.
3. **Map spec-to-TC and TC-to-spec** — assign Covered / Partially Covered / Not Covered to each spec requirement. Flag orphan TCs. Compute coverage %.
4. **Review** every TC against all 12 criteria. Run all audit steps (Steps 5–11). Identify Blocker and Minor failures only.
5. **Build evaluations** — assign B1/B2… (blocker fail), M1/M2… (minor fail) only. No pass rows.
6. **Apply all fixes** — produce corrected 11-column test case tuples. Compute per-TC quality gate results, Review Status, Readiness, Reviewer Comments, Required Corrections, and Defects for Sheet 4.
7. **Write `gen_tc_review.py`** using the Write tool — fully populated, no placeholders. All four sheets included. See `references/python-template.md` for the complete script template.
8. **Execute** using the Bash tool: `python3 gen_tc_review.py`
9. **Output** the filename only. Nothing else.

---

## Required Quality Checklist

Verify before writing the Python script:

- All 11 required columns are present in each tuple, in the exact required order.
- No extra columns added. No position left as an empty string — use `N/A`.
- Module Name is a broad product, domain, system, or pipeline area.
- Feature Name is a flow, story, or workstream inside the module — not a capability name.
- Test Case Category uses the controlled taxonomy (8 values only — see `references/taxonomy.md`).
- Each test case validates one primary behavior.
- Test steps are numbered and written as separate lines using `\n` inside the Python string literal.
- No literal `\\n` text appears as visible content in any cell. No HTML tags in any value.
- Expected Result is specific and verifiable — no vague language.
- Severity is one of: Critical, High, Medium, Low.
- Automation Readiness is one of: Automatable, Partially Automatable, Not Automatable. Assessed using the 6-condition rule: Stable, Repeatable, High-value, Low-flaky, Clearly assertable, Maintainable. A TC failing 2 or more conditions must be classified `Not Automatable`.
- Test Case IDs are sequential and unique. Duplicate or near-duplicate tests are consolidated.
- All required test types are verified for coverage.
- Spec traceability verified — every TC maps to a spec requirement, every spec requirement maps to at least one TC (when spec file is provided).
- Multiple spec files merged into one requirement list with source file tag.
- **Evaluation table contains only Blocker and Minor fail rows — no pass rows.**
- Every TC has quality gate values: Execution Ready (Yes/No), Client Deliverable (Yes/No), Production Ready (Yes/No).
- Review Status assigned per TC: Rejected / Needs Fix / Approved.
- Reviewer Comments, Required Corrections, and Defects populated per TC — "No issues found" or "None" when no issues.
- **Sheet 3 generated only when a spec file is provided — `SPEC_PROVIDED = True/False` set correctly.**
- **Sheet 4 always generated — one row per TC.**
- Excel file saved to `Testcases/` subfolder of `os.getcwd()` — no hardcoded path.
- `py` used as the executable — no fallbacks.

---

## Output

- **Format:** Excel file (`.xlsx`) with four sheets
- **Location:** `Testcases/` subfolder of `os.getcwd()` — created automatically
- **File name:** `ReviewAndFixed_<ModuleCode>_<YYYYMMDD_HHMMSS>.xlsx`
- **Example:** `ReviewAndFixed_AUTH_20240815_143022.xlsx`

Final response contains only:

```
Excel file saved: ReviewAndFixed_<ModuleCode>_<YYYYMMDD_HHMMSS>.xlsx
```

---

## Excel Generation

**File name:** `ReviewAndFixed_<ModuleCode>_<YYYYMMDD_HHMMSS>.xlsx`
**Save location:** `Testcases/` subfolder of `os.getcwd()` — created with `os.makedirs(out_dir, exist_ok=True)`.
**Executable:** `py` only — never `python`, `python3`, or a full path.
**openpyxl 3.1.5 is pre-installed** — never add install checks, version checks, or pip commands.
**Method:** Write tool then Bash tool — no heredoc.

See `references/python-template.md` for the full script template with all sheet structures, style objects, variable definitions, tuple formats, and the auto-verdict computation block.

| Setting | Value |
|---|---|
| Executable | `py` (Windows Python Launcher — `C:\Windows\py.exe`) |
| Python version | 3.14.1 |
| openpyxl version | 3.1.5 — already installed |

---

## Reference Files

| File | Contents |
|---|---|
| `references/python-template.md` | Complete `gen_tc_review.py` script template — all 4 sheets, shared styles, variable reference, tuple formats, auto-verdict block |
| `references/sheet-specifications.md` | Sheet 1–4 column definitions, Controlled Criterion List (12 criteria), row color coding, styling rules |
| `references/quality-gates.md` | Review Quality Gates (3 gates), Automation Separation (3 tiers + terminology mapping), Verdict Rules, Review Tone |
| `references/taxonomy.md` | Controlled Categories (8 values + mapping table), Taxonomy Rules (Module/Feature/Category), Severity table, TC ID Rules, Format Rules |
| `references/review-standards.md` | Detailed criteria definitions for Steps 4–11: Requirement Coverage, Spec Traceability, Test Type Coverage, Risk Prioritization, Negative Ratio, Duplicate Detection, Dependency Chain, Test Data, E2E Coverage, Clarity, Atomicity, Determinism, UI Review, Markdown Review output format |

---

## Output Token Limit Protection

Write large outputs to files. Keep the final response minimal.

1. Do not print generated test cases in chat.
2. Do not print review findings in chat unless explicitly requested.
3. Do not print the full Python script in chat.
4. Final response must be only:

```
Excel file saved: ReviewAndFixed_<ModuleCode>_<YYYYMMDD_HHMMSS>.xlsx
```

---

## Notes

- If no spec file is provided, Sheet 3 is skipped and the review is labeled "Structural Review Only — No Spec Traceability."
- Multiple spec files are merged into one requirement list; each requirement is tagged with its source file name.
- Automation must be selective and value-driven — not coverage-driven. A TC failing 2 or more of the 6 automation candidacy conditions must be classified `Not Automatable`.

## Never Do

- Output test case data or review findings in chat as a table or TSV block (unless the user explicitly requests it).
- Use a bash heredoc (`py << 'PYEOF'`) — unreliable on this machine for large scripts.
- Hardcode a save path or ask the user for one.
- Use `python`, `python3`, or a full path — always use `py`.
- Run an openpyxl install check — it is already installed (v3.1.5).
- Leave any tuple positions as placeholders or empty strings.
- Generate Sheet 3 when no spec file was provided — set `SPEC_PROVIDED = False`.
- Leave `SPEC_PROVIDED = True` when no spec file was provided in this session.
- Write pass rows in the evaluation table — fails only.
- Add a "Status" or "Pass/Fail" column in the evaluation table — the table is fails-only.
- Omit Sheet 4 — it is always required regardless of whether a spec file is provided.
- Leave Reviewer Comments, Required Corrections, or Defects cells blank — use "No issues found" or "None".
- Hardcode `verdict_value` — the auto-computation block derives it from `blocker_count`, `_b_ratio`, `_miss_crit`, and `coverage_pct`.
- Use a Test Case Category value outside the Controlled Categories list.
- Mark a TC as `Automatable` when it fails 2 or more of the 6 automation candidacy conditions (Stable, Repeatable, High-value, Low-flaky, Clearly assertable, Maintainable).
- Force `Automatable` on every TC to maximize automation coverage — automation must be selective and value-driven, not coverage-driven.
- Automate TCs that are frequently changing, highly flaky, visual-only, or have heavy manual dependencies without flagging them as `Not Automatable`.
