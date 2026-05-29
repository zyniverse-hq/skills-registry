# ANALYSIS — test-case-generator

> Generated against the [agentskills.io](https://agentskills.openml.io) standard.

---

## Overall Verdict

**Partially compliant.** The skill has a strong, well-structured body with clear step-by-step instructions, good examples, and practical edge-case coverage. However, it is missing the required `license` field, the required `compatibility` field (despite having environment-specific dependencies like `openpyxl` and the `py` executable), and numerous non-standard frontmatter fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`) are placed at the top level instead of being nested under `metadata:` as the spec mandates.

---

## Spec Compliance Checklist

| Check | Status | Detail |
|---|---|---|
| `name` field format | PASS | `test-case-generator` -- lowercase, hyphens only, no leading/trailing hyphens, 20 chars, exactly matches folder name |
| `description` present & non-empty | PASS | 178 chars -- within the 1-1024 char limit |
| `description` describes what it does | PASS | Clearly states: generate exhaustive, production-ready QA test cases |
| `description` describes when to use it | WARN | Partially -- mentions input types (user stories, BRDs, PRDs) but lacks explicit trigger verb phrases in the description field itself (those appear only in the body) |
| `license` field | FAIL | Not present -- required field is missing |
| `compatibility` field | FAIL | Not present -- skill has explicit environment dependencies (openpyxl 3.1.5, py executable, Write tool, Bash tool) that must be documented |
| `metadata` field structure | FAIL | 8 non-standard fields (version, author, email, category, tags, product, sprint, tested_with) are at the top level instead of nested under metadata: |
| `allowed-tools` field | N/A | Not present (optional) |
| Token budget (body) | PASS | ~2301 tokens -- well under the 5000-token recommendation |
| Line budget (body) | PASS | 154 body lines -- well under the 500-line recommendation |
| `scripts/` directory | FAIL | Skill generates and runs a Python script (gen_test_cases.py) at runtime, but no scripts/ subdirectory exists in the skill folder; the spec requires bundled scripts to live in scripts/ |
| `references/` directory | N/A | Not referenced; not applicable |
| `assets/` directory | N/A | Not referenced; not applicable |
| Body -- step-by-step instructions | PASS | 6 clearly numbered, sequential steps with detailed sub-instructions |
| Body -- examples | PASS | Concrete example with user input, Claude actions, and expected output described |
| Body -- edge cases | PASS | Step 2 category 4 is entirely dedicated to edge cases; Step 5 includes a quality checklist |

---

## What the Skill Gets Right

- The `name` field is perfectly formatted and exactly matches the folder name `test-case-generator`.
- The body is exceptionally well-structured: 6 numbered steps, 12 test categories, a quality validation checklist, and a worked example -- all self-contained.
- The description uses strong domain keywords (user stories, acceptance criteria, BRDs, PRDs, QA test cases) that aid agent discovery.
- Token and line budgets are both comfortably within spec limits (~2301 tokens, 154 lines).
- The example section is concrete and realistic, showing exact user input and describing expected output in detail.
- Security, edge cases, and regression impact are all explicitly covered -- going beyond what most QA skill specs include.
- The Notes section provides useful runtime guardrails (correct Python executable, pre-installed library assumption).

---

## Violations (Must Fix)

### 1. Missing `license` Field
The `license` field is a required field per the spec. The skill has no license declaration at all.

**Current (wrong):**

    name: test-case-generator
    description: Generate exhaustive ...
    version: 1.0.0
    author: Ajay R

**Fix:**

    name: test-case-generator
    description: Generate exhaustive ...
    license: MIT

---

### 2. Missing `compatibility` Field Despite Environment Dependencies
The skill has explicit, non-portable runtime dependencies: the `py` Windows executable, `openpyxl 3.1.5`, and the Write/Bash tools. The `compatibility` field is required when a skill has such prerequisites so that agents can determine if the environment supports the skill.

**Current (wrong):**
No `compatibility` field present.

**Fix:**

    compatibility: "Requires Windows environment with Python accessible via `py` command. openpyxl 3.1.5 must be pre-installed. Requires Write and Bash tools. Tested with claude-sonnet-4-6."

---

### 3. Non-Standard Frontmatter Fields at Top Level (Not Under `metadata:`)
The spec states: "Non-standard frontmatter fields MUST be nested under `metadata:`, not at top-level." The following 8 fields are non-standard and are currently at the top level: version, author, email, category, tags, product, sprint, tested_with.

**Current (wrong):**

    version: 1.0.0
    author: Ajay R
    email: ajay.r@zysk.tech
    category: qa-testing
    tags:
      - test-case-generation
      - qa-coverage
      - manual-testing
      - api-testing
      - security-testing
    product: zysk
    sprint: 1
    tested_with: claude-sonnet-4-6

**Fix:**

    metadata:
      version: 1.0.0
      author: Ajay R
      email: ajay.r@zysk.tech
      category: qa-testing
      tags:
        - test-case-generation
        - qa-coverage
        - manual-testing
        - api-testing
        - security-testing
      product: zysk
      sprint: 1
      tested_with: claude-sonnet-4-6

---

### 4. Python Script Not Bundled in `scripts/` Directory
Step 6 instructs the agent to write a Python script (gen_test_cases.py) at runtime using the Write tool. The spec requires that scripts be "bundled in `scripts/` subdirectory inside skill folder, not referenced externally." A pre-written, bundled script would also improve reliability and portability.

**Current (wrong):**
The skill dynamically generates the script at runtime with no bundled version.

**Fix:**
Create `scripts/gen_test_cases.py` inside the skill folder with the Excel generation logic pre-written. Update Step 6 to reference it:

    Execute the bundled script: `py "scripts/gen_test_cases.py"`

---

## What's More Than Needed (Consider Restructuring)

The `description` field is accurate, but it focuses entirely on the "what" and uses no direct trigger-phrase keywords (like "generate test cases", "write QA coverage", "create test cases for") that an agent routing layer would naturally match. Those phrases appear only in the "When to use" section of the body, which loads later. Consider embedding at least one trigger phrase directly in the `description` to improve upfront agent discovery before the body is loaded.

---

## What's Missing (Must Add)

### 1. `license` Field
Add a `license` field directly in the frontmatter (at the top level, alongside `name` and `description`). Example: `license: MIT`

### 2. `compatibility` Field
Document the environment prerequisites explicitly. The skill is Windows-specific (`py` command), requires a specific library version (`openpyxl 3.1.5`), and depends on Write and Bash tools being available. Without this field, agents in non-Windows environments may attempt to run the skill and fail silently.

### 3. Bundled `scripts/gen_test_cases.py`
The Excel generation script should be pre-authored and placed in a `scripts/` subdirectory. This makes the skill portable and self-contained -- agents will not need to synthesize the script from scratch on every activation, reducing variability in output.

---

## Summary Table

| Area | Status | Detail |
|---|---|---|
| `name` field | Pass | Correctly formatted, matches folder name exactly |
| `description` field | Warn | Present and informative, but lacks trigger verb phrases for upfront agent routing |
| `license` field | Missing | Required field not present |
| `compatibility` field | Missing | Required given Windows-specific `py` dependency and `openpyxl` version pin |
| `metadata` structure | Wrong | 8 non-standard fields (version, author, email, category, tags, product, sprint, tested_with) sit at top level instead of under metadata: |
| Token budget | Pass | ~2301 tokens -- well under the 5000-token limit |
| Line budget | Pass | 154 body lines -- well under the 500-line limit |
| Body structure | Excellent | 6 sequential steps, 12 test categories, quality checklist, worked example, and notes |
| Self-containment / portability | Fails | Relies on runtime script generation instead of a bundled scripts/ file; py command is Windows-only with no fallback |
