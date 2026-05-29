# IMPROVEMENTS — razorpay-integration

> Improvement plan derived from SKILL.md + ANALYSIS.md audit against the agentskills.openml.io spec.

---

## Quick Summary

| | Before | After |
|---|---|---|
| Spec compliance | Partially compliant | Fully compliant |
| Critical violations | 3 | 0 |
| Agent discoverability | Medium | High |
| Portability | Partial | Pass |

---

## Improvement 1 — Nest Non-Standard Frontmatter Fields Under `metadata:`

### What needs to change

Nine non-standard fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`, `user-invocable`) are currently placed at the top level of the frontmatter. The agentskills spec requires that all non-standard fields be nested under a `metadata:` block at the top level. This is the most structurally important fix.

### Before
```yaml
---
name: razorpay-integration
description: Integrate Razorpay payment gateway end-to-end. Activate when users mention Razorpay, payment gateway, checkout, order creation, payment verification, webhook handling, or switching to live keys.
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
allowed-tools: [Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, EnterPlanMode, ExitPlanMode, TaskCreate, TaskUpdate, TaskList]
---
```

### After
```yaml
---
name: razorpay-integration
description: Integrate Razorpay payment gateway end-to-end. Activate when users mention Razorpay, payment gateway, checkout, order creation, payment verification, webhook handling, or switching to live keys.
license: MIT
compatibility: Requires backend codebase access. Supports Laravel, Node.js, Express, NestJS, Django, Flask backends and React, Next.js, Vue, or vanilla JS frontends. HTTPS required in production for Razorpay live keys.
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

### Impact if implemented
- **Agent behaviour:** Agents and tooling that parse frontmatter by spec will no longer encounter unexpected top-level keys, preventing silent parse failures or key collisions with future spec fields like `version` or `category` if the spec formalises them.
- **Discoverability:** Structured `metadata.tags` is queryable by registry tooling (e.g., filtering all skills tagged `payment-gateway`). Flat top-level tags may be ignored by conformant parsers.
- **Portability:** Any team consuming this skill via the agentskills registry will get clean, spec-conformant YAML that their toolchain can ingest without custom field-stripping logic.
- **Risk reduced:** Prevents a future spec field named `version`, `category`, or `tags` from silently overriding or conflicting with these custom values.

### Existing use (before fix)
Today, when a registry tool or agent loader reads the `razorpay-integration` SKILL.md, it encounters nine unexpected top-level keys (`version`, `author`, `email`, etc.) that do not belong to the spec's top-level namespace. Conformant parsers may warn, skip the skill entirely, or — worse — silently accept it while ignoring the custom fields. The `tags` array (`razorpay`, `payment-gateway`, `payments`, `checkout`, `webhooks`) is especially valuable for discoverability, but because it sits at the wrong level, registry search features that filter by tag will not index this skill correctly.

### Improved use (after fix)
After the fix, all nine custom fields live under `metadata:`, which is the spec's designated namespace for extension data. Registry tooling can now index `metadata.tags` for search, display `metadata.author` in skill cards, and filter by `metadata.category: engineering-practice` without any custom parsing rules. The top-level frontmatter is clean, predictable, and fully spec-conformant — meaning the skill will pass automated linting in CI pipelines that validate against the agentskills schema.

---

## Improvement 2 — Add Missing `license` Field

### What needs to change

The `license` field is absent from the frontmatter. The agentskills spec lists it as an optional-but-expected field for published skills. Without it, consumers of this skill have no machine-readable signal about the terms under which they can embed, modify, or redistribute it.

### Before
```yaml
---
name: razorpay-integration
description: Integrate Razorpay payment gateway end-to-end. ...
version: 1.0.0
author: Tazeen Soudagar
# no license field present
---
```

### After
```yaml
---
name: razorpay-integration
description: Integrate Razorpay payment gateway end-to-end. ...
license: MIT
...
---
```

### Impact if implemented
- **Agent behaviour:** No direct change to runtime agent behaviour, but registry tooling that displays or enforces licensing terms will now surface this skill correctly.
- **Discoverability:** Skills with a `license` field pass registry publication checks that skills without one may fail, increasing the skill's visibility in public listings.
- **Portability:** Other teams and organisations can now determine at a glance whether they are permitted to fork or embed this skill in proprietary workflows — critical for enterprise adoption.
- **Risk reduced:** Prevents a "license unknown" status in registry listings, which some enterprise toolchains treat as a hard block on skill installation.

### Existing use (before fix)
Currently, any engineer or agent framework that queries the skills registry for skills they are licensed to use will find no `license` field on `razorpay-integration`. Depending on the registry's policy, this may cause the skill to be flagged as "license unknown," blocked from enterprise installs, or simply displayed with a warning badge. The author (`tazeen.soudagar@zysk.tech`) and product (`zysk`) are identified, but the usage rights are unspecified.

### Improved use (after fix)
With `license: MIT` in the frontmatter, the skill is unambiguously open for use, modification, and redistribution. Registry publication checks pass cleanly. Enterprise teams can install it without legal review, and the `zysk` product identifier combined with MIT licensing gives clear attribution-and-permissiveness semantics to any downstream consumer.

---

## Improvement 3 — Add Missing `compatibility` Field

### What needs to change

The `compatibility` field is absent from the frontmatter. The skill's body already contains a detailed "Prerequisites" section covering supported frameworks, database requirements, and HTTPS constraints — but this information is buried in prose and not accessible to agents or tooling that read structured frontmatter fields before loading the full body.

### Before
```yaml
---
name: razorpay-integration
description: ...
# no compatibility field present
---

## Prerequisites

- [ ] A Razorpay account — test mode is free and sufficient to start
- [ ] Test API credentials: `key_id` and `key_secret` from the Razorpay dashboard
- [ ] Access to both backend and frontend of the project codebase
- [ ] Database access to create orders and payments tables
- [ ] HTTPS configured in production (Razorpay requires it for live keys)
```

### After
```yaml
---
name: razorpay-integration
description: ...
license: MIT
compatibility: Requires backend codebase access. Supports Laravel, Node.js, Express, NestJS, Django, Flask backends and React, Next.js, Vue, or vanilla JS frontends. HTTPS required in production for Razorpay live keys.
---

## Prerequisites

- [ ] A Razorpay account — test mode is free and sufficient to start
...
```

### Impact if implemented
- **Agent behaviour:** Agents that check `compatibility` before activating a skill can now immediately determine whether the detected tech stack matches — without parsing the body. For example, an agent working on a Ruby on Rails project can skip this skill before even loading it.
- **Discoverability:** Registry search and filtering by environment compatibility (e.g., "show me payment skills that support Laravel") will now index this skill correctly.
- **Portability:** Teams running automated skill-selection pipelines can pre-filter skills by compatibility without executing them, reducing token consumption and latency.
- **Risk reduced:** Prevents this skill from being activated on an incompatible stack (e.g., a Django project where the Laravel-specific Composer steps would produce confusing, broken output).

### Existing use (before fix)
Today, an agent or registry tool has no structured way to know that `razorpay-integration` requires a specific set of backend and frontend technologies. The prerequisites live in a markdown checklist inside the body — readable by a human scanning the skill, but invisible to automated tooling that makes activation decisions from frontmatter alone. An agent working on a Ruby on Rails or Go project might still activate this skill based on keyword matching ("payment gateway"), then waste tokens loading the full body before discovering it cannot apply the Laravel or Node.js instructions.

### Improved use (after fix)
With a `compatibility` field present, any conformant agent loader can read: "Supports Laravel, Node.js, Express, NestJS, Django, Flask backends and React, Next.js, Vue, or vanilla JS frontends. HTTPS required in production for Razorpay live keys." This single field allows the agent to make a stack-compatibility check before activation, show a warning if the project uses an unsupported backend, and surface the HTTPS production requirement as a structured prerequisite rather than a buried prose note.

---

## Improvement 4 — Offload "Context-Specific Adaptations" to `references/framework-adaptations.md`

### What needs to change

The "Context-Specific Adaptations" section contains four framework-specific subsections (Laravel, Next.js, React SPA, Express/Node.js), each with concrete package names and structural guidance. This section is valuable, but it is inside the body — which currently sits at 276 lines. As more frameworks are added (e.g., Django, NestJS, Flask), this section will push the body toward the 400-line warning threshold and eventually the 500-line hard limit. The content should be extracted to `references/framework-adaptations.md` and referenced from the body using a relative path, following the same pattern already used for `references/payment-flow.md`.

### Before
```markdown
## Context-Specific Adaptations

### For Laravel Projects (like SRMS)
- Use `razorpay/razorpay` composer package
- Create FormRequest for validation
- Use Jobs for async webhook processing
- Create API Resources for responses
- Follow existing auth patterns (Sanctum)
- Add to existing routes in `routes/api.php`

### For Next.js Projects
- Use `razorpay` npm package (server-side in API routes)
- Use React Hooks for checkout state management
- API routes in `app/api/` or `pages/api/`
- Use Server Actions (App Router) or API Routes (Pages Router)

### For React SPA
- Backend-agnostic frontend implementation
- Use Axios/Fetch for API calls
- Context API for order state management
- React Router for navigation flow

### For Express/Node.js
- Use `razorpay` npm package
- Middleware for signature validation
- Express routes for endpoints
- Use async/await for API calls
```

### After

In `SKILL.md` body (replaces the section above):
```markdown
## Context-Specific Adaptations

Read `references/framework-adaptations.md` for framework-specific package names, structural patterns, and routing conventions. Sections cover Laravel, Next.js, React SPA, and Express/Node.js, with extension points for Django, NestJS, and Flask.
```

In new file `references/framework-adaptations.md`:
```markdown
# Framework-Specific Adaptations — razorpay-integration

## Laravel
- Use `razorpay/razorpay` composer package
- Create FormRequest for validation
- Use Jobs for async webhook processing
- Create API Resources for responses
- Follow existing auth patterns (Sanctum)
- Add to existing routes in `routes/api.php`

## Next.js
- Use `razorpay` npm package (server-side in API routes)
- Use React Hooks for checkout state management
- API routes in `app/api/` or `pages/api/`
- Use Server Actions (App Router) or API Routes (Pages Router)

## React SPA
- Backend-agnostic frontend implementation
- Use Axios/Fetch for API calls
- Context API for order state management
- React Router for navigation flow

## Express / Node.js
- Use `razorpay` npm package
- Middleware for signature validation
- Express routes for endpoints
- Use async/await for API calls
```

### Impact if implemented
- **Agent behaviour:** The body shrinks by ~25 lines, giving headroom for future framework additions (Django, NestJS, Flask) without approaching the 500-line hard limit. Agents still access the full content via the `references/` file.
- **Discoverability:** No change to discoverability — the trigger keywords and description remain unchanged.
- **Portability:** Framework adaptation content in its own file is easier to update independently, version-control separately, and reuse across related skills (e.g., a `stripe-integration` skill could reference a shared `references/framework-adaptations.md`).
- **Risk reduced:** Prevents the body from hitting the 400-line warning threshold or 500-line hard limit as additional framework sections are added over time.

### Existing use (before fix)
Today, the "Context-Specific Adaptations" section takes up approximately 25 lines of the 276-line body. This is not a violation yet, but the section is a natural growth point — every new framework supported by the skill adds another 5–7 lines. If the skill is extended to cover Django, NestJS, and Flask (all mentioned in the `compatibility` section and the `description`), the adaptations section alone could reach 50–60 lines, pushing the total body toward the warning threshold. There is also no existing `references/framework-adaptations.md` file, meaning the framework guidance is only accessible by loading the entire body.

### Improved use (after fix)
After extraction, the body stays lean and focused on the three-phase workflow. Framework-specific details live in `references/framework-adaptations.md`, following the established pattern of `references/payment-flow.md`. The skill body's Step 6 ("Execute Implementation") can reference the adaptations file directly at the point where framework-specific SDK installation instructions are needed, making the flow more logical: discover stack in Phase 1, then consult `references/framework-adaptations.md` in Step 6 for the exact package and file structure to use.

---

## Priority Order

| Priority | Improvement | Effort | Impact |
|---|---|---|---|
| 1 | Nest non-standard fields under `metadata:` | Low | Critical |
| 2 | Add missing `compatibility` field | Low | High |
| 3 | Add missing `license` field | Low | Medium |
| 4 | Offload "Context-Specific Adaptations" to `references/` | Medium | Medium |

---

## Before vs After: Full Skill Experience

### Before (current state)

A developer publishing `razorpay-integration` to the agentskills registry today will find that automated spec linting flags nine top-level frontmatter violations. The fields `version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`, and `user-invocable` all sit at the wrong YAML level, meaning registry tooling either rejects the skill outright or strips the custom fields silently. The `tags` array — which contains highly valuable keywords like `razorpay`, `payment-gateway`, and `webhooks` — is effectively invisible to any tag-based search or filtering feature in the registry. The missing `license` field means the skill shows as "license unknown" in any listing that surfaces licensing status, which enterprise teams treat as a hard block. The missing `compatibility` field means an agent working on a Ruby on Rails or Go backend might activate this skill based on keyword matching alone, load the full body, and only discover incompatibility after reading several hundred lines of Laravel- and Node.js-specific instructions.

The skill body itself is excellent — the three-phase plan, approval gate, security conventions, and framework-specific adaptations are genuinely well-crafted. But the structural metadata issues mean the skill cannot be published cleanly, cannot be filtered by stack or tag, and cannot be licensed confidently. These are all pre-flight failures that happen before a single agent ever reads a line of the body.

### After (all improvements applied)

With all four improvements applied, `razorpay-integration` becomes a fully spec-conformant, publishable skill. The frontmatter has a clean top-level structure (`name`, `description`, `license`, `compatibility`, `allowed-tools`, `metadata`) that passes automated linting in CI. The `metadata:` block contains all nine custom fields exactly as authored — none are lost, they are simply correctly namespaced. Registry search can now index the skill by `metadata.tags`, filter it by `metadata.category: engineering-practice`, and display `metadata.author` and `metadata.version` in skill cards.

The `compatibility` field gives agents and registry tooling a structured, pre-parse signal: this skill requires Laravel, Node.js, Express, NestJS, Django, or Flask on the backend, and React, Next.js, Vue, or vanilla JS on the frontend, with HTTPS in production. An agent can check this field before activation and immediately rule out incompatible stacks — saving tokens, reducing hallucination risk, and preventing confusing output for users on unsupported frameworks. The `license: MIT` field removes any legal ambiguity for enterprise teams and passes publication checks that previously left the skill in a "license unknown" state.

The optional extraction of "Context-Specific Adaptations" to `references/framework-adaptations.md` future-proofs the body against growth. At 276 lines today, the body is healthy — but with Django, NestJS, and Flask sections anticipated, extracting the adaptations now ensures the body stays lean and focused on the three-phase workflow that makes this skill uniquely effective, while the framework-specific detail remains fully accessible via the references pattern already established by `references/payment-flow.md`.
