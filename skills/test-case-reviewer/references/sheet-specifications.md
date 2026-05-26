# Sheet Specifications

Column definitions, row color coding, and styling rules for all four Excel sheets.

---

## Sheet 1 — Review Feedback

Sheet name: `Review Feedback`

### Summary Block (rows 1–10, blank row 11, evaluation table header at row 12)

| Row | Label | Value |
|---|---|---|
| 1 | Total Test Cases Reviewed | N |
| 2 | Total Issues Found — Blocker | count |
| 3 | Total Issues Found — Minor | count |
| 4 | Total Issues Found | Blocker + Minor |
| 5 | Test Types Covered | comma-separated list of test types present |
| 6 | Test Types Missing | comma-separated list absent (or "None") |
| 7 | Total Spec Requirements | N (or "N/A — No spec file provided") |
| 8 | Requirements Covered | n (or N/A) |
| 9 | Coverage % | n/N × 100% (or N/A) |
| 10 | Verdict | Approved / Approved with changes / Needs rework |

### Evaluation Table — 7 Columns (fails only — no pass rows)

| Column | Content |
|---|---|
| Check # | B1, B2… (blocker fail) · M1, M2… (minor fail) |
| TC ID | Test Case ID |
| Criterion | From Controlled Criterion List below |
| Current Value | Value found in the reviewed test case |
| Finding | Description of the problem |
| Suggested Fix | Corrected value or instruction |
| Result Type | Blocker / Minor |

Sort: Blocker rows (B1, B2…) sorted by TC ID first, then Minor rows (M1, M2…) sorted by TC ID.

### Controlled Criterion List (12 criteria)

| Criterion | What to check | Failure type |
|---|---|---|
| Test Case ID | Sequential, unique, matches pattern | Blocker |
| Module Name | Present, non-empty, valid product/domain area | Blocker |
| Feature Name | Flow-first naming; not capability or sub-feature name | Blocker |
| Test Case Category | From controlled list; not informal or unmapped label | Blocker |
| Test Case Summary | Clear, unique, one primary behavior | Minor |
| Pre-conditions | Present, valid, sufficient to set up the test | Minor |
| Test Steps | Numbered, complete, logical, no missing actions or system responses | Blocker |
| Expected Result | Specific, observable, pass/fail testable; no vague language | Blocker |
| Test Data | Real values where needed; N/A only when truly not required | Minor |
| Severity | From controlled list (Critical/High/Medium/Low); not over- or under-assigned | Minor |
| Automation Readiness | Evaluated against all 6 conditions (Stable, Repeatable, High-value, Low-flaky, Clearly assertable, Maintainable). Failing 2 or more conditions mandates `Not Automatable`. Misclassification where TC is marked `Automatable` but fails 2+ conditions is a Blocker; any other misclassification (wrong tier but TC is not being over-promoted) is a Minor. | Blocker / Minor |
| Spec Traceability | TC maps to at least one spec requirement; no orphan TCs (skip entirely if no spec file provided) | Blocker |

### Sheet Styling

| Element | Style |
|---|---|
| Header row | Fill `1F4E79`, white bold Calibri 11, centered, wrap text |
| Summary label column | Bold |
| Blocker rows | Fill `FCE4D6`, left border `C00000` |
| Minor rows | Fill `FFF2CC`, left border `ED7D31` |
| Verdict — Approved | Bold, fill `E2EFDA` |
| Verdict — Approved with changes | Bold, fill `FFF2CC` |
| Verdict — Needs rework | Bold, fill `FCE4D6` |
| Coverage % ≥ 80% | Bold, fill `E2EFDA` |
| Coverage % 50–79% | Bold, fill `FFF2CC` |
| Coverage % < 50% | Bold, fill `FCE4D6` |

---

## Sheet 2 — Fixed Test Cases

Sheet name: `Fixed Test Cases`

Standard 11-column format. Every Blocker and Minor issue corrected.

- Headers: `["Test Case ID", "Module Name", "Feature Name", "Test Case Category", "Test Case Summary", "Pre-conditions", "Test Steps", "Test Data (if applicable)", "Expected Result", "Severity", "Automation Readiness"]`
- Header styling: fill `1F4E79`, white bold Calibri 11, centered, wrap text, row height 30.
- Data rows: Calibri 10, wrap text, top-aligned.
- Alternating row fill: `D6E4F0`.
- Severity left-border (column A, medium): Critical `C00000` · High `FF0000` · Medium `ED7D31` · Low `70AD47`.
- All other borders: thin black.
- Column widths: `[15, 25, 22, 22, 55, 45, 65, 40, 65, 12, 24]`
- Freeze pane at `A2`. Auto-filter: `A1:K{ws.max_row}`.
- Tuple: `(TC_ID, Module, Feature, Category, Summary, PreConds, Steps, TestData, ExpResult, Severity, AutomationReadiness)`

---

## Sheet 3 — Spec Coverage Matrix

Sheet name: `Spec Coverage Matrix`

**Generated only when one or more spec/requirement files are provided. Omit entirely if `SPEC_PROVIDED = False`.**

### Columns (8 columns):

| Column | Content |
|---|---|
| Spec ID | Requirement ID from spec file (or SR-001, SR-002… if none in doc) |
| Source File | Name of the spec/requirement file this requirement came from |
| Requirement / Scenario | Full requirement text or scenario title |
| Business Risk | High / Medium / Low |
| Coverage Status | Covered / Partially Covered / Not Covered |
| Linked TC IDs | Comma-separated TC IDs covering this requirement; "—" if none |
| Gap Notes | What is missing; N/A if Covered |
| Required Action | Add TCs / Expand TCs / No action |

### Row color coding:

| Coverage Status | Fill | Left border |
|---|---|---|
| Covered | `E2EFDA` | `70AD47` (green, medium) |
| Partially Covered | `FFF2CC` | `ED7D31` (amber, medium) |
| Not Covered | `FCE4D6` | `C00000` (red, medium) |

### Styling:
- Header: fill `1F4E79`, white bold Calibri 11, centered, wrap text, row height 30.
- Data rows: Calibri 10, wrap text, top-aligned.
- Column widths: `[12, 30, 60, 15, 22, 35, 60, 18]`
- Freeze `A2`. Auto-filter: `A1:H{ws.max_row}`.
- Tuple: `(SpecID, SourceFile, RequirementText, BusinessRisk, CoverageStatus, LinkedTCIDs, GapNotes, RequiredAction)`

---

## Sheet 4 — TC Review Status

Sheet name: `TC Review Status`

**Always generated — one row per TC regardless of whether a spec file was provided.**

### Columns (9 columns):

| Column | Content |
|---|---|
| TC ID | Test Case ID |
| Review Status | Approved (no issues) · Needs Fix (Minor issues only) · Rejected (Blocker issues present) |
| Readiness | Automation-ready · Partially Automatable · Manual-only — derived by applying the 6-condition gate (Stable, Repeatable, High-value, Low-flaky, Clearly assertable, Maintainable) to the TC. A TC failing 2 or more conditions is always `Manual-only` regardless of the original column value. |
| Execution Ready | Yes / No — based on issues on Test Steps, Pre-conditions, Test Data |
| Client Deliverable | Yes / No — based on issues on Expected Result, Severity, Test Case Summary, or any Blocker |
| Production Ready | Yes / No — Execution Ready + Client Deliverable + No Blockers |
| Reviewer Comments | All findings for this TC (Blocker and Minor), concatenated; "No issues found" if none |
| Required Corrections | All suggested fixes, concatenated; "None" if no issues |
| Defects | All Blocker-level findings (quality defects in the TC); "None" if no Blockers |

### Quality gate derivation logic:

**Execution Ready = No** when the TC has any issue (Blocker or Minor) on: Test Steps, Pre-conditions, or Test Data.

**Client Deliverable = No** when the TC has any issue on: Expected Result, Severity, or Test Case Summary — OR when the TC has any Blocker at all.

**Production Ready = No** when: Execution Ready = No, OR Client Deliverable = No, OR the TC has any Blocker issue. A TC marked `Automatable` that fails 2 or more of the 6 automation candidacy conditions raises a Blocker on the Automation Readiness criterion — this also sets Production Ready = No.

**Review Status:**
- Rejected — TC has one or more Blocker issues.
- Needs Fix — TC has one or more Minor issues and no Blockers.
- Approved — TC has zero Blocker or Minor issues.

**Readiness mapping and override rule:**
- `Automatable` → `Automation-ready` — only when the TC passes all 6 candidacy conditions.
- `Partially Automatable` → `Partially Automatable` — TC passes 4 or 5 of 6 conditions.
- `Not Automatable` → `Manual-only` — TC fails 2 or more of 6 conditions.
- **Override:** If the original TC column says `Automatable` but the 6-condition evaluation finds 2 or more failures, output `Manual-only` in this column and raise a Blocker on the Automation Readiness criterion in Sheet 1.
- Automation is selective and value-driven. Do not inflate `Automation-ready` counts. Not every TC is expected to be automated.

### Row color coding (by Review Status):

| Review Status | Fill | Left border |
|---|---|---|
| Approved | `E2EFDA` | `70AD47` (green, medium) |
| Needs Fix | `FFF2CC` | `ED7D31` (amber, medium) |
| Rejected | `FCE4D6` | `C00000` (red, medium) |

### Styling:
- Header: fill `1F4E79`, white bold Calibri 11, centered, wrap text, row height 30.
- Data rows: Calibri 10, wrap text, top-aligned.
- Column widths: `[15, 18, 22, 18, 20, 20, 60, 60, 55]`
- Freeze `A2`. Auto-filter: `A1:I{ws.max_row}`.
