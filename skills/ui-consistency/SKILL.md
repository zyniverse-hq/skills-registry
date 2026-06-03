---
name: ui-consistency
description: Use when asked for any frontend UI change — modals, forms, buttons, tables, layouts, colors, or spacing. Runs pattern inspection before writing code; never skip for small changes.
license: MIT
compatibility: >
  Requires access to a frontend source directory (resources/js/, src/, assets/,
  or equivalent). Depends on Glob tool and an Explore sub-agent for pattern
  inspection. Compatible with Vue, React (JSX/TSX), Svelte, and Blade projects
  using Tailwind or Bootstrap. Designed for Claude Code.
metadata:
  version: "1.0.0"
  author: Ruthu Bahubali Jain
  email: ruthu.jain@zysk.tech
  category: engineering-practice
  tags: "frontend, ui, css, components, consistency"
  product: zysk
  sprint: "1"
  tested_with: claude-sonnet-4-6
---

# UI Consistency

> Inspect existing patterns before writing any frontend code — match, don't improve.

If the project ships a Claude design system file, that file is the Pattern Inventory and Step 1 is skipped. If not, conventions are inferred by scanning existing components.

## When to use

- Activate when: the user asks for ANY frontend UI change, fix, or addition (modals, forms, buttons, tables, layouts, colors, spacing, components, flows)
- Activate when: the user says "make it look like X", "similar to another page", or "fix the styling"
- Activate when: the user shares a screenshot and asks for a UI match
- Activate when: the user asks to change button color, padding, or any visual property
- Do NOT activate when: the change is purely back-end with no UI output
- Do NOT skip for small changes — small changes break consistency most often

## Prerequisites

- [ ] Access to the frontend source directory (`resources/js/`, `src/`, `assets/`, or equivalent)
- [ ] Existing components of the same type are present in the codebase (for reference reading)
- [ ] (Optional) A design system file (`DESIGN_SYSTEM.md`, `design-tokens.json`, etc.) in the project root

## Steps

### Step 1: Claude Design System Check

Use **Glob** to search the project root and common config directories for any of these file names (case-insensitive):

```
DESIGN_SYSTEM.md   design-system.md   design-system.json
design-tokens.md   design-tokens.json design-tokens.ts
claude-design.md   claude-design.json
tokens.json        tokens.ts
```

Also check `package.json` for a dependency whose name contains `design-system`, `design-tokens`, or `@anthropic`.

**If a design system file is found:**

1. Read the file in full.
2. Treat its contents as the authoritative Pattern Inventory — it replaces Step 2 entirely.
3. Add a one-line note to your response: _"Using project design system at `<path>`."_
4. Skip Step 2 and proceed directly to Step 3, using the design system as the inventory source of truth.

**If no design system file is found:** proceed to Step 2. Do not invent tokens or assume a design system exists.

### Step 2: Frontend Pattern Scan

Dispatch an **`Explore` agent** scoped to the frontend source directory (`resources/js/`, `src/`, `assets/`, or wherever components live). Instruct it to return findings directly in this conversation as a Pattern Inventory. No files should be written.

**What to extract:**

1. **CSS framework** — What framework is in use? (Bootstrap, Tailwind, custom, mixed?) What version? Are there multiple frameworks in the same project?
2. **Component file types** — `.vue`, `.tsx`, `.jsx`, `.svelte`, plain `.html`? Where do they live?
3. **Button patterns** — What utility/component classes appear on `<button>` elements? List every distinct combination observed. Do action and cancel buttons differ?
4. **Color utilities** — What color classes, CSS variables, or hex values appear? Which are used for destructive actions, confirmations, and neutral actions?
5. **Spacing conventions** — What margin/padding classes or values dominate in component templates?
6. **Overlay/modal approach** — Are modals driven by CSS framework JS (`data-bs-*`, `data-modal-*`), a Vue/React state variable (`v-if`, `useState`), a dedicated component library, or a custom overlay?
7. **Form patterns** — Label placement, validation error display, required field markers.
8. **Typography** — Heading tags and text utility classes used in components.
9. **Framework mixing rules** — Are there file-type boundaries for different frameworks (e.g. Tailwind only in Blade, Bootstrap only in Vue)?

**Output format — summarise findings as a Pattern Inventory block:**

```
## Pattern Inventory (discovered)
- CSS framework: <name + version>
- Component type: <.vue / .tsx / etc.>
- Framework mixing: <rule if any>
- Buttons — action: <classes> | cancel: <classes> | destructive: <classes>
- Colors — destructive: <class> | confirm: <class> | neutral: <class>
- Spacing — dominant: <classes>
- Modals — driven by: <approach> | typical states: <n>
- Forms — layout: <approach> | errors: <approach> | required: <approach>
- Typography — headings: <tags+classes> | body: <classes>
```

This inventory is the source of truth for all remaining steps.

### Step 3: Inspect Before You Touch

> The Pattern Inventory from Step 2 must exist before starting this step.

Before writing a single line of code, read existing components to verify and extend the Pattern Inventory with component-type-specific detail.

**3a — Locate related components**

Find 2–3 components that are the closest match to what you are about to build or change (same type: modal → read other modals, form → read other forms, table → read other tables). Read the full file — template, script/logic, and any scoped styles.

**3b — Extend the Pattern Inventory for this component type**

| Area | What to check |
|------|---------------|
| Buttons | Exact utility/component classes in sibling files; confirm match with Step 2; note any deviations |
| Colors | Color utility classes or CSS variables; hex colors in inline styles; destructive / confirm / neutral usage |
| Spacing | Dominant margin/padding classes; spacing inside modals (title↔body, body↔footer); form field spacing |
| Modal/overlay | Structure, state-toggling mechanism (`v-if`/`v-show`/`step` variable), footer content per state |
| Forms | Label layout; validation error display; required field markers |
| Typography | Heading tags + text utility classes; font size utilities |

**3c — Check ALL interactive states**

This is the most commonly missed step.

- **Modals**: read every step/view the modal can show. If it uses `v-if="step === 2"`, read what's in that block.
- **Buttons**: note what buttons appear in each state — do not add new button variants that don't exist elsewhere.
- **Forms**: note what happens after submission (loading state? success message? redirect?).

If the user referenced a specific component ("make it like the modal on the billing page"), find and read that exact file in full before proceeding.

### Step 4: Apply What You Found

Write the code. Rules:

1. **Framework classes over inline styles.** Use utility classes from the Pattern Inventory — never add `style=""` for things the CSS framework already handles.
2. **Match, don't improve.** If existing modals use a specific cancel button class, use that class exactly. Consistency is the goal, not design improvement — unless the user explicitly asks.
3. **Copy the button pattern exactly.** The most common failure is adding button colors that don't exist elsewhere. Use only the button classes observed in the Pattern Inventory.
4. **Cover every state.** If the component has multiple steps or views, style all of them using the same patterns. Do not style only the first visible state.
5. **No new inline styles unless unavoidable.** If you must add one, comment it: `<!-- intentional inline: no framework equivalent -->`.
6. **Respect framework mixing rules.** Never mix frameworks within a single file if the Pattern Inventory found file-type boundaries.
7. **No new color values.** Do not introduce any hex color (`#xxxxxx`) or RGB value that does not already exist in the codebase.

### Step 5: Self-Check Before Responding

Before presenting your code, run through this checklist:

- [ ] Did I read at least 2 existing components of the same type?
- [ ] Did I read ALL interactive states of the reference component (not just the first view)?
- [ ] Are all button classes copied from what I observed — not invented?
- [ ] Are there any inline hex colors I added? If yes, remove them.
- [ ] Did I violate the framework mixing rules from the Pattern Inventory? If yes, fix.
- [ ] Does every step/state of my component follow the same pattern as the rest?

If any answer is "no", fix it before responding.

## Output

- **Format:** Code (component file — `.vue`, `.tsx`, `.jsx`, etc.) with CSS utility classes matching the Pattern Inventory
- **Location:** Inline in chat, ready to paste into the relevant component file
- **Example:** A new confirmation modal that exactly matches the overlay pattern, button styles, and spacing found in existing modals — no new color values, no inline styles, no framework mixing

## Example

**User says:** "Add a delete confirmation modal to the users table"

**Claude does:** Runs the design system check, scans existing modal components, builds the Pattern Inventory, extends it with modal-specific detail from sibling files, then writes the modal following all observed patterns across every state (open, confirming, loading).

**Result:** A complete modal component using the project's exact button classes, overlay approach, and spacing — visually identical to every other modal in the codebase.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Skipping Step 2 and assuming the CSS framework | Step 2 is mandatory — run the Explore agent first |
| Using a button class not found in the Pattern Inventory | Only use what was observed; check the inventory |
| Styling only step 1 of a multi-step modal | Read every state branch and apply the same patterns throughout |
| Using framework JS to control component visibility | Check the Pattern Inventory for the modal approach; use component state if the framework is JS-driven |
| Copying an inline style from an existing component | Check if a framework utility class covers it; only replicate if there is genuinely no alternative |
| Mixing CSS frameworks within a single file | Check the framework mixing rules in the Pattern Inventory and respect them |

## Notes

- **Inline styles are legacy**: If you encounter ad-hoc inline styles in existing components, treat them as technical debt — do not replicate the inline style, use the framework utility equivalent. Only replicate if there is genuinely no utility class for it.
- **Pattern Inventory is the source of truth**: If the inventory contradicts something you think you know about the project's stack, trust the inventory. It was derived from what is actually in the codebase.
