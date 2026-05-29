# ANALYSIS - instagram-carousel

> Generated against the [agentskills.io](https://agentskills.openml.io) standard.

---

## Overall Verdict

**Partially compliant.** The skill has an excellent, well-structured body with detailed step-by-step instructions, thorough code examples, and strong edge-case coverage. However, it has a significant frontmatter violation: numerous non-standard fields (version, author, email, category, tags, product, sprint, tested_with, disable-model-invocation) are defined at the top level instead of being nested under metadata:. The license and compatibility fields are also absent.

---

## Spec Compliance Checklist

| Check | Status | Detail |
|---|---|---|
| `name` field format | PASS | `instagram-carousel` -- lowercase, hyphens only, no leading/trailing hyphens, 19 chars, matches folder name |
| `description` present & non-empty | PASS | 146 chars, well within 1-1024 range |
| `description` describes what it does | PASS | Clearly describes generating a swipeable HTML carousel with 1080x1350px export-ready slides |
| `description` describes when to use it | WARN | Describes the output well but omits trigger keywords like social media post, brand content, marketing slide |
| `license` field | FAIL | Field is absent |
| `compatibility` field | FAIL | Field is absent -- but the skill has a hard dependency on Python + Playwright (Chromium) that should be documented here |
| `metadata` field structure | FAIL | version, author, email, category, tags, product, sprint, tested_with, disable-model-invocation are all top-level non-standard fields; spec requires them under metadata: |
| `allowed-tools` field | WARN | Present as "*" (allow all) -- functional but overly broad; listing specific tools (Bash, Write, Read) would be more precise |
| Token budget (body) | PASS | Estimated ~3,300-3,500 tokens (body ~13,500 chars / 4); well under the 5,000-token limit |
| Line budget (body) | PASS | Estimated ~310 lines; under the 400 warn threshold and well under the 500-line limit |
| scripts/ directory | -- | No scripts/ directory; the Playwright export script is inlined in the body as a code block rather than bundled as a file |
| references/ directory | -- | Not present; not required |
| assets/ directory | -- | Not present; not required |
| Body -- step-by-step instructions | PASS | Seven clearly numbered steps covering the full workflow from brand intake to PNG export |
| Body -- examples | PASS | Includes concrete HTML/CSS/JS/Python code examples, font pairing table, slide sequence table, reusable component snippets |
| Body -- edge cases | PASS | Common export mistakes table explicitly covers five failure modes with root causes and fixes |

---

## What the Skill Gets Right

- **Name field** is perfectly formatted: lowercase, hyphen-separated, matches folder name exactly.
- **Step-by-step structure** is thorough and logical -- seven numbered steps that map a clear workflow from requirements gathering through to file export.
- **Code is complete and copy-paste ready** -- the JavaScript progressBar() and swipeArrow() functions, the HTML component snippets, and the Python/Playwright export script are all production-quality and fully self-contained.
- **Edge-case coverage** is strong -- the Common export mistakes table with five entries (wrong viewport size, shell interpolation bugs, font loading timing, frame chrome visibility, frame width mutation) is exactly the kind of defensive guidance that makes a skill reliable in the real world.
- **Font pairing table** and **slide sequence table** give the model concrete defaults to fall back on without requiring user input for every parameter.
- **Token and line budgets** are comfortably within limits despite the skill being content-rich.
- **Trigger conditions** in When to use are explicit, including a clear negative trigger (Do NOT activate when).
- **Description** is concise and accurately summarizes the skill output artifact.

---

## Violations (Must Fix)

### 1. Non-standard frontmatter fields not nested under metadata:

The spec states: Non-standard frontmatter fields must be nested under metadata:, not at top-level. Nine fields violate this rule.

**Current (violating):**

    version: 1.0.0
    author: Arijit Saha
    email: arijit.saha@zysk.tech
    category: comms
    tags:
      - instagram
      - carousel
      - social-media
      - marketing
      - design
    product: zysk
    sprint: 1
    tested_with: claude-sonnet-4-6
    disable-model-invocation: false

**Fix -- nest all non-standard fields under metadata::**

    metadata:
      version: 1.0.0
      author: Arijit Saha
      email: arijit.saha@zysk.tech
      category: comms
      tags:
        - instagram
        - carousel
        - social-media
        - marketing
        - design
      product: zysk
      sprint: 1
      tested_with: claude-sonnet-4-6
      disable-model-invocation: false

### 2. license field is missing

The spec lists license as an optional field that specifies applicable licensing terms. Its absence is acceptable for internal/proprietary skills, but should be explicitly set.

**Fix -- add to frontmatter (example):**

    license: MIT

Or for a proprietary skill:

    license: proprietary

### 3. compatibility field is missing

The spec defines compatibility as documenting environment prerequisites. This skill has a hard dependency on Python and Playwright (Chromium) for the export step -- users on environments without these installed will hit silent failures. This context belongs in compatibility.

**Fix -- add to frontmatter:**

    compatibility: "Requires Python 3.8+ and Playwright (pip install playwright && playwright install chromium) for PNG export. Preview generation works in any environment."

---

## What's More Than Needed (Consider Restructuring)

- **Inlined Playwright script** -- the Python export script (Step 7) is ~50 lines of code inlined in the body. The spec notes that scripts must be bundled in scripts/ subdirectory inside skill folder. Moving this to scripts/export_slides.py would reduce body length and make it reusable. The body can then reference it as scripts/export_slides.py.
- **allowed-tools: "*"** -- granting all tools is functional but imprecise. The skill only needs Bash (to run Playwright), Write (to write HTML), and Read. Scoping this reduces unintended side-effects.
- **Color system derivation rules** (Step 2) are detailed enough to be a design spec -- this level of prescriptiveness is valuable but could be condensed into a reference table rather than prose to save tokens.

---

## What's Missing (Must Add)

1. **license field** -- add a license value to the frontmatter (see Violations section above).
2. **compatibility field** -- document the Python + Playwright dependency so agents and users know the environment requirement before activation (see Violations section above).
3. **metadata: wrapper** -- wrap all non-standard fields under metadata: (see Violations section above).
4. **Description trigger keywords** -- the description could be strengthened with additional discovery keywords. Consider adding phrases like social media content, brand slides, IG post, or marketing carousel so agents match it more broadly.

   Current: Generates a self-contained, swipeable HTML Instagram carousel with export-ready 1080x1350px slides, deriving brand colors, typography, and slide layout.

   Suggested: Generates a self-contained, swipeable HTML Instagram carousel with export-ready 1080x1350px slides, deriving brand colors, typography, and slide layout. Use when creating social media content, IG posts, brand carousels, or multi-slide marketing designs for Instagram.

---

## Summary Table

| Area | Status | Detail |
|---|---|---|
| name field | Pass | Valid format, matches folder name instagram-carousel |
| description field | Warn | Accurate but lacks broader trigger keywords for agent discovery |
| license field | Missing | Not present in frontmatter |
| compatibility field | Missing | Not present; Python + Playwright dependency undocumented |
| metadata structure | Wrong | Nine non-standard fields at top level instead of nested under metadata: |
| allowed-tools field | Warn | Present but set to * (all tools); should be scoped |
| Token budget | Pass | ~3,300-3,500 estimated tokens; comfortably under 5,000 limit |
| Line budget | Pass | ~310 estimated lines; under 400 warn and 500 fail thresholds |
| Body structure | Excellent | Seven numbered steps, tables, code examples, edge-case table, clear output spec |
| Self-containment / portability | Warn | Body is self-contained; export script should move to scripts/ per spec; external dependency (Playwright) should be in compatibility |
