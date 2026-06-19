# Category Mapping — Generator → Reviewer Schema

This skill's output is designed to compose with **test-case-reviewer**. The reviewer
audits coverage against a controlled vocabulary and assigns automation readiness.
The controlled vocabulary (the 8 categories, severity, automation readiness, ID and
format rules) lives in `test-case-reviewer/references/taxonomy.md` — that file is the
source of truth. This file only records how the generator's output maps onto it.

Run **test-case-reviewer** after generation to audit coverage, validate the controlled
schema, and assign `Automation Readiness` and `Feature Name`.

---

## Category Mapping (12 generator Types → 8 controlled Categories)

The generator emits one of 12 `Type` values per test case. The reviewer uses 8
controlled `Test Case Category` values (Functional, Validation, Error handling, UI/UX,
State / workflow, NFR, Integration, Regression / Smoke). Every generator type maps —
none are unmapped.

| Generator `Type` | Reviewer `Test Case Category` | Resolution rule |
|---|---|---|
| Positive | Functional | Happy path, valid inputs, expected business flow. |
| Negative | Validation **or** Error handling | Validation when invalid user input is rejected; Error handling when a system/service failure is exercised. |
| Boundary | Validation | Boundary violations are input validation. |
| Edge | Validation **or** State / workflow | Validation by default; State / workflow for state-transition edges (session timeout, token expiry, concurrent updates, mid-transaction interruption). |
| Validation | Validation | Direct mapping. |
| UI-UX | UI/UX | Direct mapping. |
| API | Integration | Cross-system data flow, third-party APIs, API-to-UI sync. |
| Database | Integration | DB persistence and cross-system data flow. |
| Security | NFR | Security non-functional requirements (per taxonomy NFR row). |
| Error Handling | Error handling | Direct mapping. |
| Regression | Regression / Smoke | Direct mapping. |
| Exploratory | Validation \| Error handling \| State / workflow | Resolve by what the exploratory scenario discovers (invalid input → Validation; failure → Error handling; broken state transition → State / workflow). |

---

## Column Mapping (10 generator columns → 11 reviewer columns)

The generator's table (see `SKILL.md` Step 4) maps onto the reviewer's 11-column schema
(see `test-case-reviewer/references/sheet-specifications.md`).

| Generator column | Reviewer column | Note |
|---|---|---|
| TC ID | Test Case ID | Sequential, unique; reviewer continues the existing ID pattern. |
| Module | Module Name | Direct mapping. |
| Type | Test Case Category | Translated via the Category Mapping table above. |
| Scenario | Test Case Summary | Direct mapping. |
| Preconditions | Pre-conditions | Direct mapping. |
| Test Data | Test Data (if applicable) | Direct mapping. |
| Test Steps | Test Steps | Direct mapping. |
| Expected Result | Expected Result | Direct mapping. |
| Severity | Severity | Same controlled values (Critical/High/Medium/Low). |
| Priority | — | Generator-only. The reviewer schema has no Priority column. |
| — | Feature Name | Assigned by the reviewer (flow-first naming) — not produced at generation time. |
| — | Automation Readiness | Assigned by the reviewer via the 6-condition gate — not produced at generation time. |
