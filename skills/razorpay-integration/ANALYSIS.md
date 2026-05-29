# ANALYSIS — razorpay-integration

> Generated against the [agentskills.io](https://agentskills.openml.io) standard.

---

## Overall Verdict

**Partially compliant.** The skill body is well-structured, thorough, and genuinely useful — it covers discovery, planning, implementation, and post-launch guidance with strong security awareness and concrete examples. However, it has a significant structural violation: nine non-standard frontmatter fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`, `user-invocable`) are placed at the top level instead of being nested under `metadata:` as the spec requires. The `license` and `compatibility` fields are also absent.

---

## Spec Compliance Checklist

| Check | Status | Detail |
|---|---|---|
| `name` field format | PASS | `razorpay-integration` — lowercase, hyphens only, no leading/trailing hyphen, 21 chars (<=64), matches folder name exactly |
| `description` present & non-empty | PASS | 183 chars, well within 1-1024 char limit |
| `description` describes what it does | PASS | "Integrate Razorpay payment gateway end-to-end" is precise and action-oriented |
| `description` describes when to use it | PASS | Lists specific trigger keywords: Razorpay, payment gateway, checkout, order creation, payment verification, webhook handling, switching to live keys |
| `license` field | FAIL | Field is absent; spec lists it as optional but expected for published skills |
| `compatibility` field | FAIL | Field is absent; prerequisites exist in the body but not in the structured frontmatter field |
| `metadata` field structure | FAIL | Nine non-standard fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`, `user-invocable`) are at top-level frontmatter instead of nested under `metadata:` |
| `allowed-tools` field | PASS | Present and lists 11 tools using array syntax; experimentally valid |
| Token budget (body) | PASS | ~2918 tokens (body is ~11,671 chars / 4); well under the 5000-token warning threshold |
| Line budget (body) | PASS | 276 lines; under the 400-line warn threshold and the 500-line hard limit |
| `scripts/` directory | N/A | No scripts directory; all logic is inline instructions, no external scripts needed |
| `references/` directory | PASS | `references/payment-flow.md` exists and is referenced in Step 3 using a relative path |
| `assets/` directory | N/A | No assets directory; none needed for this skill |
| Body — step-by-step instructions | PASS | Three clearly labelled phases with seven numbered steps; each step has sub-bullets and concrete actions |
| Body — examples | PASS | A concrete end-to-end example covers a real user prompt, Claude actions, and the expected result |
| Body — edge cases | PASS | Covers webhook async vs. frontend callback timing, signature mismatch, ngrok for local testing, HTTPS requirement, test-vs-live key separation, and the paise unit trap |

---

## What the Skill Gets Right

- **Name and description are exemplary.** The name matches the folder exactly; the description front-loads the action ("Integrate Razorpay payment gateway end-to-end") and a precise list of trigger keywords agents can match against.
- **Three-phase gating pattern is excellent.** The explicit "do not write code until plan is approved" gate at the end of Phase 2 is exactly right for a payment integration where misaligned assumptions touch real money and databases.
- **Security coverage is thorough.** The skill calls out: never expose `key_secret` to the frontend, HMAC-SHA256 signature validation for both payment verification and webhooks, CSRF protection, HTTPS requirement, and encrypted storage — all specific and actionable.
- **Framework-specific adaptations are practical.** Separate sections for Laravel, Next.js, React SPA, and Express/Node.js give concrete package names and structural guidance rather than vague generics.
- **References file is properly used.** The ASCII payment-flow diagram is offloaded to `references/payment-flow.md` and referenced with a relative path, keeping the body lean while providing a rich visual aid.
- **Conventions section prevents common bugs.** The paise unit note (Rs.100 = 10000 paise), unique order IDs, and async webhook warning are exactly the gotchas that cause production incidents.
- **Completion criteria are concrete and verifiable.** The "Skill Completion" section gives seven discrete, checkable conditions rather than a vague "integration is done."
- **Token and line budgets are healthy.** At ~2918 tokens and 276 body lines, there is significant room before hitting spec limits — no trimming required.

---

## Violations (Must Fix)

### 1. Non-standard frontmatter fields must be nested under `metadata:`

Nine fields are placed at the top level of the frontmatter. The spec is explicit: "Non-standard frontmatter fields must be nested under `metadata:`, not at top-level."

**Current (violating):**

```yaml
---
name: razorpay-integration
description: ...
version: 1.0.0
author: Tazeen Soudagar
email: tazeen.soudagar@zysk.tech
category: engineering-practice
tags:
  - razorpay
  - payment-gateway
  - payments
  - checkout
  - webhooks
product: zysk
sprint: 1
tested_with: claude-sonnet-4-6
user-invocable: true
allowed-tools: [...]
---
```

**Fixed:**

```yaml
---
name: razorpay-integration
description: ...
license: MIT
compatibility: Requires backend codebase access (Laravel, Node.js, Express, NestJS, Django, or Flask). Frontend must be React, Next.js, Vue, or vanilla JS. HTTPS required for live Razorpay keys.
allowed-tools: [Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, EnterPlanMode, ExitPlanMode, TaskCreate, TaskUpdate, TaskList]
metadata:
  version: 1.0.0
  author: Tazeen Soudagar
  email: tazeen.soudagar@zysk.tech
  category: engineering-practice
  tags:
    - razorpay
    - payment-gateway
    - payments
    - checkout
    - webhooks
  product: zysk
  sprint: 1
  tested_with: claude-sonnet-4-6
  user-invocable: true
---
```

### 2. `license` field is missing

The spec lists `license` as an optional field for specifying applicable licensing terms. For a published skill, this should be present.

**Fix:** Add `license: MIT` (or the appropriate license) to the frontmatter at the top level alongside `name` and `description`.

### 3. `compatibility` field is missing

The spec's `compatibility` field (up to 500 chars) documents environment prerequisites. The skill covers prerequisites in the body's "Prerequisites" section, but the structured frontmatter field is absent, making the skill harder for automated tooling to filter or validate.

**Fix:** Add a `compatibility` field, for example:

```yaml
compatibility: Requires backend codebase access. Supports Laravel, Node.js, Express, NestJS, Django, Flask backends and React, Next.js, Vue, or vanilla JS frontends. HTTPS required in production for Razorpay live keys.
```

---

## What's More Than Needed (Consider Restructuring)

- **"Context-Specific Adaptations" section is broad but not excessive.** Four framework sections (Laravel, Next.js, React SPA, Express) each add real value without inflating the body. No restructuring required, but if future frameworks are added, consider moving this content to `references/framework-adaptations.md` to preserve body headroom.
- **"Skill Completion" section is slightly redundant** with the Output section and Phase 3 step checklist. It could be merged into the Output section without losing information, but it is not a spec violation.

---

## What's Missing (Must Add)

1. **`license` field in frontmatter.** Required to be a complete, publishable skill. Add `license: MIT` or the applicable license at top level.

2. **`compatibility` field in frontmatter.** Move the environment prerequisites from the body into this structured field so agents and tooling can read them without parsing the body.

3. **`metadata:` wrapper for all non-standard fields.** All nine non-standard top-level fields must be moved under `metadata:`. This is the most important structural fix.

---

## Summary Table

| Area | Status | Detail |
|---|---|---|
| `name` field | Pass | Valid format, matches folder name, within length limit |
| `description` field | Pass | Clear, action-oriented, strong trigger keywords, within char limit |
| `license` field | Missing | Must be added at top-level frontmatter |
| `compatibility` field | Missing | Must be added at top-level frontmatter (prerequisites exist in body but not in the structured field) |
| `metadata` structure | Wrong | Nine non-standard fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`, `user-invocable`) are at top level instead of nested under `metadata:` |
| `allowed-tools` field | Pass | Present, lists 11 tools, experimentally valid |
| Token budget | Pass | ~2918 tokens; well under 5000-token limit |
| Line budget | Pass | 276 body lines; well under 500-line limit |
| Body structure | Excellent | Three-phase plan with seven numbered steps, explicit approval gate, concrete sub-tasks, and clear completion criteria |
| Self-containment / portability | Pass | All references use relative paths; `references/payment-flow.md` is bundled in the skill folder; no external script dependencies |
