# Quality Gates, Automation Separation, and Verdict Rules

---

## Review Quality Gates

Every test case is assessed against three named quality gates. These gates determine the Review Status (Approved / Needs Fix / Rejected) and the per-TC flags in Sheet 4.

> **Review Status vs. Overall Verdict — two separate concepts:**
> - **Review Status** (Sheet 4, per-TC): "Approved / Needs Fix / Rejected" — quality of each individual test case.
> - **Overall Verdict** (Sheet 1, suite-level): "Approved / Approved with changes / Needs rework" — quality of the entire test suite.
> These use different terminology intentionally.

> **Defects column** lists quality defects in the test case itself (not bugs found in the product). These are Blocker-level findings that make the TC unusable until corrected.

### Gate 1 — Execution-ready

A TC is Execution-ready when a tester can pick it up and run it without asking any follow-up questions.

Checklist:
- Test steps are numbered and complete — no missing user actions or system responses.
- Preconditions are stated and sufficient to set up the test.
- Test data is specified with exact values — not "valid data", "any value", or other vague descriptors.
- User role and authentication state are defined.
- Environment or feature entry point is clear.

**Execution Ready = No** when the TC has any Blocker or Minor issue on: Test Steps, Pre-conditions, or Test Data.

### Gate 2 — Client-deliverable

A TC is Client-deliverable when it meets output quality standards safe to share with a client or product owner.

Checklist:
- Expected Result is specific and observable — no vague language such as "works correctly", "successfully", or "proper behavior".
- Severity is correctly assigned from the controlled list.
- Test Case Summary is clear, unique, and states one primary behavior.

**Client Deliverable = No** when the TC has any Blocker or Minor issue on: Expected Result, Severity, or Test Case Summary — or has any Blocker issue at all.

### Gate 3 — Production-ready

A TC is Production-ready when it is safe to include in a release sign-off suite.

Checklist:
- Execution-ready = Yes.
- Client-deliverable = Yes.
- No Blocker issues assigned to this TC.
- Spec traceability confirmed (when spec file provided).
- Automation Readiness correctly classified.

**Production Ready = No** when: Execution Ready = No, OR Client Deliverable = No, OR the TC has any Blocker issue.

---

## Automation Separation

**Terminology — input column vs. output Readiness tier:**
- TC file Automation Readiness column uses: `Automatable` · `Partially Automatable` · `Not Automatable`
- Sheet 4 Readiness column uses: `Automation-ready` · `Partially Automatable` · `Manual-only`
- Mapping: `Automatable` → `Automation-ready`; `Not Automatable` → `Manual-only`; `Partially Automatable` → `Partially Automatable`

Classify every TC into one of three tiers. Verify the existing Automation Readiness column value is correct against the 6-condition evaluation below.

---

### Automation Candidacy Evaluation — 6 Conditions

Before assigning a tier, evaluate each TC against all six conditions:

| # | Condition | Pass when |
|---|---|---|
| 1 | **Stable** | Requirements and UI/API behavior are not frequently changing. |
| 2 | **Repeatable** | The TC can run multiple times with consistent, deterministic results. |
| 3 | **High-value** | The TC covers critical business, user, security, or revenue-impacting functionality. |
| 4 | **Low-flaky** | The TC does not depend on unstable timing, random behavior, third-party instability, OTP, CAPTCHA, or unreliable environments. |
| 5 | **Clearly assertable** | Pass/fail conditions can be validated objectively without subjective human judgment. |
| 6 | **Maintainable** | Automation effort and long-term maintenance cost are reasonable relative to the value gained. |

**Decision Rule:** If a TC fails **2 or more** of the above conditions, classify it as `Not Automatable`. Keep it manual, flag it for redesign, stabilize its dependencies, or recommend moving validation to a lower testing layer (API or unit testing). Do not force automation on such TCs.

**Selection is value-driven, not coverage-driven.** It is NOT mandatory that all TCs be automated. A smaller stable automation suite is far more valuable than a large unstable suite nobody trusts.

---

### Priority Rule — what to automate first

**Automate first:**
- Stable flows
- Frequently executed flows
- High business impact scenarios
- Regression and smoke validations
- Flows with clear assertions and reusable components

**Avoid or delay automation for:**
- Frequently changing features
- Highly flaky scenarios (OTP, CAPTCHA, real-payment, third-party dependent)
- Low-value validations
- Visual-only checks
- Heavy manual dependency flows

---

### Automation-ready

Apply when the TC passes all 6 candidacy conditions AND all of the following technical criteria are true:
- Steps are deterministic and repeatable — same input always produces same output.
- Inputs and expected outputs are fully specified with exact values.
- TC is independent — does not require execution of another TC first.
- No subjective human judgment required to verify the result.
- No physical device, biometric, or real-payment dependency that cannot be simulated.
- Stable entry point exists (API endpoint, stable UI selector, or CLI command).

### Manual-only

Apply when the TC fails 2 or more candidacy conditions, OR when any of the following is true:
- Expected result requires visual or subjective human judgment (e.g., "layout looks correct").
- One-time or non-repeatable scenario (e.g., first-time setup wizard, data migration run).
- Flow depends on real external systems that cannot be mocked or stubbed.
- Physical, biometric, or real-payment dependency that cannot be simulated.
- TC explicitly tests exploratory, usability, or accessibility behavior without machine-verifiable criteria.
- TC depends on OTP, CAPTCHA, or live third-party service with no stable mock available.

### Partially Automatable

Apply when the TC passes 4 or 5 of the 6 candidacy conditions AND:
- Most steps are automatable but at least one step requires manual execution or non-deterministic timing.
- Mock or stub strategy is required but not yet defined in the TC.

**Flag misclassified values:**
- Minor — value is incorrect but TC is still usable.
- Blocker — TC is marked Automatable but fails 2 or more candidacy conditions, has non-deterministic behavior, missing test data, or a subjective expected result.

---

## Final Automation Principle

> The goal of automation is not to automate everything.
> The goal is to automate the right test cases that improve reliability, reduce manual effort, and provide fast, trustworthy feedback.

> A smaller stable automation suite is far more valuable than a large unstable suite nobody trusts.

During review, identify and separate only the test cases that are genuinely automation-ready based on the 6 conditions. Flag all others as `Partially Automatable` or `Not Automatable` with a clear reason. Never inflate the automation-ready count to improve coverage metrics.

---

## Verdict Rules

Suite-level overall verdict (Sheet 1, row 10). Computed automatically by the `_CRITICAL_TYPES` block in the Python script.

| Verdict | Condition |
|---|---|
| Approved | Zero blocker failures; no missing critical test types (Functional, Negative, E2E); spec coverage ≥ 80% when spec provided; tests are clear. |
| Approved with changes | Blocker failures in fewer than 20% of TCs, or isolated to one area; minor test type gaps; spec coverage 50–79% when spec provided. |
| Needs rework | Blocker failures in 20% or more of TCs; missing Functional, Negative, or E2E; spec coverage < 50% when spec provided; or major requirement gaps. |

---

## Review Tone

Be direct, factual, and actionable. Do not soften serious gaps. Explain why each issue matters and how to fix it.
