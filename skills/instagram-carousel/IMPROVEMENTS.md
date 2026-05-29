# IMPROVEMENTS — instagram-carousel

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
Nine top-level frontmatter fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`, `disable-model-invocation`) are placed at the root of the YAML frontmatter. The spec requires all non-standard fields to be nested under a `metadata:` key. These fields are currently treated as unknown top-level keys and may be silently ignored or cause parsing errors in compliant skill registries.

### Before
```yaml
---
name: instagram-carousel
description: Generates a self-contained, swipeable HTML Instagram carousel with export-ready 1080x1350px slides, deriving brand colors, typography, and slide layout.
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
allowed-tools: "*"
---
```

### After
```yaml
---
name: instagram-carousel
description: Generates a self-contained, swipeable HTML Instagram carousel with export-ready 1080x1350px slides, deriving brand colors, typography, and slide layout. Use when creating social media content, IG posts, brand carousels, or multi-slide marketing designs for Instagram.
license: MIT
compatibility: "Requires Python 3.8+ and Playwright (pip install playwright && playwright install chromium) for PNG export. Preview generation works in any environment."
allowed-tools:
  - Bash
  - Write
  - Read
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
---
```

### Impact if implemented
- **Agent behaviour:** Skill registries and orchestration layers that validate frontmatter will correctly parse the skill without schema violations. Fields like `author` and `email` are preserved for attribution without polluting the root namespace.
- **Discoverability:** Registry indexers that scan standard fields will no longer encounter unexpected top-level keys; the skill will pass validation and be indexed correctly.
- **Portability:** Any team or project importing this skill into a compliant registry will not need to manually fix the frontmatter before use.
- **Risk reduced:** Prevents silent schema failures where registry tooling discards or ignores unrecognised top-level keys, causing `author`, `tags`, and `tested_with` metadata to be lost.

### Existing use (before fix)
Today, when a skill registry ingests `instagram-carousel`, it encounters nine unrecognised keys at the frontmatter root level. Depending on the parser's strictness, this can cause the entire skill to be rejected, or the non-standard fields to be silently dropped. A developer querying the registry for skills tagged `social-media` or authored by `arijit.saha@zysk.tech` will get no results because the `tags` and `email` fields were never stored. The `disable-model-invocation: false` flag at root level may also conflict with a standard field of the same name if the spec ever introduces it, creating a subtle override bug.

### Improved use (after fix)
Once the nine fields are nested under `metadata:`, the registry parser processes only recognised standard fields at the root and stores the custom metadata block intact under its own key. Tag-based discovery (`social-media`, `marketing`, `carousel`) works correctly. Author attribution is preserved and queryable. The `disable-model-invocation` flag is unambiguously scoped to custom metadata and cannot conflict with any future spec-level field. The skill passes frontmatter validation on first import with zero manual edits required.

---

## Improvement 2 — Add Missing `license` Field

### What needs to change
The `license` field is absent from the frontmatter entirely. The spec lists it as an optional-but-recommended field. For a skill published under an author's name and email (`arijit.saha@zysk.tech`), the absence of a license creates ambiguity about reuse rights — downstream teams do not know whether they can adapt or redistribute the skill.

### Before
```yaml
---
name: instagram-carousel
description: Generates a self-contained, swipeable HTML Instagram carousel...
version: 1.0.0
author: Arijit Saha
# license field is absent
---
```

### After
```yaml
---
name: instagram-carousel
description: Generates a self-contained, swipeable HTML Instagram carousel...
license: MIT
metadata:
  version: 1.0.0
  author: Arijit Saha
  ...
---
```

### Impact if implemented
- **Agent behaviour:** No direct change to agent execution. License is metadata consumed by humans and tooling, not the model.
- **Discoverability:** Some registries filter by license type (e.g., only showing open-source skills). Adding `license: MIT` makes the skill eligible for those filtered views.
- **Portability:** Teams evaluating whether they can fork, adapt, or embed the skill in a proprietary product now have a clear answer. Without a license, the legally safe default is "all rights reserved," which blocks reuse.
- **Risk reduced:** Prevents legal ambiguity in multi-team or open-source contexts where redistribution rights matter.

### Existing use (before fix)
Today, a developer at a different organisation browsing the skills registry finds `instagram-carousel` and wants to adapt it for their own brand toolkit. There is no license field. The legally conservative interpretation is that the skill is proprietary to `zysk.tech` and cannot be reused without explicit permission. The developer has to email `arijit.saha@zysk.tech` to clarify — or simply avoids using the skill altogether.

### Improved use (after fix)
With `license: MIT` in the frontmatter, the reuse terms are immediately clear. Developers can fork, adapt, and bundle the skill without requiring legal consultation. Registry tooling can surface the skill in "open skills" search filters. The author's intent is unambiguous and discoverable in the same place as all other skill metadata.

---

## Improvement 3 — Add Missing `compatibility` Field Documenting Python + Playwright Dependency

### What needs to change
The skill has a hard runtime dependency on Python 3.8+ and Playwright (Chromium) for the PNG export step described in Step 7. This dependency is mentioned in the `## Notes` section at the very bottom of the body — but it is not in the frontmatter `compatibility` field where tooling and agents expect to find environment requirements. An agent activating this skill in a Python-free or browser-less environment will fail silently at the export step with no upfront warning.

### Before
```markdown
## Notes

- **Dependency:** Python + Playwright (Chromium) for the PNG export step.
- Content must never overlap the progress bar...
```
_(No `compatibility` field in frontmatter)_

### After
```yaml
---
name: instagram-carousel
description: ...
license: MIT
compatibility: "Requires Python 3.8+ and Playwright (pip install playwright && playwright install chromium) for PNG export. Preview generation (HTML carousel) works in any environment."
---
```

And in the body `## Notes` section, keep a short cross-reference:

```markdown
## Notes

- **Dependency:** See `compatibility` in frontmatter. Install with: `pip install playwright && playwright install chromium`.
- Content must never overlap the progress bar...
```

### Impact if implemented
- **Agent behaviour:** Agents and orchestrators that check `compatibility` before activating a skill will detect the Python + Playwright requirement and either pre-install dependencies or surface a clear error before the user spends time configuring a carousel.
- **Discoverability:** The skill becomes filterable by environment. Teams running containerised agents can verify compatibility before onboarding.
- **Portability:** Any new environment importing the skill knows exactly what to install before running Step 7. No more hunting through the body for the dependency note buried in `## Notes`.
- **Risk reduced:** Prevents the failure mode where the user designs a full 7-slide carousel, approves the preview, and then hits a `playwright: command not found` error at the export step with no recovery path documented upfront.

### Existing use (before fix)
Today, a developer on a fresh machine activates the skill, works through Steps 1–6 (brand details, color palette, typography, slide build, preview), approves the carousel, and triggers the export. The Python script in Step 7 fails immediately because Playwright is not installed. The error is `ModuleNotFoundError: No module named 'playwright'` — nothing in the activation flow warned them. The install command (`pip install playwright && playwright install chromium`) is buried in `## Notes` at the end of the body, which the developer did not read before starting. They must now re-run the export script after installing, losing momentum.

### Improved use (after fix)
With `compatibility` in the frontmatter, any agent or developer who inspects the skill before activation immediately sees the Python + Playwright requirement. Orchestration tools can emit a pre-flight check: "This skill requires Playwright. Run `pip install playwright && playwright install chromium` before proceeding." The developer installs the dependency once, before even entering Step 1, and the export in Step 7 completes without interruption.

---

## Improvement 4 — Scope `allowed-tools` from `"*"` to Specific Tools

### What needs to change
`allowed-tools` is currently set to `"*"` (all tools). The skill only actually requires three tools: `Bash` (to run the Playwright export script), `Write` (to write the HTML file), and `Read` (to read uploaded images or existing files). Granting all tools is overly broad and introduces risk of unintended side-effects (e.g., the model deleting files, making network requests, or spawning processes unrelated to carousel generation).

### Before
```yaml
allowed-tools: "*"
```

### After
```yaml
allowed-tools:
  - Bash
  - Write
  - Read
```

### Impact if implemented
- **Agent behaviour:** The model is constrained to only the tools needed for the skill's workflow. It cannot accidentally invoke tools like `Edit` on unrelated files or use `WebSearch` mid-generation.
- **Discoverability:** No direct effect on discovery, but a precise `allowed-tools` list signals to reviewers that the skill is well-audited.
- **Portability:** Environments with strict tool-permission policies will accept a scoped list more readily than a wildcard grant. Some registries flag `"*"` as a security concern.
- **Risk reduced:** Eliminates the footgun where the model, while generating carousel HTML, incidentally modifies unrelated project files or makes outbound network calls because no tool boundary was enforced.

### Existing use (before fix)
Today, with `allowed-tools: "*"`, the model has permission to use any available tool at any point during carousel generation. In practice this is unlikely to cause problems, but it means a misbehaving or confused model could write to arbitrary paths, read sensitive files, or invoke destructive Bash commands — all within the skill's permission grant. Security-conscious organisations that audit tool permissions before deploying a skill will flag this and require a manual fix.

### Improved use (after fix)
With `allowed-tools: [Bash, Write, Read]`, the skill's tool footprint is minimal and auditable. A reviewer can verify in seconds that the skill can write the HTML file (`Write`), run the Playwright script (`Bash`), and read base64-encode source images (`Read`) — and nothing else. Organisations with strict permission policies can onboard the skill without modification.

---

## Improvement 5 — Strengthen `description` with Agent Discovery Keywords

### What needs to change
The `description` field accurately describes the skill's output artifact but lacks trigger keywords that agents use to match user intent to skill selection. Phrases like "social media content", "IG post", "brand carousel", and "multi-slide marketing" are natural ways users phrase requests but are absent from the description. This reduces the skill's discoverability in agent routing and semantic search.

### Before
```yaml
description: Generates a self-contained, swipeable HTML Instagram carousel with export-ready 1080x1350px slides, deriving brand colors, typography, and slide layout.
```

### After
```yaml
description: Generates a self-contained, swipeable HTML Instagram carousel with export-ready 1080x1350px slides, deriving brand colors, typography, and slide layout. Use when creating social media content, IG posts, brand carousels, or multi-slide marketing designs for Instagram.
```

### Impact if implemented
- **Agent behaviour:** Semantic routing agents matching user prompts like "create IG content for my brand" or "make a multi-slide post" will now surface this skill as a candidate, where before they might not have matched on the more technical "1080x1350px" phrasing.
- **Discoverability:** The description now contains natural-language trigger phrases that align with how marketing teams and social media managers phrase their requests, not just how engineers describe the output format.
- **Portability:** Skills shared across organisations benefit from broader trigger coverage — a team unfamiliar with Instagram's exact pixel dimensions will still find the skill when searching "marketing carousel."
- **Risk reduced:** Prevents the skill being overlooked by agent routing when the user's phrasing does not mention "HTML", "1080x1350", or "swipeable."

### Existing use (before fix)
Today, a marketing manager tells Claude "create some Instagram content for our product launch." The agent router scans skill descriptions for matches. The current description contains "Instagram carousel" and "1080x1350px" but not "social media content," "IG post," or "marketing." Depending on the router's embedding model and threshold, this skill may not rank highly enough to be selected, and the agent falls back to a generic response or a less-specific skill.

### Improved use (after fix)
With the extended description, the skill matches a broader set of user intents: "make an IG carousel," "create social media slides," "build a brand marketing post," and "generate multi-slide Instagram content" all surface `instagram-carousel` as the top candidate. The skill activates earlier in the conversation and the user reaches the brand-details intake step (Step 1) without needing to rephrase their request.

---

## Improvement 6 — Move Inlined Playwright Export Script to `scripts/export_slides.py`

### What needs to change
The ~50-line Python Playwright export script is inlined as a code block inside Step 7 of the body. The spec states that scripts must be bundled in a `scripts/` subdirectory inside the skill folder. Moving the script out of the body reduces token consumption, makes the script independently executable and version-controllable, and allows the body to reference it by path rather than reproducing it inline.

### Before
```markdown
### Step 7: Export slides as Instagram-ready PNGs

...

```python
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

INPUT_HTML = Path("/path/to/carousel.html")
OUTPUT_DIR = Path("/path/to/output/slides")
OUTPUT_DIR.mkdir(exist_ok=True)
TOTAL_SLIDES = 7  # Update to match your carousel
...
asyncio.run(export_slides())
```
```
_(~50 lines of Python inlined in the skill body)_

### After
File: `skills/instagram-carousel/scripts/export_slides.py` — contains the full Python script.

Body reference in Step 7:
```markdown
### Step 7: Export slides as Instagram-ready PNGs

After the user approves the carousel preview, run the bundled export script to produce 1080x1350px PNGs:

```bash
python skills/instagram-carousel/scripts/export_slides.py \
  --input /path/to/carousel.html \
  --output /path/to/slides/ \
  --slides 7
```

See `scripts/export_slides.py` for the full Playwright implementation and configuration constants (`VIEW_W`, `VIEW_H`, `SCALE`).
```

### Impact if implemented
- **Agent behaviour:** The model's instruction context is shorter (removing ~50 lines of Python), reducing token pressure and leaving more budget for content-generation instructions. The agent calls `Bash` to run the script rather than generating it inline.
- **Discoverability:** The scripts/ directory signals to skill browsers that this skill includes executable tooling — a useful signal for developers evaluating the skill.
- **Portability:** The script can be updated, tested, and versioned independently of the prose body. A bug fix in the Playwright logic does not require editing the skill body.
- **Risk reduced:** Eliminates the failure mode where the model slightly misrenders the inlined Python (indentation errors, missing imports) when reproducing it from the body context. The script on disk is always authoritative.

### Existing use (before fix)
Today, every time the skill is activated, the model loads the full ~50-line Python script into its context window as part of the body. When Step 7 is reached, the model either instructs the user to copy-paste the block manually or attempts to write it to disk using `Write` — reproducing it from memory, which introduces the risk of subtle transcription errors (wrong indentation, a missing `await`, incorrect path constants). The script is also harder to update: fixing a Playwright API change requires editing the skill body prose rather than a standalone `.py` file.

### Improved use (after fix)
With the script at `scripts/export_slides.py`, the model's Step 7 instruction is a single `bash` command. The script runs directly from disk, always matches the authored version, and can be updated by a maintainer without touching the skill body. The body saves approximately 50 lines and ~400 tokens, keeping the skill well within its line and token budgets even as future improvements are added.

---

## Priority Order

| Priority | Improvement | Effort | Impact |
|---|---|---|---|
| 1 | Nest non-standard frontmatter fields under `metadata:` | Low | Critical |
| 2 | Add missing `compatibility` field (Python + Playwright) | Low | Critical |
| 3 | Add missing `license` field | Low | High |
| 4 | Strengthen `description` with agent discovery keywords | Low | High |
| 5 | Scope `allowed-tools` from `"*"` to specific tools | Low | Medium |
| 6 | Move inlined Playwright script to `scripts/export_slides.py` | Medium | Medium |

---

## Before vs After: Full Skill Experience

### Before (current state)

A developer discovers `instagram-carousel` in the registry and attempts to import it into their organisation's skill runner. Immediately, the frontmatter parser flags nine unrecognised root-level keys (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`, `disable-model-invocation`). Depending on the runner's strictness, the skill either fails validation entirely or silently drops these fields — meaning `tags: [instagram, carousel, social-media]` are never indexed, and tag-based discovery returns no results. The `license` field is absent, so the legal team flags the skill as "unknown rights" and blocks deployment until the author confirms reuse terms. The `compatibility` field is absent, so no pre-flight check warns that Python + Playwright must be installed before the skill is useful.

When a marketing manager finally activates the skill and describes their brand, the agent works through Steps 1–6 flawlessly — the brand intake, color system, typography, slide architecture, and Instagram preview are all well-structured and produce a high-quality result. The manager approves the carousel. Then Step 7 runs the inlined Python script, and the terminal immediately throws `ModuleNotFoundError: No module named 'playwright'`. The install instructions are at the very bottom of the body in `## Notes`, which the manager never read. The `allowed-tools: "*"` grant means the model had unrestricted tool access throughout, which the security reviewer will flag in the post-deployment audit.

### After (all improvements applied)

With all six improvements applied, the skill imports cleanly into any compliant registry. The nine non-standard fields are correctly nested under `metadata:`, so the root frontmatter contains only spec-standard keys and passes validation on first import. `license: MIT` is present, so legal review is instant — teams know they can adapt and redistribute. The `compatibility` field documents the Python + Playwright requirement upfront, enabling orchestration tools to emit a pre-flight check: "Install Playwright before proceeding." Developers install the dependency before entering Step 1, and the export step in Step 7 completes without interruption.

The strengthened `description` now matches a wider set of user phrasings — "create IG content," "build a brand carousel," "make multi-slide marketing posts" — so the skill surfaces correctly in agent routing without requiring the user to know the exact technical terminology. `allowed-tools` is scoped to `[Bash, Write, Read]`, satisfying security audits and preventing unintended side-effects. The Playwright script lives at `scripts/export_slides.py`, is always authoritative, and can be maintained independently of the skill body. The body is shorter, the token budget has more headroom, and the overall skill is production-ready for cross-team deployment.
