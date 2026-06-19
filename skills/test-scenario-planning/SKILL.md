---
name: test-scenario-planning
description: Plan high-level test scenarios that describe user behaviors and business rules before writing test code.
version: 1.0.1
author: Deepikaa Naganathan
email: deepikaa.n@zysk.tech
category: qa-testing
tags:
  - scenario-planning
  - test-strategy
  - qa
  - requirements
sprint: 1
tested_with: claude-sonnet-4-6
---

# Test Scenario Planning

> Plan high-level test scenarios that describe user behaviors and business rules before writing test code.

## When to use

- Activate when: the user asks to plan, define, or write test scenarios for any feature or module
- Activate when: the user says "write scenarios for X", "plan test scenarios for X", "what scenarios should I test for X", "create test plan for X"
- Do NOT activate when: the user wants actual test code generated (use playwright-test-generation instead)

## Prerequisites

- [ ] Live URL of the feature to explore is accessible
- [ ] Understanding of the feature's business purpose

## Steps

### Step 1: Understand the Feature

Use Playwright browser tools to explore the live page:
- Navigate through the full happy path
- Trigger error states, validation messages, modals
- Note distinct user goals and business rules

### Step 2: Identify Scenarios

Group what you observed into **behaviors**, not steps. Ask:
> "What is the user trying to achieve?"
> "What business rule is being enforced?"
> "What could go wrong from the user's perspective?"

Target: **10–15 scenarios** per feature. Never more than 20.

Scenario types to cover:
- **Positive** — happy path, successful flows
- **Negative** — rejection, validation, errors
- **Edge** — boundaries, unusual inputs, accessibility, security

### Step 3: Write the Scenario Document

**File location:** `specs/<feature-name>-scenarios.md`

Use this table format for every scenario:

| ID | Scenario | Type | Priority | Risk |
|----|----------|------|----------|------|
| SC-01 | User can log in with valid credentials | Positive | High | Low |
| SC-02 | Invalid credentials are rejected with clear feedback | Negative | High | Medium |

Priority rules:
- **High** — core user journey, data integrity, security
- **Medium** — important but not blocking
- **Low** — nice-to-have, cosmetic, rare edge

Risk rules:
- **High** — failure causes data loss, security breach, or user lockout
- **Medium** — failure degrades UX or causes confusion
- **Low** — failure is cosmetic or easily recoverable

### Step 4: Write the Summary Report

After the scenario table, **always** create `reports/<feature-name>-scenario-report.md` AND show it in chat. Do not wait to be asked.

One report per feature. Never combine features.
File naming: `reports/<feature-name>-scenario-report.md`

The report must include:
1. **Feature Overview** — what this feature does end-to-end from the user's perspective (3–5 sentences)
2. **Scenario Summary** — the full scenario table from Step 3
3. **Coverage Breakdown** — count of Positive / Negative / Edge scenarios
4. **What Each Scenario Covers** — for each scenario ID, list the test cases it will generate
5. **Risks and Gaps** — what is NOT covered and why
6. **Dependencies** — auth state needed, seed data, other features that must work first

## Output

- **Format:** One Markdown scenario document + one Markdown report
- **Location:** `specs/` for scenario document, `reports/` for the summary report
- **Example:** `specs/login-scenarios.md`, `reports/login-scenario-report.md`

## Example

**User says:** "Plan test scenarios for the login feature"

**Claude does:** Explores the live login page, identifies user goals and business rules, groups observations into 10–15 scenarios covering positive, negative, and edge cases, writes the scenario table, and produces a scenario planning report.

**Result:** A scenario document with a prioritized table and a report covering feature overview, coverage breakdown, what each scenario covers, risks, and dependencies.

## Notes

- One scenario covers multiple test cases — never create one scenario per test case
- Target 10–15 scenarios per feature, never more than 20
- Always explore the live UI first — never plan from assumptions
- The summary report is mandatory — create the file and show it in chat every time
- Vague scenario names are not acceptable — be specific: "Phone field rejects alphabetical input" not "Invalid input"
