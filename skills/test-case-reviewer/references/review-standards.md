# Review Standards

Detailed criteria definitions for Steps 4–11 of the Review Sequence.

---

## Requirement Coverage

Every requirement or acceptance criterion maps to at least one test case. Important requirements need more than one test case: happy path, failure path, edge case, and permission-related scenario.

Checklist:
- Every requirement has at least one test.
- Critical requirements have positive, negative, boundary, and permission scenarios.
- Test cases are mapped to AC IDs, user story IDs, endpoint IDs, or flow IDs.
- No test validates behavior that is not specified or intentionally accepted.

Reject or flag:
- Test cases without requirement mapping
- Requirements without test coverage
- Tests that validate undefined behavior
- Generic tests that do not prove the acceptance criterion

---

## Spec Traceability (applies when spec file is provided)

Each TC must trace to at least one spec requirement. Each spec requirement must be covered by at least one TC.

Flag as Blocker:
- Spec requirement with Not Covered status
- TC that cannot be traced to any spec requirement (Orphan TC)

Flag as Minor:
- Spec requirement with only Partial Coverage (happy path only, negatives missing)

---

## Test Type Coverage

The suite must include all applicable test types:

- **Blocker** if missing: Functional, Negative, E2E (for non-trivial features)
- **Minor** if missing: Smoke, Sanity, Integration, System, Boundary/Edge, Security, UI/UX, State/Workflow, NFR

Flag test types that are present but thin (only 1 TC where 3+ are warranted for high-risk areas).

---

## Risk-Based Prioritization

Classify each spec requirement by business risk:
- **High risk** — core workflows, financial transactions, auth, data integrity, user-facing errors. Must have Functional + Validation + Error Handling + State/Workflow TCs. Flag if fewer than 3 TCs covering different categories.
- **Medium risk** — secondary features, optional flows, configuration. Must have Functional + Validation TCs.
- **Low risk** — cosmetic, admin-only, rarely used flows. Functional TC minimum.

---

## Negative Coverage Ratio

For each module or feature, the count of Validation + Error Handling TCs must be ≥ count of Functional TCs. If not, flag the gap and list the specific missing negative scenarios by requirement.

---

## Duplicate Intent Detection

Two TCs have duplicate intent when they test the same behavior with only surface-level variation (different input values, different phrasing). Consolidate into one parameterized TC with a test data table. Do not preserve duplicates.

---

## Precondition Dependency Chain

A TC must be executable independently without relying on data or state created by a previous TC. Flag any TC where the precondition says "TC_XXX must have been executed" or implies a required execution order.

---

## Test Data Completeness

Every TC marked `Automatable` must have fully specified test data — exact values, not descriptions. Flag any data cell containing "valid", "any", "some", "appropriate", or other vague descriptors.

A TC with vague or unresolved test data fails the **Clearly assertable** condition of the 6-condition automation gate. If test data cannot be fully specified (e.g., because it depends on live data, OTP, or environment state), this also contributes toward failing the **Repeatable** or **Low-flaky** conditions. Two or more such failures mandate a `Not Automatable` classification.

---

## E2E Flow Coverage

For each major workflow (e.g., Create Order → Pay → Confirm → Deliver), at least one TC must trace the full user journey from start to final observable state. Flag workflows with no E2E coverage.

---

## Test Case Structure

Every test case output must contain exactly these 11 columns in this exact order:

1. Test Case ID
2. Module Name
3. Feature Name
4. Test Case Category
5. Test Case Summary
6. Pre-conditions
7. Test Steps
8. Test Data (if applicable)
9. Expected Result
10. Severity
11. Automation Readiness

Do not add, remove, rename, reorder, abbreviate, or modify any column name.

---

## Clarity and Executability

A tester must be able to execute the case without asking follow-up questions.

Flag:
- Vague titles such as "Verify login works"
- Steps that combine multiple actions
- Missing input values
- Missing user role or auth state
- Unclear environment assumptions
- Expected results like "works correctly", "successfully", or "proper behavior"

Replace vague language with measurable outcomes.

---

## Atomicity

One test case validates one main objective.

Flag:
- Mega test cases covering many unrelated outcomes
- Tests mixing positive and negative scenarios
- Tests depending on previous test execution order

---

## Determinism and Repeatability

Tests must produce the same result across repeated runs.

Flag:
- Random data without controlled generation
- External service dependency without mock/stub strategy
- Time-sensitive tests without time control
- Shared mutable data
- Hardcoded waits in automation candidates
- OTP, CAPTCHA, or live third-party dependency with no stable mock — these fail the **Low-flaky** condition
- Non-deterministic outcomes across runs — these fail the **Repeatable** condition

When a TC fails both **Low-flaky** and **Repeatable** (2 of the 6 automation conditions), classify it as `Not Automatable`. Do not attempt to automate it by adding waits, retries, or workarounds — stabilize the dependency at a lower layer (API or unit test) first.

---

## Automation Readiness Classification (Step 12)

Automation readiness is evaluated using the 6-condition gate. Every TC must be scored against all six conditions before a tier is assigned. This is not a checkbox exercise — apply judgment based on what the TC actually requires at runtime.

### 6-Condition Evaluation

| # | Condition | Fails when |
|---|---|---|
| 1 | **Stable** | The feature or UI/API contract is actively changing or under frequent revision. |
| 2 | **Repeatable** | The TC produces different outcomes on repeated runs due to data state, timing, or environment variance. |
| 3 | **High-value** | The TC covers cosmetic, rarely used, or low-business-impact behavior — automation adds little reliability gain. |
| 4 | **Low-flaky** | The TC depends on OTP, CAPTCHA, live third-party APIs, real payment gateways, unstable mocks, or hardcoded waits. |
| 5 | **Clearly assertable** | The expected result requires human visual judgment, subjective interpretation, or cannot be verified programmatically. |
| 6 | **Maintainable** | The TC requires fragile selectors, complex state setup, or automation effort that outweighs the long-term value. |

### Decision Rule

**If a TC fails 2 or more conditions → classify as `Not Automatable`.**

Do not attempt to work around failures using retries, waits, or conditional logic. Instead:
- Keep the TC manual.
- Flag it for redesign or dependency stabilization.
- Recommend moving validation to a lower testing layer (API or unit test) where the condition can be met.

### Tier Assignment

| Tier | Condition Score | Notes |
|---|---|---|
| `Automatable` | Passes all 6 conditions | Also requires deterministic steps, exact test data, independent execution, and a stable entry point. |
| `Partially Automatable` | Passes 4 or 5 of 6 conditions | At least one blocking sub-step requires manual execution or a mock strategy not yet defined. |
| `Not Automatable` | Fails 2 or more conditions | Keep manual. Flag reason. Recommend path to eventual automation if feasible. |

### Misclassification Flags

- **Minor** — existing Automation Readiness value is wrong but the TC is still usable.
- **Blocker** — TC is marked `Automatable` but fails 2 or more conditions, has non-deterministic behavior, missing exact test data, or a subjective expected result.

### Priority Rule — what to automate first

**Automate first:**
- Stable, frequently executed flows
- High business impact and revenue-critical scenarios
- Regression suite and smoke validations
- Flows with clear assertions and reusable setup components

**Avoid or delay automation for:**
- Features under active development or frequent change
- Flows with OTP, CAPTCHA, real-payment, or live third-party dependency
- Low-value, admin-only, or rarely executed validations
- Visual-only or layout checks
- Flows requiring heavy manual environment setup

### Final Principle

> Automation is not mandatory for all test cases. It must be selective, practical, and value-driven.
> A smaller stable automation suite is far more valuable than a large unstable suite nobody trusts.
> Never inflate the `Automatable` count to maximize coverage metrics. Accuracy of classification is more important than count.

---

## UI Review

UI tests focus on behavior, not fragile styling.

Prefer:
- User-visible behavior
- Validation and error states
- Role-based visibility
- Accessibility roles or stable test selectors
- Business outcome after UI action

Flag:
- Pixel-perfect checks unless specifically required
- Fragile selectors tied to layout or CSS classes
- Manual visual checks without clear criteria
- Layout, visibility, labels, empty states, navigation, and usability gaps

---

## Output Format (Markdown Review)

When reviewing without generating Excel, or when asked for a structured review report, use this structure:

```markdown
# Test Case Review

## Overall verdict
[Approved / Approved with changes / Needs rework]

## Summary
[Short assessment of coverage, quality, and risk]

## Spec Coverage Summary (when spec file provided)
| Metric | Value |
|---|---|
| Total Spec Requirements | N |
| Covered | n |
| Partially Covered | n |
| Not Covered | n |
| Coverage % | n/N × 100% |

## Test Type Coverage Summary
| Test Type | Present | TC Count | Gap |
|---|---|---|---|
| Functional | Yes/No | n | — / description |
| Negative | Yes/No | n | — / description |
| Smoke | Yes/No | n | — / description |
| Sanity | Yes/No | n | — / description |
| Integration | Yes/No | n | — / description |
| E2E | Yes/No | n | — / description |
| System | Yes/No | n | — / description |
| Boundary / Edge | Yes/No | n | — / description |
| Security | Yes/No | n | — / description |
| UI/UX | Yes/No | n | — / description |
| State / Workflow | Yes/No | n | — / description |
| NFR | Yes/No | n | — / description |

## Critical gaps
| Gap ID | Area | Issue | Risk | Required fix |
|---|---|---|---|---|

## Test case review findings (fails only)
| Test ID | Criterion | Issue | Recommended Fix | Result Type |
|---|---|---|---|---|

## Missing test cases
| Suggested Test ID | Requirement / Area | Scenario | Priority |
|---|---|---|---|

## Traceability gaps
| Requirement / AC ID | Coverage status | Missing scenario |
|---|---|---|

## Approval criteria
[Concrete conditions that must be met before approval]
```
