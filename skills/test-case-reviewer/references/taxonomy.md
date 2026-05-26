# Taxonomy Reference

Controlled values for Severity, Test Case Category, Taxonomy Rules, Test Case ID Rules, and Format Rules.

---

## Controlled Categories

Use only these eight Test Case Category values. Do not invent new categories or use feature names as category values.

| # | Category | When to use |
|---|---|---|
| 1 | Functional | Happy path — core feature behavior when all inputs and preconditions are valid |
| 2 | Validation | Invalid input, missing required fields, boundary violations, business-rule rejection |
| 3 | Error handling | System errors, service failures, permission denied, timeout, graceful fallback |
| 4 | UI/UX | Layout, visibility, labels, empty states, navigation, usability, accessibility |
| 5 | State / workflow | State transitions, multi-step progression, data persistence, rollback |
| 6 | NFR | Performance, reliability, scalability, concurrency, security non-functional requirements |
| 7 | Integration | Cross-system data flow, third-party APIs, API-to-UI sync, event-driven flows |
| 8 | Regression / Smoke | Smoke check, sanity check, regression guard for existing behavior |

**Informal label → controlled category mapping:**

| Informal label | Maps to |
|---|---|
| Functionality / Positive / Happy Path | Functional |
| Negative / Failure | Validation (user input rejected) or Error handling (system/service failure) |
| Data Validation / Boundary / Edge | Validation |
| UI / Navigation / Display | UI/UX |
| State Transition / Data Persistence | State / workflow |
| Performance / Reliability / Security NFR | NFR |
| API / Cross-system / Third-party | Integration |
| Sanity / Smoke / Regression | Regression / Smoke |

---

## Taxonomy Rules

| Field | Definition | Rule |
|---|---|---|
| Module Name | Broad product area, domain, or system. | Stable top-level grouping teams can filter on. Never empty. Examples: Project Management, Billing, Authentication, Notifications. |
| Feature Name | The user flow, story, or workstream being tested within the module. | Flow-first naming (verb + object): "Create Project", "Revert Stage to Prospect", "Submit Proposal". Never use a component name, sub-feature name, or UI element name. |
| Test Case Category | Type of test — what the TC proves. | From the Controlled Categories list only. Never use a feature name, component name, or capability as a category. |

**Correct example:**
```
Module Name:          Project Management
Feature Name:         Revert Stage to Prospect
Test Case Category:   Functional
Test Case Summary:    Verify a user can revert a Proposal Submitted project back to Prospect stage.
```

**Incorrect example (flag as Blocker):**
```
Module Name:          Project Management
Feature Name:         Stage Selector            ← component name, not a user flow
Test Case Category:   Revert Stage              ← feature name used as category
```

Capability detail belongs in Test Case Summary, Test Steps, Test Data, or Expected Result — not in Feature Name or Category.

---

## Severity

Use only these values:

| Value | Use when |
|---|---|
| Critical | System crash, data loss, security failure, core workflow completely blocked, or wrong output affecting users. |
| High | Major feature broken, key flow unavailable, significant regression, or incorrect important data. |
| Medium | Non-blocking issue, minor workflow degradation, or limited-impact edge case. |
| Low | Cosmetic issue, minor UI alignment issue, or low-risk usability issue. |

Flag over-assigned Critical and under-assigned severity.

---

## Automation Readiness

Use only these three values. Assign using the 6-condition evaluation below — do not assign `Automatable` by default or to inflate coverage counts.

| Value | Condition score | When to use |
|---|---|---|
| `Automatable` | Passes all 6 conditions | Steps are deterministic and repeatable; expected result is machine-verifiable; inputs and outputs are fully specified; no OTP, CAPTCHA, physical device, or real-payment dependency; stable entry point exists. |
| `Partially Automatable` | Passes 4 or 5 of 6 conditions | Most steps are automatable but at least one requires manual execution, an undefined mock/stub strategy, or non-deterministic timing. |
| `Not Automatable` | Fails 2 or more conditions | Expected result requires subjective human judgment; depends on OTP, CAPTCHA, live third-party, or real payment that cannot be stubbed; or automation cost outweighs value. |

### 6-Condition Evaluation

Evaluate each TC against all six conditions before assigning a tier:

| # | Condition | Fails when |
|---|---|---|
| 1 | **Stable** | The feature or UI/API contract is actively changing or under frequent revision. |
| 2 | **Repeatable** | The TC produces different outcomes on repeated runs due to data state, timing, or environment variance. |
| 3 | **High-value** | The TC covers cosmetic, rarely used, or low-business-impact behavior — automation adds little reliability gain. |
| 4 | **Low-flaky** | The TC depends on OTP, CAPTCHA, live third-party APIs, real payment gateways, unstable mocks, or hardcoded waits. |
| 5 | **Clearly assertable** | The expected result requires human visual judgment, subjective interpretation, or cannot be verified programmatically. |
| 6 | **Maintainable** | The TC requires fragile selectors, complex state setup, or automation effort that outweighs the long-term value. |

**Decision rule:** A TC failing **2 or more** conditions must be classified `Not Automatable`.

### Misclassification flags

| Finding | Failure type |
|---|---|
| TC marked `Automatable` but fails 2 or more of the 6 conditions (over-promotion) | Blocker |
| TC assigned wrong tier but not being over-promoted (e.g. `Automatable` when should be `Partially Automatable`) | Minor |

### Automation is selective — not coverage-driven

It is NOT mandatory that all TCs be automated. A smaller stable automation suite is far more valuable than a large unstable suite nobody trusts. Never inflate `Automatable` counts. Accuracy of classification is more important than count.

---

## Test Case ID Rules

Follow the user's existing test case ID pattern when provided. Continue from the last provided ID — do not restart numbering. Do not create duplicate IDs.

When no prior ID pattern exists, use: `TC_[MODULE_CODE]_001`

Increment sequentially: `TC_[MODULE_CODE]_002`, `TC_[MODULE_CODE]_003`, and so on.

**Continuation example:** If the user provides TCs with IDs TC_AUTH_001 to TC_AUTH_045, the next new TC must be TC_AUTH_046, not TC_AUTH_001.

---

## Format Rules

- No literal `\n` or `\\n` visible in cells. Use actual line breaks (use `\n` inside Python string literals only).
- No HTML tags in any cell value.
- Test steps: numbered, one step per line, logical order, no missing user actions or system responses.
- All 11 fields present per row. Use `N/A` — never leave blank.
- Test Case IDs: sequential, unique, no duplicates.
- Do not combine multiple behaviors in one test case.
- Do not split one test case into multiple rows.
- Automation Readiness must be one of the three controlled values: `Automatable`, `Partially Automatable`, `Not Automatable`. Assigned using the 6-condition gate — never assigned by default. A TC failing 2 or more conditions is always `Not Automatable`.
