---
name: playwright-test-generation
description: Generate structured Playwright E2E tests by exploring the live UI first, then producing helpers, spec files, and a summary report.
version: 1.0.1
author: Deepikaa Naganathan
email: deepikaa.n@zysk.tech
category: qa-testing
tags:
  - playwright
  - e2e-testing
  - test-generation
  - automation
sprint: 1
tested_with: claude-sonnet-4-6
---

# Playwright Test Generation

> Generate structured Playwright E2E tests by exploring the live UI first, then producing helpers, spec files, and a summary report.

## When to use

- Activate when: the user asks to generate, write, or create Playwright tests for any feature or page
- Activate when: the user says "generate tests for X", "write tests for X", "create test cases for X", "test the X page/feature"
- Do NOT activate when: the user is only asking about test scenarios or planning (use test-scenario-planning instead)

## Prerequisites

- [ ] Live URL of the feature to test is accessible
- [ ] Valid credentials available for authenticated flows
- [ ] Playwright installed in the project (`npx playwright install`)
- [ ] TypeScript configured in the project

## Steps

### Step 1: Explore the Live Page

Use Playwright browser tools to navigate to the feature URL:
- Take a snapshot to inspect all elements, roles, labels, and interactions
- Click through all interactive elements to understand the full flow
- Note error states, modals, redirects, validation messages, loading states
- Explore as a real user would — positive path first, then intentional failures

### Step 2: Create the Helpers File

**File location:** `tests/<feature-name>/<feature-name>-helpers.ts`

All constants and shared helper functions MUST go here — never inside the spec file:
- URL constants (`FEATURE_URL`, `HOME_URL`, etc.)
- Every helper function used by more than one test (`login`, `enterPhone`, `navigate`, etc.)
- Any full-flow setup logic (`loginKeepModal`, etc.)

### Step 3: Generate the Spec File

**File location:** `tests/<feature-name>/<feature-name>.spec.ts`

One folder per feature. One spec file per feature. Never scatter tests across multiple files.
The spec file imports everything from the helpers file — no constants or helpers defined inside the spec file.

Add sub-describes (e.g. `Page Tour`, `Re-trigger`) inside the main describe when a feature has distinct sub-flows.

**Test coverage checklist — include all that apply:**

Positive:
- [ ] Page loads with all required elements visible
- [ ] Successful happy-path flow end-to-end
- [ ] All interactive states (toggle, expand, modal open/close)
- [ ] Session persistence after page refresh
- [ ] External links / redirects open correctly

Negative:
- [ ] Empty required fields — show validation error, do not submit
- [ ] Wrong/invalid inputs — show error, do not proceed
- [ ] Unregistered / unauthorised credentials
- [ ] Network failure (use `page.route()` to abort API calls)
- [ ] Multiple failed attempts / lockout

Edge Cases:
- [ ] Whitespace trimming in input fields
- [ ] Clipboard paste via `evaluate()` + `dispatchEvent`
- [ ] Max-length input enforcement
- [ ] XSS payload — no alert must fire
- [ ] SQL injection payload — must not bypass
- [ ] Keyboard Enter key submission
- [ ] Tab order / focus management
- [ ] Redirect from protected routes to login when unauthenticated

### Step 4: Playwright Config

Apply this config whenever `playwright.config.ts` is created or modified — single browser (Microsoft Edge), maximized window, sequential (one window at a time):

```ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  fullyParallel: false,
  workers: 1,
  use: {
    viewport: null,
    launchOptions: {
      args: ['--start-maximized'],
    },
  },
  projects: [
    {
      name: 'edge',
      use: {
        ...devices['Desktop Edge'],
        channel: 'msedge',
      },
    },
  ],
});
```

### Step 5: Summary Report

After generating tests, **always** create `reports/<feature-name>-summary-report.md` AND output the full report in chat. Do not wait to be asked.

One report file per feature. Never combine multiple features into one report.
File naming: `reports/<feature-name>-summary-report.md` (e.g. `login-summary-report.md`).

The report must include:
1. **Flow Summary** — end-to-end user flow, happy path, steps and triggers
2. **Performance** — page load speed, API response observations, spinners/skeletons noticed
3. **UI/UX & Accessibility** — visual clarity, keyboard navigability, ARIA roles, UX friction points
4. **Edge Case Possibilities** — all edge cases identified, covered and uncovered production risks
5. **Expected Outcome** — tests likely to pass, tests that may be flaky, overall confidence level

## Output

- **Format:** Two TypeScript files + one Markdown report
- **Location:** `tests/<feature-name>/` for test files, `reports/` for the summary report
- **Example:** `tests/login/login-helpers.ts`, `tests/login/login.spec.ts`, `reports/login-summary-report.md`

## Example

**User says:** "Generate Playwright tests for the login page"

**Claude does:** Navigates to the login page, explores all interactive elements, creates `login-helpers.ts` with URL constants and login utilities, generates `login.spec.ts` with positive/negative/edge case tests, then produces a summary report.

**Result:** A complete test suite with helper functions, a spec file covering all scenario types, and a structured summary report covering flow, performance, UI/UX observations, and expected outcomes.

## Notes

- Always explore the live UI first — never guess selectors
- Prefer `getByRole` with `name` over `getByTestId` for resilience
- All helper functions and constants belong in the helpers file, never inside the spec file
- The summary report is mandatory — create the file and show it in chat every time
- One report per feature — never combine multiple features into one report
