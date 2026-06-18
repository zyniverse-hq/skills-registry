---
name: wp-maintenance-conductor
description: Run a full WordPress maintenance session — pre-flight, backup, tiered updates, security, performance, and final backup with safety gates at every phase. Use for WP maintenance or site health checks.
version: 1.0.0
author: Stalin Marbhenn
email: stalin.marbhenn@zysk.tech
category: infra-security
tags:
  - wordpress
  - maintenance
  - updates
  - security
  - backup
product: zysk
sprint: 1
tested_with: claude-sonnet-4-6
---

# WordPress Maintenance Conductor

> Run a complete end-to-end WordPress maintenance session — pre-flight through final backup — with safety gates at every phase to prevent regressions on any WP stack.

## When to use

- Activate when: the user asks to "do the WordPress maintenance", "run maintenance on the site", or "monthly WP checkup"
- Activate when: the user says "audit and update the WordPress site", "run through the maintenance checklist", or "check site health"
- Activate when: the user says "full site audit", "update WordPress safely", "the site needs updating", or "make sure the site is healthy"
- Activate when: the user asks to "check what plugins need updating"
- Do NOT activate when: the user only wants a single isolated action (e.g., update one plugin only, clear cache only, or check one specific page)

## Prerequisites

- [ ] WP Admin credentials and access to the target site's dashboard
- [ ] Access to the active backup solution (ManageWP, UpdraftPlus, Jetpack Backup, or host-level)
- [ ] Browser with incognito/private mode available for visual verification
- [ ] PageSpeed Insights access (public tool — no account required)
- [ ] References folder at `references/` containing: `pre-flight.md`, `update-protocol.md`, `post-change-verify.md`, `security-checklist.md`, `cache-management.md`

## Steps

### Step 1: Pre-Flight Assessment

**Goal:** Know exactly what you're working with before touching anything.

1. Access WP Admin Dashboard — confirm you're logged in and the admin is accessible
2. Record: WordPress version, PHP version, active theme and version
3. List all active plugins and flag: any with available updates, any marked inactive, any known vulnerable
4. Check Site Health (`Tools → Site Health`) — note any CRITICAL or RECOMMENDED items
5. Note the current date/time for the report
6. Ask the user (or check records): when was the last backup? Has anything changed on the site since the last session?
7. Record baseline: what is working NOW before any changes (homepage loads, admin accessible, no visible errors)

Read: `references/pre-flight.md` for the full assessment checklist and what to record.

**Gate:** Passes when you have a clear snapshot of the current state and the admin is accessible with no critical blockers.

---

### Step 2: Backup Gate

**Goal:** Guarantee a recovery point exists before any changes.

**Non-negotiable rule:** If there is no confirmed recent backup (within 24 hours), trigger one before proceeding to Step 3. No exceptions.

1. Check the active backup solution (ManageWP, UpdraftPlus, Jetpack Backup, host-level, etc.)
2. Confirm the most recent backup: date, size, storage location
3. If last backup is older than 24 hours OR the user cannot confirm a backup exists: trigger a fresh backup now
4. Wait for backup completion confirmation before proceeding

**Gate:** Passes only when a backup exists that was taken BEFORE this session's changes.

---

### Step 3: Safe Update Sequence

**Goal:** Apply all available updates in risk order, with a verification step between each tier.

The risk order is fixed — never change it:

```
Tier 1 (Lowest risk): Security, SEO, analytics, utility plugins
Tier 2 (Medium risk): Form plugins, gallery, e-commerce add-ons
Tier 3 (Higher risk): Page builder add-ons, WooCommerce, caching/performance plugins
Tier 4 (Highest risk): Page builder core (Elementor, Divi, Beaver Builder)
Tier 5: Active theme
Tier 6: WordPress core
```

For each tier:
1. Trigger a backup checkpoint (ManageWP or UpdraftPlus incremental if available)
2. Apply updates for that tier
3. Run Tier Verification: WP Admin accessible, homepage loads without errors, no PHP notices or white screens, WooCommerce shop/checkout pages if installed
4. If verification fails: identify which update caused the issue, roll back that update, document it

Read: `references/update-protocol.md` for how to categorise plugins and handle edge cases (no rollback plugin, auto-updates, multisite).

**Gate:** Passes when all available updates are applied and Tier Verification passes for every tier.

---

### Step 4: Functional Verification

**Goal:** Confirm all critical site functions work after updates.

1. Test every Contact Form 7 / WPForms / Gravity Forms form — submit a test entry, confirm delivery
2. Run a broken links scan — fix or flag any found
3. Check WooCommerce checkout flow end-to-end if e-commerce is active
4. Check any site-specific critical flows the user has identified
5. Review Google Analytics / Site Kit — confirm tracking is firing (no sudden drop in real-time)
6. Check spam comments queue — clear if >0

Read: `references/post-change-verify.md` for the full verification checklist.

**Gate:** Passes when forms submit, no critical broken links remain, and key conversion paths are functional.

---

### Step 5: Security Audit

**Goal:** Run the universal security checklist — every item, every time.

The universal security checklist is in: `references/security-checklist.md`

Never skip this step. Security issues are silent — they won't show up in a visual audit. The checklist takes 10–15 minutes and can catch issues that have been open for months.

For each finding:
- Document it in the session notes with severity: CRITICAL / HIGH / MEDIUM / LOW
- If fixable immediately (e.g., adding a WPCode snippet, setting a Cloudflare rule): fix it now and mark RESOLVED
- If it requires credentials, server access, or user decision: mark PENDING and add to the to-do list with exact steps

**Gate:** Passes when every item on the security checklist has been assessed — either RESOLVED or documented as PENDING with steps. Passing does not mean everything is fixed; it means nothing is unknown.

---

### Step 6: Performance Audit

**Goal:** Measure baseline performance, identify the top issues, apply safe quick wins.

1. Run PageSpeed Insights for both mobile and desktop — record all scores (Performance, LCP, TBT, CLS, FCP, Accessibility, Best Practices, SEO)
2. Identify the top 3 issues by impact
3. Cross-reference with what's available on this site (caching plugin, CDN, image optimiser)
4. Apply safe wins that do not require theme/plugin changes: known-safe caching settings, image lazy load, font optimisation
5. For each change applied: clear relevant cache, verify no regression on frontend, re-note the change

For any setting that defers or removes CSS/JS: enable one setting at a time, clear cache after each, check the homepage AND any JS-heavy pages (animations, counters, sliders) before enabling the next. If a section goes blank, reverts visually, or the console shows JS errors: disable that setting immediately, clear cache, and re-verify.

Read: `references/cache-management.md` for caching plugin detection and settings guidance.

**Gate:** Passes when baseline scores are recorded, changes applied are documented, and the frontend is confirmed clean after each change.

---

### Step 7: Database & Cache Hygiene

**Goal:** Clean the database and clear all cache layers in the correct order.

Database cleanup (universal — same regardless of plugins):
1. Post revisions — remove all beyond the last 3
2. Auto-drafts — remove
3. Trashed posts/pages/comments — remove
4. Expired transients — remove
5. Spam comments — remove
6. Optimise all tables

Cache clearing — ALWAYS in this order:
```
1. Application-level cache (WordPress caching plugin: WP Rocket, LiteSpeed, W3TC, etc.)
2. Object cache (Redis/Memcached if active)
3. CDN cache (Cloudflare, BunnyCDN, etc.)
4. Browser cache verification (test with hard reload in incognito)
```

Clearing out of order wastes the effort — if you clear CDN before WordPress cache, the CDN re-fetches the old stale origin content.

Read: `references/cache-management.md` for per-platform detection and clearing instructions.

**Gate:** Passes when the database is optimised, all cache layers are cleared in correct order, and the site is serving fresh content (verified with a hard reload in incognito).

---

### Step 8: Visual Regression Audit

**Goal:** Check every public-facing page with fresh eyes after all changes.

1. List all public pages (use sitemap or WP Admin → Pages)
2. Visit each page in a browser (incognito, hard reload)
3. For each page check: page loads without error, hero/banner renders correctly, all images load, navigation works, no visible JS errors in console, CTA buttons/links are functional, animations/counters/sliders work
4. Document any issue found — severity, page, what's wrong

Minimum pages to check: Homepage, About, Services/Products, Contact, Blog index. Also check any page-builder-heavy pages (Elementor, Divi) — these are most sensitive to caching and JS changes.

**Gate:** Passes when every public page is visually confirmed clean, or any issue found is documented with a fix plan.

---

### Step 9: Final Backup

**Goal:** Take a clean backup of the post-session state.

1. Trigger a backup via the active backup solution
2. Name it clearly: `post-maintenance-{YYYY-MM}` or similar
3. Confirm it completes — don't just trigger, verify the completion status
4. Note the size and storage location

**Gate:** Passes when the backup completes successfully.

---

### Step 10: Documentation

**Goal:** Generate the session report.

Invoke the `wp-maintenance-report` skill with the full session context. The report should cover everything discovered and done across all steps.

If `wp-maintenance-report` is not available, write a plain Markdown summary covering: what was updated, what was fixed, what security issues were found, performance scores before/after, and all pending to-do items with exact steps.

## Output

- **Format:** Markdown maintenance report
- **Location:** Saved as a file via the `wp-maintenance-report` skill, or output as a message if the skill is unavailable
- **Example:** A structured report listing WordPress/plugin/theme versions updated, security findings with RESOLVED/PENDING status, PageSpeed scores before and after, database cleanup summary, and a to-do list for any deferred items with exact remediation steps

## Example

**User says:** "Do the WordPress maintenance on the site."

**Claude does:** Runs all 10 steps in sequence — assessing the current state, confirming a backup exists, applying updates in risk-tiered order with verification between each tier, testing critical site functions, auditing security and performance, cleaning the database and clearing all cache layers in correct order, visually checking every public page, taking a final backup, then generating a full session report.

**Result:** All available updates applied safely with no regressions, universal security checklist completed with all findings documented, performance baseline recorded and safe optimisations applied, all cache layers cleared in correct order, and a Markdown maintenance report ready for the client.

## Notes

- **Pause and confirm with the user before:** applying a major version update (WordPress X.0, page builder major release), rolling back an update after a Tier Verification failure, or applying a CRITICAL security fix immediately
- **Stop the session if:** the site becomes inaccessible and cannot be restored via available tools, a backup fails with no recovery point, or a critical plugin regression (WooCommerce, Elementor) cannot be quickly resolved
- **Document and move on (don't get stuck) when:** a fix requires server access, DNS changes, credentials you don't have, or a decision the user must make — document with exact steps and continue
- Works for any WP stack (any theme, caching plugin, or host) because Step 1 discovers the stack before any assumptions are made
- Core principles: order is everything (the sequence is risk-ordered), every change gets a verification, and gates must pass before proceeding — never skip them
