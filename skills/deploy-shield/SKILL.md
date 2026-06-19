---
name: deploy-shield
description: Audits a codebase branch or diff for production risks, deployment safety, and engineering hygiene before a release. Use when a developer wants to know if code is safe to deploy, assess blast radius, check rollback safety, audit dependencies, or get a pre-release risk report — even if they don't use the word "deployment".
metadata:
  version: 1.0.0
  author: Akash R
  email: akash.r@zysk.tech
  category: pre-deploy-safety
  tags:
    - deployment
    - code-review
    - production-safety
    - risk-audit
  product: zysk
  sprint: 1
  tested_with: claude-sonnet-4-6
---

# DeployShield

> Detect production risks before they cause incidents — not a generic PR reviewer.

## When to use

- Activate when: the user asks "is this ready to deploy?", "check for issues before I push", "what could go wrong?", "safe to merge?", "pre-release audit", "what's the blast radius?", "what breaks if I deploy this?"
- Activate when: the user asks for a code review with emphasis on runtime safety, reliability, or operational impact — even without the word "deployment"
- Activate when: the user mentions deployment risk, production readiness, rollback safety, or dependency health in the context of shipping code
Do NOT activate when: the user wants a general style review, formatting feedback, or architecture discussion with no imminent release

## Prerequisites

 - [ ] Access to the codebase (local path, repository, or pasted diff)
 - [ ] A branch, diff, or set of changed files to review
 - [ ] (Optional) Target environment — staging vs. production changes the risk threshold

## Steps

## Step 1: Understand the stack
Run git diff --stat and git status first. Read changed files with context. Do not analyze blind.
Identify:

Language & framework — Node/NestJS, Python/Django/FastAPI, Ruby/Rails, Go, Java/Spring, etc.
Database layer — PostgreSQL, MySQL, MongoDB, Redis, etc.
Queue/async layer — Bull, Sidekiq, Celery, SQS, etc.
Key integrations — payment gateways, external APIs, auth providers, cloud services
Infrastructure hints — Docker, Kubernetes, serverless, environment config files

Every finding must reference real patterns from the actual code — not generic examples. The stack context does not appear in the output as a list; it informs the findings.

## Step 2: Ask if scope is unclear

- Ask when: the diff is large, multiple unrelated areas changed, or the user has not specified what they are most worried about. A 47-file diff touching auth, payments, and migrations at the same time has very different risk than a single service change.
Skip when: the scope, stack, and intent are clear from context. Do not ask questions you already know the answers to.
When you do ask, 1-2 focused questions:

- Is there a specific area you are most concerned about — auth, migrations, a new integration?

- Are you deploying to production directly, or staging first?

## Step 3: Analyze across five dimensions

Evaluate every change against all five dimensions. Every finding must state what it is, why it is dangerous, and exactly what to fix.

1. Production Readiness — runtime and operational safety:

Missing timeouts on HTTP/DB/queue/external API calls
Blocking synchronous operations in async paths
Silent failures / swallowed exceptions
Missing error handling in DB queries or job processors
Unsafe async flows (missing await, unhandled promises, missing rescue/except)
Memory-heavy operations without pagination (unbounded row fetches)
Excessive DB queries in loops (N+1 patterns)
Connection/resource leaks (unclosed files, DB connections, HTTP clients)
Missing circuit breakers on external service calls
Cache stampede risks, unbounded retries without backoff

2. Blast Radius — downstream impact:

Which modules/services/packages are affected by the change
Shared utilities, base classes, or middleware consumed across the app
Real-time/websocket events that may break connected clients
Queue/job schema changes that break in-flight jobs
External integration side effects (payments, ERP, inventory, notifications)
ORM entity/model/schema changes that affect multiple consumers
API contract changes visible to frontends, mobile apps, or external consumers
Auth/session changes that could log out users or invalidate tokens
Database migrations that lock tables or cause downtime

3. Dependency Health — package and module quality:

Duplicate packages solving the same purpose (two HTTP clients, two date libraries)
Deprecated, unmaintained, or known-vulnerable packages
Packages with known security advisories — check package.json, requirements.txt, Gemfile, go.mod
Circular module/import dependencies
Unused imported providers, modules, or packages added in this diff

4. Code Hygiene — engineering quality:

Dead code / unreachable branches introduced in the diff
Duplicate business logic now existing in multiple places
Large functions doing too many things (god functions)
Missing input validation on new endpoints or public-facing methods
Credentials, secrets, or tokens hardcoded or logged
Missing or bypassed authorization checks on new routes
Overly broad exception catches that hide real errors

5. Deployment & Rollback Safety — release risk:

Migration safety: destructive operations — DROP COLUMN, ALTER TYPE, TRUNCATE, irreversible renames
Migration sequencing: schema change applied before or after the code that depends on it
Rollback viability: can the previous version run against the new schema?
New NOT NULL columns without defaults on existing tables
Model/entity changes without a corresponding migration
Config/env additions: new process.env.X or os.environ["X"] without fallback or documented requirement
Feature flags: changes that should be behind a flag but aren't
Auto-sync/auto-migrate settings left on — e.g., synchronize: true, DB_SYNC=true
Breaking API changes deployed before consumers are updated

## Step 4: Classify every finding by severity

- SeverityMeaning 
🔴CRITICALProduction outage, data loss, security breach, or payment/financial failure

🟠HIGHMajor operational risk, deployment instability, or auth/security issue

🟡MEDIUMReliability, scalability, or maintainability concern

🟢LOWMinor hygiene issue, non-blocking

## Step 5: Write the report
Produce the full DeployShield report. See Output section for exact structure.
What NOT to flag:

Code formatting, spacing, or style/lint issues
Subjective design preferences
Things already handled by global middleware, filters, or interceptors
TypeScript/type strictness warnings that don't affect runtime
Test file issues — unless they mask real production bugs

## Output

Format: Structured markdown report delivered inline in the conversation
Location: Inline response — no files written unless the user requests one
Example structure:

```markdown
## DeployShield Report — [branch or description]

**Stack detected:** [framework · DB · key integrations]

### Summary
[2-3 sentences: what changed, overall risk level, deploy recommendation]

---

### 🔴 CRITICAL Issues
[Each issue: what it is · why it's dangerous · what to fix]
— or — "None found."

### 🟠 HIGH Issues
— or — "None found."

### 🟡 MEDIUM Issues
— or — "None found."

### 🟢 LOW / Hygiene
— or — "None found."

---

### Production Readiness Score

| Dimension              | Score | Notes |
|------------------------|-------|-------|
| Production Readiness   | X/20  | ...   |
| Blast Radius           | X/20  | ...   |
| Dependency Health      | X/20  | ...   |
| Code Hygiene           | X/20  | ...   |
| Deployment Safety      | X/20  | ...   |
| **Total**              | **X/100** | |

- 90–100: ✅ Safe to deploy
- 75–89:  ⚠️  Deploy with caution — address HIGH issues first
- 60–74:  🚧 Do not deploy — fix CRITICAL/HIGH issues
- <60:    🛑 Stop — significant rework needed

---

### Deployment Recommendation
[✅ Safe to deploy | ⚠️ Deploy with caution | 🚧 Do not deploy | 🛑 Stop]
[One sentence primary reason]

### Top 3 Action Items
1. [Most urgent fix]
2. [Second priority]
3. [Third priority]
```