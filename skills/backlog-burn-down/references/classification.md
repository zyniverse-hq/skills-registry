# Issue Classification Reference

Used by Step 3 and Step 4 of `backlog-burn-down`.

---

## Track Definitions

| Track | When to use | Typical scope |
|---|---|---|
| **Quick-fix** | Change is 1–2 lines, the fix is obvious, no design decisions required | Single file, no new abstractions |
| **Clear-scope** | Fix is explicit and contained, but touches more than 1–2 lines or 1–2 files | Up to 3 files, one clear outcome |
| **Ambiguous** | Requirements are unclear, multiple valid approaches exist, or the body says "we should think about X" | Defer — needs PM or tech lead to clarify before assigning |

When in doubt, err toward **Ambiguous** rather than guessing. A deferred issue costs nothing; an ambiguously assigned issue wastes a dev's time.

---

## Stale-Check Dispositions

Run before classifying. Any issue that hits one of these dispositions is removed from the assignable batch.

| Finding | Action |
|---|---|
| File / function named in the issue no longer exists on `origin/dev` | Close as stale with verification comment |
| `git log -S` shows the fix was already committed | Close as stale with verification comment |
| Codebase was redesigned around the problem (file deleted, architecture changed) | Close as stale with verification comment |
| Issue carries `status: needs-investigation` label | Defer — already flagged ambiguous by a prior run |
| Issue depends on an unmerged PR or backend change | Defer with a note explaining the blocker |

Stale-close comment template:
```
Closing as stale — the referenced code no longer exists on origin/dev.
```

---

## Quick-Fix Bundling Rules

Bundle quick-fixes by **mental model**, not by size. A bundle is a group of issues a developer can fix in one focused session without context-switching.

### Bundle if:
- Issues share the same domain concept (e.g. all `aria-label` fixes, all `console.error → Sentry` swaps)
- A dev fixing one would naturally notice and fix the others in the same pass
- The combined diff would read as one coherent change in a PR review

### Do not bundle if:
- Issues touch unrelated domains (even if both are small)
- One issue is a bug fix and another is a refactor — different reviewer intent
- Bundling would make the PR harder to review or revert

### Examples

| Pair | Bundle? | Reason |
|---|---|---|
| Two missing `aria-label` attributes | Yes | Same a11y mental model |
| Two `console.error` → `Sentry` swaps | Yes | Same observability mental model |
| `aria-label` fix + wrong API URL | No | Unrelated domains |
| Bug fix + scope-creep refactor | No | Different intents, different reviewers |
| Three small unrelated fixes | No | Small doesn't mean same mental model |

### Bundle sizing
- No strict limit, but keep bundles reviewable in one sitting
- If a bundle would touch more than ~5 files, consider splitting it

---

## ETA Defaults (for Step 5 comment)

| Track | Default ETA |
|---|---|
| Quick-fix | 1–2 days |
| Clear-scope | 3–5 days |

These are defaults — the PM can override per issue during assignment.
