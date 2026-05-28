---
name: test-case-generator
description: Generate exhaustive, production-ready QA test cases from user stories, acceptance criteria, BRDs, PRDs, or feature descriptions — covering all test types with zero critical gaps.
version: 1.0.0
author: Ajay R
email: ajay.r@zysk.tech
category: qa-testing
tags:
  - test-case-generation
  - qa-coverage
  - manual-testing
  - api-testing
  - security-testing
product: zysk
sprint: 1
tested_with: claude-sonnet-4-6
---

# Enterprise QA Test Case Generator

> Generate exhaustive, production-ready QA test cases from any feature input — covering all test types, risk scenarios, and edge cases with zero critical gaps.

## When to use

- Activate when: the user asks to "generate test cases", "write QA coverage", or "build test coverage"
- Activate when: the user provides a user story, acceptance criteria, BRD, PRD, or feature description and wants test cases
- Activate when: the user says "create test cases for X", "give me QA scenarios for X", or "what should I test for X"
- Activate when: the user needs test coverage for login, authentication, payments, integrations, or any enterprise feature
- Do NOT activate when: the user only wants to *review* existing test cases (use test-case-reviewer instead)
- Do NOT activate when: the user is asking general QA methodology questions without a feature to test

## Prerequisites

- [ ] Feature description, user story, acceptance criteria, BRD, or PRD is available
- [ ] Module/feature name is known
- [ ] Any API contracts, UI flows, or integration details are shared (optional but improves coverage)

## Steps

Execute all steps in order. Do not skip categories. Do not generate shallow or generic test cases.

### Step 0: Input Completeness Check

Before doing anything else, assess whether the input has enough detail to generate meaningful test cases.

**If the input is vague** (e.g., "test the delete feature", "generate test cases for login" with no further detail), **stop and ask:**

> "To generate complete test cases, I need a bit more detail:
> 1. What are the acceptance criteria or expected behaviours?
> 2. Are there any specific edge cases or constraints I should know about?
> 3. Are there APIs, roles, or integrations involved?"

Do not proceed to Step 1 until the user has provided sufficient detail. A feature description with at least 3 acceptance criteria points or a clear flow description is the minimum needed for meaningful coverage.

### Step 1: Analyse the Input

Read the provided feature description, user story, or acceptance criteria. Identify:
- The module/feature being tested
- All acceptance criteria points
- APIs involved (if any)
- User roles and permissions
- Integration touchpoints
- Security-sensitive areas (login, payments, user data, file upload)

### Step 2: Generate Test Cases Across All 12 Categories

For EVERY applicable category below, generate dedicated test cases. Never combine multiple validations into one test case.

**1. Positive Test Cases** `[Mandatory]` — happy path flows, valid inputs, successful transactions, standard user behaviour, expected business flow.

**2. Negative Test Cases** `[Mandatory]` — invalid inputs, empty mandatory fields, incorrect formats, unauthorized actions, invalid states, duplicate submissions, broken workflows, invalid transitions.

**3. Boundary Value Analysis** `[Mandatory when numeric/character/date limits exist]` — generate a dedicated test case for EACH: minimum value, minimum+1, maximum-1, maximum value, just outside limits, character limits, file size limits, numeric ranges, date ranges. Each boundary gets its own test case. Skip only if the feature has no input limits of any kind.

**4. Edge Cases** `[Mandatory]` — double-click actions, browser refresh during save, back button behaviour, concurrent updates, session timeout, token expiry, multiple tabs, repeated API retries, partial failures, slow network/interruption, mid-transaction interruption, expired links, race conditions, simultaneous users.

**5. Validation Testing** `[Mandatory when user input fields exist]` — field validations, mandatory checks, data formats, business rule enforcement, input sanitization, cross-field dependencies, dropdown validation, conditional fields, dynamic validations. Verify: correct validation message, trigger timing, and removal after correction. Skip only for features with no user-facing input.

**6. UI/UX Testing** `[Mandatory when a UI is involved; skip for API-only features]` — button enabled/disabled states, loader visibility, empty states, alignment, truncation, responsive layout, accessibility, tooltip behaviour, error message visibility, confirmation popups, keyboard navigation, tab order, focus handling.

**7. API Testing** `[When applicable — only when APIs are involved]`:
- Request: headers, authorization, payload structure, mandatory fields, invalid payloads, null handling
- Response: status codes, response schema, data correctness, error responses, field types, response time
- Reliability: retry behaviour, idempotency, duplicate requests, timeout handling, rate limiting, token expiration
- Integration: DB persistence, third-party sync, event generation, queue handling, webhook validation

**8. Database Validation** `[When applicable — only when the feature reads from or writes to a database]` — correct DB insertion, update accuracy, duplicate prevention, data consistency, soft delete behaviour, audit logging, timestamp validation, rollback behaviour.

**9. Security Testing** `[When applicable — ALWAYS include when the feature involves login, authentication, authorization, tokens, user data, file upload, payments, or sensitive information]`:
- SQL injection, XSS, token reuse, auth bypass, role bypass, forced browsing, session hijacking, privilege escalation, rate limiting, direct API access, sensitive data exposure.

**10. Error Handling** `[Mandatory]` — API failures, server errors, timeout handling, retry mechanism, graceful failure, user-friendly messaging, logging behaviour, partial system failures.

**11. Regression Impact Analysis** `[When applicable — only when related existing modules or shared components exist]` — identify related modules that may break. Generate regression test cases for existing flows, shared components, dependent services, common workflows, notifications, reporting, permissions, integrations.

**12. Exploratory Testing Ideas** `[Mandatory]` — unexpected user actions, random navigation, rapid clicking, invalid sequence flows, cross-browser oddities, real production misuse patterns.

### Step 3: Apply Risk-Based Prioritization

Prioritize test cases in this order:
1. Revenue-impacting flows
2. Authentication flows
3. Data-loss scenarios
4. Integration failures
5. High-frequency user journeys
6. Compliance/security risks

Assign Critical severity + P1 priority to production-blocking failures.

### Step 4: Output the Test Cases as a Structured Table

Generate ALL test cases in this exact column format:

| TC ID | Module | Type | Severity | Priority | Scenario | Preconditions | Test Data | Test Steps | Expected Result |

**Column rules:**

- **TC ID** — sequential: TC-001, TC-002, TC-003, …
- **Module** — feature/module name (Login, Payment, Deal Creation, API Sync, etc.)
- **Type** — one of: Positive, Negative, Boundary, Edge, Validation, UI-UX, API, Database, Security, Error Handling, Regression, Exploratory
- **Severity** — one of: Critical, High, Medium, Low (production/business impact)
- **Priority** — one of: P1, P2, P3 (testing urgency)
- **Scenario** — specific description of exactly what is validated; never generic (bad: "Verify login"; good: "Verify user can log in successfully with valid email and password")
- **Preconditions** — required setup, user role, existing data, environment state; use "N/A" if none
- **Test Data** — realistic values (email IDs, passwords, file sizes, dates, JSON payloads, API tokens, numeric values); never vague placeholders
- **Test Steps** — numbered steps, one action per step, each beginning with a verb (Navigate, Enter, Click, Submit, Verify, Refresh, Reopen)
- **Expected Result** — specific, verifiable, measurable; mention exact validation message, UI/API/DB behaviour, state changes; never use "works correctly" or "behaves as expected"

### Step 5: Internal Quality Validation

Before finalizing output, verify:
- Every acceptance criteria point has test coverage
- No duplicate test cases
- No vague expected results
- Every boundary has its own dedicated test case
- Security coverage exists where applicable
- Regression impact is considered
- API validation included where applicable
- Error handling covered
- Edge cases included
- Exploratory scenarios included
- Real-world misuse behaviour considered

### Step 6: Generate Excel Output

Write a Python script using the Write tool and execute it using the Bash tool to produce a `.xlsx` file.

Excel requirements:
- Bold headers
- Wrapped text
- Auto-fit columns
- Freeze top row
- One test case per row
- Sequential TC IDs
- All 10 columns preserved

File naming format: `Test_Cases_<Sanitized_Feature_Name>.xlsx` (spaces → underscores, special characters removed).

The script must create the output directory before saving. Include this at the top of the script:

```python
import os
os.makedirs('Testcases', exist_ok=True)
```

Save the script as `gen_test_cases.py` in the current working directory and execute it from the same directory:

```bash
python3 gen_test_cases.py
```

## Output

- **Format:** Structured Markdown table in chat + Excel file (`.xlsx`)
- **Location:** Excel saved to `Testcases/` subfolder of `os.getcwd()`
- **File name:** `Test_Cases_<Feature_Name>.xlsx`
- **Example:** `Test_Cases_User_Login.xlsx`

## Example

**User says:** "Generate test cases for the user login feature — valid credentials, invalid password, account lockout after 5 attempts."

**Claude does:** Analyses the acceptance criteria, then generates test cases across all 12 categories — positive happy path, negative invalid credentials, boundary 5-attempt lockout, security SQL injection and brute-force scenarios, UI error message display, API response validation, session handling edge cases, and regression impact on password reset flow.

**Result:** A complete test case table with 30–60 test cases covering all risk areas, plus an Excel file `Test_Cases_User_Login.xlsx` ready for import into Jira, TestRail, or Azure DevOps.

## Notes

- Always think: what would break in production? what would users misuse? what would attackers exploit? what would fail under load?
- Each boundary value gets its own test case — never bundle min/max into one row.
- Security test cases are mandatory when the feature involves auth, tokens, payments, or user data.
- Generated test cases are immediately usable in Jira, Excel, TestRail, and Azure DevOps.
- Use `python3` as the Python executable — works on macOS, Linux, and Windows.
- openpyxl 3.1.5 is pre-installed — never add install checks or pip commands.
