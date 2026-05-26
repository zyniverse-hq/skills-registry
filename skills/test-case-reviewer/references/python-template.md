# Python Script Template — gen_tc_review.py

Full script structure for the four-sheet Excel review output.

---

## Complete Template

```python
import openpyxl, os
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from datetime import datetime
from collections import defaultdict

wb = openpyxl.Workbook()

# ── Shared style objects ───────────────────────────────────────────────────────
hdr_font       = Font(name="Calibri", bold=True, color="FFFFFF", size=11)
hdr_fill       = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
hdr_align      = Alignment(horizontal="center", vertical="center", wrap_text=True)
bold_font      = Font(name="Calibri", bold=True, size=10)
row_font       = Font(name="Calibri", size=10)
data_alignment = Alignment(vertical="top", wrap_text=True)
thin           = Side(style="thin")
thin_border    = Border(left=thin, right=thin, top=thin, bottom=thin)
alt_fill       = PatternFill(start_color="D6E4F0", end_color="D6E4F0", fill_type="solid")
no_fill        = PatternFill(fill_type=None)
blocker_fill   = PatternFill(start_color="FCE4D6", end_color="FCE4D6", fill_type="solid")
minor_fill     = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
covered_fill   = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")
appr_fill4     = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")
fix_fill4      = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
rej_fill4      = PatternFill(start_color="FCE4D6", end_color="FCE4D6", fill_type="solid")
bl_border      = Side(style="medium", color="C00000")
mn_border      = Side(style="medium", color="ED7D31")
cov_border     = Side(style="medium", color="70AD47")
part_border    = Side(style="medium", color="ED7D31")
nocov_border   = Side(style="medium", color="C00000")
appr_side4     = Side(style="medium", color="70AD47")
fix_side4      = Side(style="medium", color="ED7D31")
rej_side4      = Side(style="medium", color="C00000")
sev_hex        = {"Critical": "C00000", "High": "FF0000", "Medium": "ED7D31", "Low": "70AD47"}

# ── Sheet 1: Review Feedback ───────────────────────────────────────────────────
ws1 = wb.active
ws1.title = "Review Feedback"

# Summary variables — replace all values before writing the script
N              = 0        # replace: total test cases reviewed
blocker_count  = 0        # replace: total blocker failure rows
minor_count    = 0        # replace: total minor failure rows
types_covered  = ""       # replace: comma-separated test types present (e.g. "Functional, Negative, Smoke")
types_missing  = ""       # replace: comma-separated missing types (or "None")
total_spec     = 0        # replace: total spec requirements (0 if no spec)
covered_count  = 0        # replace: requirements with Covered status (0 if no spec)
coverage_pct   = None     # replace: float (e.g. 85.0) or None if no spec provided
verdict_value  = "Needs rework"  # initial value — overwritten by auto-compute block near Save section

summary = [
    ("Total Test Cases Reviewed",         N),
    ("Total Issues Found \u2014 Blocker", blocker_count),
    ("Total Issues Found \u2014 Minor",   minor_count),
    ("Total Issues Found",                blocker_count + minor_count),
    ("Test Types Covered",                types_covered),
    ("Test Types Missing",                types_missing),
    ("Total Spec Requirements",           total_spec if total_spec else "N/A \u2014 No spec file provided"),
    ("Requirements Covered",              covered_count if total_spec else "N/A"),
    ("Coverage %",                        f"{coverage_pct:.1f}%" if isinstance(coverage_pct, float) else "N/A"),
    ("Verdict",                           verdict_value),
]

for r, (label, value) in enumerate(summary, start=1):
    ws1.cell(row=r, column=1, value=label).font = bold_font
    ws1.cell(row=r, column=2, value=value)

# Coverage % cell coloring (row 9)
cov_cell = ws1.cell(row=9, column=2)
if isinstance(coverage_pct, float):
    if coverage_pct >= 80:
        cov_cell.fill = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")
    elif coverage_pct >= 50:
        cov_cell.fill = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
    else:
        cov_cell.fill = PatternFill(start_color="FCE4D6", end_color="FCE4D6", fill_type="solid")
cov_cell.font = Font(name="Calibri", bold=True, size=10)
# Note: Verdict cell (row 10) value and styling are set by the auto-compute block near the Save section.

# Blank row 11; evaluation table header at row 12
# Evaluation table: FAILS ONLY — no pass rows
eval_headers = ["Check #", "TC ID", "Criterion", "Current Value",
                "Finding", "Suggested Fix", "Result Type"]
for c, h in enumerate(eval_headers, start=1):
    cell = ws1.cell(row=12, column=c, value=h)
    cell.font = hdr_font; cell.fill = hdr_fill; cell.alignment = hdr_align

# Tuple: (Check#, TC_ID, Criterion, CurrentValue, Finding, SuggestedFix, ResultType)
# Sort: B rows first (sorted by TC ID), then M rows (sorted by TC ID).
# ResultType must be exactly "Blocker" or "Minor" — NO pass rows.
evaluations = [
    # INSERT ALL BLOCKER AND MINOR TUPLES HERE — NO PASS ROWS
    # Example:
    # ("B1", "TC_001", "Expected Result", "works correctly",
    #  "Expected result uses vague language 'works correctly' — not testable.",
    #  "Replace with: 'System displays confirmation message: \"Project saved successfully.\" and project appears in the project list with status Active.'",
    #  "Blocker"),
    # ("M1", "TC_002", "Test Data", "valid credentials",
    #  "Test data uses vague descriptor 'valid credentials' — exact values required for automation.",
    #  "Replace with: Username: qa_user@example.com | Password: Test@1234",
    #  "Minor"),
    # Automation Readiness Blocker — TC over-promoted: marked Automatable but fails 2+ of the 6 conditions.
    # Use this pattern when a TC is marked Automatable but fails: Low-flaky (OTP/CAPTCHA/third-party),
    # Repeatable (non-deterministic), Stable (frequently changing), Clearly assertable (subjective result),
    # or Maintainable (fragile selectors / unreasonable effort).
    # ("B2", "TC_003", "Automation Readiness", "Automatable",
    #  "TC marked Automatable but fails 2 of 6 conditions: Low-flaky (depends on live OTP) and Clearly assertable (expected result requires visual judgment). Per the 6-condition rule, 2+ failures mandate Not Automatable.",
    #  "Change Automation Readiness to: Not Automatable. Stabilize OTP dependency via mock/stub before reconsidering.",
    #  "Blocker"),
]

for r, ev in enumerate(evaluations, start=13):
    rt = ev[6]
    fill   = blocker_fill if rt == "Blocker" else minor_fill
    lbside = bl_border    if rt == "Blocker" else mn_border
    for c, val in enumerate(ev, start=1):
        cell = ws1.cell(row=r, column=c, value=val)
        cell.fill = fill
        cell.alignment = Alignment(vertical="top", wrap_text=True)
        cell.font = Font(name="Calibri", size=10)
        cell.border = Border(
            left=lbside if c == 1 else thin,
            right=thin, top=thin, bottom=thin
        )

# ── Sheet 2: Fixed Test Cases ──────────────────────────────────────────────────
ws2 = wb.create_sheet(title="Fixed Test Cases")

headers = [
    "Test Case ID", "Module Name", "Feature Name", "Test Case Category",
    "Test Case Summary", "Pre-conditions", "Test Steps",
    "Test Data (if applicable)", "Expected Result", "Severity", "Automation Readiness"
]

for col_idx, header in enumerate(headers, start=1):
    cell = ws2.cell(row=1, column=col_idx, value=header)
    cell.font = hdr_font; cell.fill = hdr_fill
    cell.alignment = hdr_align; cell.border = thin_border
ws2.row_dimensions[1].height = 30

# Tuple: (TC_ID, Module, Feature, Category, Summary, PreConds, Steps, TestData, ExpResult, Severity, AutomationReadiness)
# Use \n inside string literals for multi-line cells (Pre-conditions, Test Steps).
# Automation Readiness values: Automatable | Partially Automatable | Not Automatable
# Evaluated against 6 conditions: Stable, Repeatable, High-value, Low-flaky, Clearly assertable, Maintainable.
# A TC failing 2 or more of these conditions MUST be classified Not Automatable.
# If the original TC was marked Automatable but 6-condition evaluation finds 2+ failures,
# add a Blocker row in evaluations (Criterion: "Automation Readiness") — Sheet 4 will
# automatically override Readiness to Manual-only via the ar_blocker4 check below.
test_cases = [
    # INSERT ALL FIXED TEST CASE TUPLES HERE
    # Example:
    # ("TC_PM_001", "Project Management", "Create Project",
    #  "Functional",
    #  "Verify a logged-in Manager can create a new project with all required fields.",
    #  "1. User is logged in as a Manager role.\n2. At least one client exists in the system.",
    #  "1. Navigate to Projects > New Project.\n2. Enter Project Name: Alpha Rollout.\n3. Select Client: Acme Corp.\n4. Set Start Date: 2026-06-01.\n5. Click Save.",
    #  "Project Name: Alpha Rollout | Client: Acme Corp | Start Date: 2026-06-01",
    #  "System saves the project and redirects to the Project Detail page. Project name 'Alpha Rollout' is displayed with status 'Active'.",
    #  "High",
    #  "Automatable"),
]

for row_idx, tc in enumerate(test_cases, start=2):
    color = sev_hex.get(tc[9], "000000")
    fill  = alt_fill if row_idx % 2 == 0 else no_fill
    for col_idx, value in enumerate(tc, start=1):
        cell = ws2.cell(row=row_idx, column=col_idx, value=value)
        cell.font = row_font; cell.alignment = data_alignment; cell.fill = fill
        cell.border = Border(
            left   = Side(style="medium" if col_idx == 1 else "thin",
                          color=color if col_idx == 1 else "000000"),
            right  = Side(style="thin"),
            top    = Side(style="thin"),
            bottom = Side(style="thin")
        )

col_widths = [15, 25, 22, 22, 55, 45, 65, 40, 65, 12, 24]
for i, w in enumerate(col_widths, start=1):
    ws2.column_dimensions[get_column_letter(i)].width = w

ws2.freeze_panes = "A2"
ws2.auto_filter.ref = f"A1:K{ws2.max_row}"

# ── Sheet 3: Spec Coverage Matrix ─────────────────────────────────────────────
# REQUIRED: Set SPEC_PROVIDED = True when spec/requirement files were provided.
# Set SPEC_PROVIDED = False when no spec files were provided — Sheet 3 is omitted
# and all spec-related summary rows (7–9) show "N/A".
SPEC_PROVIDED = True  # MUST be set to False when no spec file was provided

if SPEC_PROVIDED:
    ws3 = wb.create_sheet(title="Spec Coverage Matrix")

    spec_headers = [
        "Spec ID", "Source File", "Requirement / Scenario", "Business Risk",
        "Coverage Status", "Linked TC IDs", "Gap Notes", "Required Action"
    ]
    for col_idx, header in enumerate(spec_headers, start=1):
        cell = ws3.cell(row=1, column=col_idx, value=header)
        cell.font = hdr_font; cell.fill = hdr_fill
        cell.alignment = hdr_align; cell.border = thin_border
    ws3.row_dimensions[1].height = 30

    partial_fill3 = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
    notcov_fill3  = PatternFill(start_color="FCE4D6", end_color="FCE4D6", fill_type="solid")

    # Tuple: (SpecID, SourceFile, RequirementText, BusinessRisk, CoverageStatus, LinkedTCIDs, GapNotes, RequiredAction)
    # CoverageStatus values: Covered | Partially Covered | Not Covered
    # BusinessRisk values: High | Medium | Low
    # RequiredAction values: No action | Expand TCs | Add TCs
    spec_coverage = [
        # INSERT ALL SPEC COVERAGE TUPLES HERE
        # Example:
        # ("SR-001", "login_spec.md", "User can log in with valid email and password.",
        #  "High", "Covered", "TC_AUTH_001", "N/A", "No action"),
        # ("SR-002", "login_spec.md", "System locks account after 5 failed login attempts.",
        #  "High", "Not Covered", "\u2014",
        #  "No TC tests account lockout after repeated failures.",
        #  "Add TCs"),
    ]

    spec_col_widths = [12, 30, 60, 15, 22, 35, 60, 18]
    for i, w in enumerate(spec_col_widths, start=1):
        ws3.column_dimensions[get_column_letter(i)].width = w

    for row_idx, sr in enumerate(spec_coverage, start=2):
        status = sr[4]
        if status == "Covered":
            row_fill = covered_fill; lborder = cov_border
        elif status == "Partially Covered":
            row_fill = partial_fill3; lborder = part_border
        else:
            row_fill = notcov_fill3; lborder = nocov_border
        for col_idx, value in enumerate(sr, start=1):
            cell = ws3.cell(row=row_idx, column=col_idx, value=value)
            cell.font = row_font; cell.alignment = data_alignment; cell.fill = row_fill
            cell.border = Border(
                left=lborder if col_idx == 1 else thin,
                right=thin, top=thin, bottom=thin
            )

    ws3.freeze_panes = "A2"
    ws3.auto_filter.ref = f"A1:H{ws3.max_row}"

# ── Sheet 4: TC Review Status ──────────────────────────────────────────────────
# Always generated — one row per TC.
ws4 = wb.create_sheet(title="TC Review Status")

tc_status_headers = [
    "TC ID", "Review Status", "Readiness",
    "Execution Ready", "Client Deliverable", "Production Ready",
    "Reviewer Comments", "Required Corrections", "Defects"
]
for col_idx, header in enumerate(tc_status_headers, start=1):
    cell = ws4.cell(row=1, column=col_idx, value=header)
    cell.font = hdr_font; cell.fill = hdr_fill
    cell.alignment = hdr_align; cell.border = thin_border
ws4.row_dimensions[1].height = 30

# Build per-TC issue index from evaluations list
# ev tuple: (Check#, TC_ID, Criterion, CurrentValue, Finding, SuggestedFix, ResultType)
tc_issues = defaultdict(lambda: {"blockers": [], "minors": [], "corrections": []})

for ev in evaluations:
    tc_id_ev = ev[1]; criterion_ev = ev[2]; finding_ev = ev[4]
    fix_ev = ev[5]; rt_ev = ev[6]
    if rt_ev == "Blocker":
        tc_issues[tc_id_ev]["blockers"].append(f"{criterion_ev}: {finding_ev}")
    else:
        tc_issues[tc_id_ev]["minors"].append(f"{criterion_ev}: {finding_ev}")
    tc_issues[tc_id_ev]["corrections"].append(f"{criterion_ev}: {fix_ev}")

# Criteria that trigger quality gate failures
EXEC_CRITERIA   = {"Test Steps", "Pre-conditions", "Test Data"}
CLIENT_CRITERIA = {"Expected Result", "Severity", "Test Case Summary"}

# Readiness tier mapping — base values (may be overridden by 6-condition gate below)
# Automatable     → Automation-ready  (only when TC passes all 6 conditions)
# Partially Auto  → Partially Automatable  (TC passes 4 or 5 of 6 conditions)
# Not Automatable → Manual-only  (TC fails 2 or more of 6 conditions)
# Override rule: if TC is marked Automatable but has a Blocker on "Automation Readiness"
# criterion in evaluations (i.e. it failed 2+ conditions), output Manual-only instead.
ar_map = {"Automatable": "Automation-ready", "Not Automatable": "Manual-only",
          "Partially Automatable": "Partially Automatable"}

for row_idx4, tc4 in enumerate(test_cases, start=2):
    tc_id4  = tc4[0]
    ar_val4 = tc4[10]
    issues4 = tc_issues[tc_id4]
    has_b4  = len(issues4["blockers"]) > 0
    has_m4  = len(issues4["minors"]) > 0

    # Review Status
    if has_b4:
        review_status4 = "Rejected"
    elif has_m4:
        review_status4 = "Needs Fix"
    else:
        review_status4 = "Approved"

    # Readiness — apply 6-condition override rule
    # If TC is marked Automatable but has a Blocker on "Automation Readiness" criterion,
    # it failed 2+ of the 6 conditions → force Manual-only regardless of column value.
    ar_blocker4 = any("Automation Readiness" in b for b in issues4["blockers"])
    if ar_val4 == "Automatable" and ar_blocker4:
        readiness4 = "Manual-only"
    else:
        readiness4 = ar_map.get(ar_val4, "Partially Automatable")

    # Execution Ready — issues on Test Steps, Pre-conditions, Test Data
    all4 = issues4["blockers"] + issues4["minors"]
    exec_fail4  = any(any(c in i for c in EXEC_CRITERIA) for i in all4)
    exec_ready4 = "No" if exec_fail4 else "Yes"

    # Client Deliverable — issues on Expected Result, Severity, Test Case Summary, or any Blocker
    client_fail4 = has_b4 or any(any(c in i for c in CLIENT_CRITERIA) for i in all4)
    client4      = "No" if client_fail4 else "Yes"

    # Production Ready — all gates pass + no blockers
    prod4 = "Yes" if (exec_ready4 == "Yes" and client4 == "Yes" and not has_b4) else "No"

    # Reviewer Comments
    comments4 = "; ".join(issues4["blockers"] + issues4["minors"]) if (has_b4 or has_m4) else "No issues found"

    # Required Corrections
    corrections4 = "; ".join(issues4["corrections"]) if issues4["corrections"] else "None"

    # Defects — Blocker issues are quality defects in the TC
    defects4 = "; ".join(issues4["blockers"]) if has_b4 else "None"

    row4 = (tc_id4, review_status4, readiness4, exec_ready4, client4, prod4,
            comments4, corrections4, defects4)

    if review_status4 == "Rejected":
        fill4 = rej_fill4; lbside4 = rej_side4
    elif review_status4 == "Needs Fix":
        fill4 = fix_fill4; lbside4 = fix_side4
    else:
        fill4 = appr_fill4; lbside4 = appr_side4

    for col_idx4, val4 in enumerate(row4, start=1):
        cell4 = ws4.cell(row=row_idx4, column=col_idx4, value=val4)
        cell4.font = row_font; cell4.alignment = data_alignment; cell4.fill = fill4
        cell4.border = Border(
            left=lbside4 if col_idx4 == 1 else thin,
            right=thin, top=thin, bottom=thin
        )

tc4_col_widths = [15, 18, 22, 18, 20, 20, 60, 60, 55]
for i4, w4 in enumerate(tc4_col_widths, start=1):
    ws4.column_dimensions[get_column_letter(i4)].width = w4

ws4.freeze_panes = "A2"
ws4.auto_filter.ref = f"A1:I{ws4.max_row}"

# ── Auto-compute Overall Verdict ───────────────────────────────────────────────
# Runs after evaluations list is fully populated.
# Verdict is suite-level — distinct from per-TC Review Status.
# types_missing must be a string (e.g. "System, NFR") for the _miss_crit check.
_CRITICAL_TYPES = {"Functional", "Negative", "E2E (End-to-End)"}
_tc_with_b      = len(set(ev[1] for ev in evaluations if ev[6] == "Blocker"))
_b_ratio        = _tc_with_b / N if N > 0 else 0
_miss_crit      = [t for t in _CRITICAL_TYPES if t in types_missing]
_spec_ok        = coverage_pct is None or coverage_pct >= 80

if blocker_count == 0 and not _miss_crit and _spec_ok:
    verdict_value = "Approved"
elif _b_ratio < 0.20 and not _miss_crit and (coverage_pct is None or coverage_pct >= 50):
    verdict_value = "Approved with changes"
else:
    verdict_value = "Needs rework"

# Update Sheet 1 verdict cell (row 10, col 2) with computed value and color
_vc = ws1.cell(row=10, column=2)
_vc.value = verdict_value
if "Needs rework" in verdict_value:
    _vc.fill = PatternFill(start_color="FCE4D6", end_color="FCE4D6", fill_type="solid")
elif "Approved with changes" in verdict_value:
    _vc.fill = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
else:
    _vc.fill = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")
_vc.font = Font(name="Calibri", bold=True, size=10)

# ── Save ───────────────────────────────────────────────────────────────────────
module_code = "PM"   # replace with actual module code (e.g. "AUTH", "PROJ", "BILL")
timestamp   = datetime.now().strftime("%Y%m%d_%H%M%S")
out_dir     = os.path.join(os.getcwd(), "Testcases")
os.makedirs(out_dir, exist_ok=True)
filename    = os.path.join(out_dir, f"ReviewAndFixed_{module_code}_{timestamp}.xlsx")
wb.save(filename)
print(f"Excel file saved: {filename}")
```

---

## Variable Reference

| Variable | Type | Description |
|---|---|---|
| `N` | int | Total test cases reviewed |
| `blocker_count` | int | Count of Blocker failure rows in `evaluations` |
| `minor_count` | int | Count of Minor failure rows in `evaluations` |
| `types_covered` | str | Comma-separated test types present (e.g. `"Functional, Negative, Smoke"`) |
| `types_missing` | str | Comma-separated missing test types, or `"None"` |
| `total_spec` | int | Count of spec requirements; `0` if no spec provided |
| `covered_count` | int | Count of requirements with Covered status; `0` if no spec |
| `coverage_pct` | float or None | Coverage percentage (e.g. `85.0`); `None` if no spec |
| `SPEC_PROVIDED` | bool | `True` if spec files were provided; `False` otherwise — controls Sheet 3 generation |
| `module_code` | str | Short module code for the filename (e.g. `"AUTH"`, `"PROJ"`) |

---

## Automation Readiness Override Logic

The generated script enforces the 6-condition gate at runtime. The override operates as follows:

| Step | What happens |
|---|---|
| 1 — Review (Step 12) | Evaluate each TC against all 6 conditions: Stable, Repeatable, High-value, Low-flaky, Clearly assertable, Maintainable. |
| 2 — Flag Blocker | If TC is marked `Automatable` and fails 2 or more conditions, add a Blocker row to `evaluations` with `Criterion = "Automation Readiness"`. Describe which specific conditions failed and why. |
| 3 — Fix in Sheet 2 | In the `test_cases` tuple, correct `AutomationReadiness` to `"Not Automatable"` for that TC. |
| 4 — Override in Sheet 4 | `ar_blocker4` detects the Blocker on "Automation Readiness". If `ar_val4 == "Automatable"` and `ar_blocker4 is True`, `readiness4` is forced to `"Manual-only"` regardless of the tuple value. |
| 5 — Gates cascade | The Blocker sets: `Client Deliverable = No`, `Production Ready = No`, `Review Status = Rejected`. |

**Conditions that commonly force `Not Automatable`:**
- OTP, CAPTCHA, live payment, or real third-party API with no stable mock → fails **Low-flaky**
- Non-deterministic outcome across repeated runs → fails **Repeatable**
- Feature under active development → fails **Stable**
- Expected result requires human visual or subjective judgment → fails **Clearly assertable**
- Fragile selector-heavy flow or disproportionate maintenance cost → fails **Maintainable**
- Low business impact, rarely executed → fails **High-value**

**Important:** Do not add `ar_blocker4` workarounds (retries, waits, conditional logic) to make a flaky TC pass. Fix the underlying dependency or keep it manual.

---

## Tuple Formats

**`evaluations` tuple** (7 positions):
```
(Check#, TC_ID, Criterion, CurrentValue, Finding, SuggestedFix, ResultType)
```
- `Check#`: `"B1"`, `"B2"`, … for Blockers; `"M1"`, `"M2"`, … for Minors
- `ResultType`: exactly `"Blocker"` or `"Minor"` — never `"Pass"`

**`test_cases` tuple** (11 positions):
```
(TC_ID, Module, Feature, Category, Summary, PreConds, Steps, TestData, ExpResult, Severity, AutomationReadiness)
```
- `AutomationReadiness`: `"Automatable"` | `"Partially Automatable"` | `"Not Automatable"` — must reflect the 6-condition gate result. A TC failing 2+ conditions must be `"Not Automatable"` here (fixed value in Sheet 2). The Sheet 4 override (`ar_blocker4`) additionally enforces `Manual-only` in the Readiness column when an Automation Readiness Blocker exists.
- Use `\n` inside string literals for multi-line Pre-conditions and Test Steps

**`spec_coverage` tuple** (8 positions):
```
(SpecID, SourceFile, RequirementText, BusinessRisk, CoverageStatus, LinkedTCIDs, GapNotes, RequiredAction)
```
- `CoverageStatus`: `"Covered"` | `"Partially Covered"` | `"Not Covered"`
- `BusinessRisk`: `"High"` | `"Medium"` | `"Low"`
- `RequiredAction`: `"No action"` | `"Expand TCs"` | `"Add TCs"`

---

## Execution

```
py "C:/Users/Rachayya/CPN_Path/gen_tc_review.py"
```

After execution, output exactly one line:

```
Excel file saved: ReviewAndFixed_<ModuleCode>_<YYYYMMDD_HHMMSS>.xlsx
```
