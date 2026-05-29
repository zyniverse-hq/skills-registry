# IMPROVEMENTS — test-case-generator

> Improvement plan derived from SKILL.md + ANALYSIS.md audit against the agentskills.openml.io spec.

---

## Quick Summary

| | Before | After |
|---|---|---|
| Spec compliance | Partially compliant | Fully compliant |
| Critical violations | 4 | 0 |
| Agent discoverability | Medium | High |
| Portability | Fails | Pass |

---

## Improvement 1 — Add Missing `license` Field

### What needs to change
The `license` field is a required frontmatter field per the agentskills.openml.io spec. The skill has no license declaration whatsoever. It must be added at the top level of the frontmatter, alongside `name` and `description`.

### Before
```yaml
---
name: test-case-generator
description: Generate exhaustive, production-ready QA test cases from user stories, acceptance criteria, BRDs, PRDs, or feature descriptions — covering all test types with zero critical gaps.
version: 1.0.0
author: Ajay R
email: ajay.r@zysk.tech
---
```

### After
```yaml
---
name: test-case-generator
description: Generate exhaustive, production-ready QA test cases from user stories, acceptance criteria, BRDs, PRDs, or feature descriptions — covering all test types with zero critical gaps.
license: MIT
---
```

### Impact if implemented
- **Agent behaviour:** Registries and agent orchestrators that enforce required fields will now accept this skill without erroring out or skipping it during indexing.
- **Discoverability:** Skills without a license field may be excluded from curated registry listings or flagged as incomplete, reducing visibility.
- **Portability:** Teams adopting this skill across projects will know under what terms they can redistribute or modify it.
- **Risk reduced:** Prevents silent rejection by spec-validating agents that gate on required frontmatter fields before loading the skill body.

### Existing use (before fix)
Today, any agent or registry tool that validates skill frontmatter against the spec will flag `test-case-generator` as non-compliant the moment it reads the frontmatter. Depending on the validator's strictness, the skill may be skipped entirely during loading, causing QA engineers who trigger "generate test cases" to get no response — or a fallback generic response — with no visible error explaining why. The missing `license` field is a silent compliance gap.

### Improved use (after fix)
After adding `license: MIT`, the skill passes frontmatter validation on the first required-field check. Registry indexers include it without warnings. Teams importing it into their own skill sets know immediately that it is permissively licensed and can be modified or redistributed. The skill loads reliably across all compliant agent runtimes.

---

## Improvement 2 — Add Missing `compatibility` Field for Windows/openpyxl Dependencies

### What needs to change
The skill has hard, non-portable runtime dependencies: the `py` Windows-only executable, `openpyxl 3.1.5`, and the Write and Bash tools. Without a `compatibility` field, agents running on Linux or macOS environments will attempt to execute Step 6 and fail silently when `py` is not found. The `compatibility` field must be added at the top level of the frontmatter.

### Before
```yaml
---
name: test-case-generator
description: Generate exhaustive, production-ready QA test cases from user stories, acceptance criteria, BRDs, PRDs, or feature descriptions — covering all test types with zero critical gaps.
license: MIT
---
```
(No `compatibility` field present anywhere in the frontmatter.)

### After
```yaml
---
name: test-case-generator
description: Generate exhaustive, production-ready QA test cases from user stories, acceptance criteria, BRDs, PRDs, or feature descriptions — covering all test types with zero critical gaps.
license: MIT
compatibility: "Requires Windows environment with Python accessible via the `py` command. openpyxl 3.1.5 must be pre-installed. Requires Write and Bash tools. Tested with claude-sonnet-4-6."
---
```

### Impact if implemented
- **Agent behaviour:** Agents in non-Windows environments can detect the incompatibility before invoking the skill and surface a clear message to the user ("this skill requires a Windows environment") instead of failing mid-execution at Step 6.
- **Discoverability:** Registry filters for environment compatibility will correctly categorise this skill as Windows-specific, preventing it from being served to macOS/Linux users.
- **Portability:** Explicitly documents the openpyxl version pin (3.1.5), so teams that upgrade openpyxl know to re-test the Excel generation step.
- **Risk reduced:** Prevents the frustrating failure mode where the agent generates 40-60 test cases in the Markdown table (Steps 1-5 succeed) but then crashes at Step 6 when writing the `.xlsx` file — leaving the user with an incomplete output and no explanation.

### Existing use (before fix)
Today, a QA engineer on a macOS machine triggers "generate test cases for the payment checkout flow." The skill activates, runs Steps 1-5 successfully, produces the full Markdown table, then hits Step 6 where it calls `py "gen_test_cases.py"`. The `py` command does not exist on macOS; the Bash tool returns a non-zero exit code. The agent has no guidance on what to do next. The user receives an incomplete output — the Markdown table but no `.xlsx` file — with a confusing error. There is no upfront signal that this skill is Windows-only.

### Improved use (after fix)
After adding the `compatibility` field, an agent on macOS reads the frontmatter before executing the body and detects the Windows-only constraint. It either skips the skill and routes to an alternative, or immediately informs the user: "This skill requires a Windows environment with the `py` command and openpyxl 3.1.5 pre-installed." On Windows environments, the field confirms the expected setup, and Step 6 executes with confidence. The `openpyxl 3.1.5` version pin is visible to maintainers who later consider upgrading the library.

---

## Improvement 3 — Move Non-Standard Frontmatter Fields Under `metadata:`

### What needs to change
The spec mandates that non-standard frontmatter fields must be nested under `metadata:`, not placed at the top level. Currently, 8 non-standard fields — `version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, and `tested_with` — are at the top level. This causes frontmatter parsers to either reject the skill or silently ignore these fields, losing organisational metadata.

### Before
```yaml
---
name: test-case-generator
description: Generate exhaustive, production-ready QA test cases from user stories, acceptance criteria, BRDs, PRDs, or feature descriptions — covering all test types with zero critical gaps.
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
```

### After
```yaml
---
name: test-case-generator
description: Generate exhaustive, production-ready QA test cases from user stories, acceptance criteria, BRDs, PRDs, or feature descriptions — covering all test types with zero critical gaps.
license: MIT
compatibility: "Requires Windows environment with Python accessible via the `py` command. openpyxl 3.1.5 must be pre-installed. Requires Write and Bash tools. Tested with claude-sonnet-4-6."
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
```

### Impact if implemented
- **Agent behaviour:** Spec-compliant frontmatter parsers will correctly read the top-level standard fields (`name`, `description`, `license`, `compatibility`) and separately ingest the `metadata` block for organisational purposes, without conflicts or unexpected key collisions.
- **Discoverability:** Registry tag-based search (e.g., filtering by `qa-testing` or `test-case-generation`) depends on correctly structured `metadata.tags`. Misplaced top-level `tags` may not be indexed by category/tag filters.
- **Portability:** Other teams importing this skill into their own registries will have clean, unambiguous frontmatter that passes validation on first parse.
- **Risk reduced:** Eliminates the risk of a strict YAML parser rejecting the entire frontmatter block due to unexpected top-level keys, which would cause the skill to fail to load entirely.

### Existing use (before fix)
Today, a strict frontmatter validator reading `test-case-generator` encounters `version: 1.0.0` at the top level immediately after `description`. The validator does not recognise `version` as a standard spec field at the top level and either throws a validation error (blocking skill registration) or silently drops all 8 non-standard keys. The `tags` list — which enables category filtering for `qa-testing`, `manual-testing`, and `security-testing` — is never indexed. Teams searching the registry by tag `api-testing` will not find this skill even though it explicitly covers API test cases.

### Improved use (after fix)
After nesting all 8 fields under `metadata:`, the frontmatter is clean and unambiguous. The top-level section contains only spec-recognised fields. Registry indexers correctly parse `metadata.tags` and make the skill discoverable via `qa-testing`, `manual-testing`, `api-testing`, and `security-testing` filters. The `metadata.author` and `metadata.email` fields are preserved for attribution. Validators pass the skill on first check, and the skill is correctly categorised in the `qa-testing` category across all registry tools.

---

## Improvement 4 — Bundle `scripts/gen_test_cases.py` Instead of Generating It at Runtime

### What needs to change
Step 6 instructs the agent to use the Write tool to create `gen_test_cases.py` at runtime, then immediately execute it. The spec requires bundled scripts to live in a `scripts/` subdirectory inside the skill folder. A pre-authored, bundled script removes runtime variability (the agent may generate slightly different script code each activation), improves reliability, and satisfies the spec's self-containment requirement. Step 6 must be updated to reference the bundled path.

### Before
```markdown
### Step 6: Generate Excel Output

Write a Python script using the Write tool and execute it using the Bash tool to produce a `.xlsx` file.

Excel requirements:
- Bold headers
- Wrapped text
- Auto-fit columns
- Freeze top row
- One test case per row
- Sequential TC IDs
- All 10 columns preserved

File naming format: `Test_Cases_<Sanitized_Feature_Name>.xlsx` (spaces → underscores, special characters removed).

Execute: `py "<absolute_path>/gen_test_cases.py"`
```
(No `scripts/gen_test_cases.py` file exists in the skill folder.)

### After
Create `skills/test-case-generator/scripts/gen_test_cases.py` with the full Excel generation logic pre-authored. Update Step 6 in SKILL.md to:

```markdown
### Step 6: Generate Excel Output

Execute the bundled script to produce a `.xlsx` file:

```bash
py "scripts/gen_test_cases.py"
```

The script (`scripts/gen_test_cases.py`) handles:
- Bold headers, wrapped text, auto-fit columns, frozen top row
- One test case per row with sequential TC IDs
- All 10 columns preserved
- File naming: `Test_Cases_<Sanitized_Feature_Name>.xlsx` (spaces → underscores, special characters removed)
- Output saved to `Testcases/` subfolder of `os.getcwd()`
```

### Impact if implemented
- **Agent behaviour:** The agent no longer needs to synthesise the Python script from scratch on every activation. It reads the consistent, pre-authored script from `scripts/gen_test_cases.py` and executes it directly, eliminating code generation variability between runs.
- **Discoverability:** No direct discoverability impact, but the skill's quality signal improves — reviewers and registry curators see a complete, self-contained skill folder with bundled assets.
- **Portability:** Teams cloning the skill repository get the script immediately without needing to activate the skill once first to generate it. The script is version-controlled alongside the skill definition.
- **Risk reduced:** Eliminates the failure mode where the agent generates syntactically incorrect Python (e.g., wrong openpyxl API calls, wrong column indexing) due to LLM variability, causing Step 6 to crash and leaving the user without an `.xlsx` file. Also prevents the script from being written to an unexpected working directory path when `<absolute_path>` is resolved inconsistently.

### Existing use (before fix)
Today, every time the skill is activated, the agent in Step 6 must invent the `gen_test_cases.py` script from scratch using the Write tool. Because this generation is LLM-driven, the script varies between activations — sometimes using correct `openpyxl` column-writing patterns, sometimes not. On one run, the agent may generate a script that correctly iterates over the test case list and writes all 10 columns. On another run, with a long context window from 50+ test cases generated in Step 4, the agent may produce a truncated or syntactically broken script. The user is left with a partially working Excel file or a Python traceback, with no easy way to debug the generated script.

### Improved use (after fix)
After adding `scripts/gen_test_cases.py` as a bundled, tested script, Step 6 becomes a deterministic execution step. The agent reads the pre-authored script path, passes the test case data to it (via a temp JSON file or inline arguments as designed in the script), and executes it. The output is always a correctly formatted `.xlsx` file with bold headers, frozen rows, and auto-fit columns — identical across every activation. QA engineers can open the file directly in Excel or upload it to Jira/TestRail without reformatting. The script is also independently testable and improvable without modifying SKILL.md.

---

## Improvement 5 — Embed Trigger Verb Phrases in the `description` Field

### What needs to change
The `description` field currently focuses entirely on the "what" of the skill (generate test cases from various input types) but contains no trigger verb phrases that an agent routing layer would match against natural language user requests. Trigger phrases like "generate test cases", "write QA coverage", and "create test cases for" appear only inside the body's "When to use" section — which loads after the frontmatter. For upfront agent routing that reads only `name` + `description`, this skill is harder to match than it should be.

### Before
```yaml
description: Generate exhaustive, production-ready QA test cases from user stories, acceptance criteria, BRDs, PRDs, or feature descriptions — covering all test types with zero critical gaps.
```

### After
```yaml
description: "Generate test cases, write QA coverage, or create test cases for any feature — produces exhaustive, production-ready test cases from user stories, acceptance criteria, BRDs, PRDs, or feature descriptions, covering all test types with zero critical gaps."
```

### Impact if implemented
- **Agent behaviour:** Routing agents that match user intent ("generate test cases for login", "create test cases for the payment flow") against skill descriptions will now match `test-case-generator` directly on the `description` field, without needing to load and parse the full skill body first.
- **Discoverability:** Significantly improves upfront discoverability. Natural language queries containing "generate test cases", "write QA coverage", or "create test cases for" will surface this skill in the first candidate pass.
- **Portability:** No portability impact, but improves the skill's reusability across different agent routing implementations that rely solely on `name` + `description` for initial matching.
- **Risk reduced:** Reduces the risk of the skill being overlooked in favour of a more generically described competitor skill when a user's phrasing matches a trigger verb phrase exactly.

### Existing use (before fix)
Today, a user types "create test cases for the user registration flow." An agent routing layer reads the `description` of `test-case-generator`: "Generate exhaustive, production-ready QA test cases from user stories..." The description starts with "Generate" (matching partially) but the trigger phrase "create test cases for" does not appear. A routing layer doing keyword or semantic match on descriptions may rank this skill lower than expected, or may fail to select it in favour of a more generically described testing skill. The user may receive no skill activation or a wrong skill.

### Improved use (after fix)
After updating the `description` to include "Generate test cases, write QA coverage, or create test cases for any feature", the routing layer matches all three primary trigger phrases directly from the description. User queries like "generate test cases for the checkout API", "write QA coverage for the admin dashboard", and "create test cases for file upload" all resolve to `test-case-generator` on the first routing pass, before the body is loaded. Activation is faster, more reliable, and consistent regardless of which trigger phrasing the user chooses.

---

## Priority Order

| Priority | Improvement | Effort | Impact |
|---|---|---|---|
| 1 | Add missing `license` field | Low | Critical |
| 2 | Add missing `compatibility` field | Low | Critical |
| 3 | Move non-standard fields under `metadata:` | Low | High |
| 4 | Bundle `scripts/gen_test_cases.py` | Medium | High |
| 5 | Embed trigger verb phrases in `description` | Low | Medium |

---

## Before vs After: Full Skill Experience

### Before (current state)

A QA engineer on a macOS machine discovers `test-case-generator` in a shared registry and activates it by typing "create test cases for the payment checkout feature." The routing layer reads the skill's `description` — "Generate exhaustive, production-ready QA test cases from user stories..." — and makes a tentative match, though "create test cases for" is not present in the description, so confidence is lower than ideal. The skill loads. The frontmatter validator flags the skill as non-compliant: no `license` field, no `compatibility` field, and 8 non-standard fields (`version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`) sitting at the top level instead of under `metadata:`. Depending on the validator's strictness, the skill may be skipped entirely or loaded with warnings.

If the skill does load, Steps 1-5 execute correctly — the agent generates a thorough Markdown table of 45 test cases covering positive, negative, boundary, security, and API categories. Then Step 6 runs. The agent synthesises `gen_test_cases.py` from scratch using the Write tool, writing it to a working directory path. On this particular run, with a long context window from the 45 test cases, the generated script has a subtle column-indexing error. The Bash tool executes `py gen_test_cases.py` — but `py` does not exist on macOS. The command fails with "command not found." The user has the Markdown table but no `.xlsx` file, no clear error explanation, and no way to know this skill was designed exclusively for Windows.

Meanwhile, a registry administrator searching by tag `qa-testing` does not find this skill because the `tags` field at the top level was silently dropped by the YAML parser. The skill is effectively invisible to category-based discovery despite being the most comprehensive QA test generation skill in the registry.

### After (all improvements applied)

The same QA engineer types "create test cases for the payment checkout feature." The routing layer reads the updated `description` — "Generate test cases, write QA coverage, or create test cases for any feature..." — and immediately matches with high confidence on the "create test cases for" phrase. The `compatibility` field is read next: "Requires Windows environment with Python accessible via the `py` command." The agent is running on macOS and detects the incompatibility before loading the body. It surfaces a clear, actionable message: "This skill requires a Windows environment. Please run it on a Windows machine with Python (`py`) and openpyxl 3.1.5 installed." No silent failure, no confusing mid-execution crash.

On a Windows machine, the same skill activates cleanly. The frontmatter validator reads `license: MIT`, `compatibility`, and a clean `metadata:` block with all 8 non-standard fields correctly nested. Validation passes on the first check. Steps 1-5 generate the full 45-test-case Markdown table. Step 6 references `scripts/gen_test_cases.py` — the pre-authored, version-controlled script. The agent executes `py "scripts/gen_test_cases.py"` directly. The script runs deterministically, writing `Testcases/Test_Cases_Payment_Checkout.xlsx` with bold headers, frozen top row, and auto-fit columns. The QA engineer opens the file, confirms all 45 rows are present with correct formatting, and uploads it directly to TestRail. No errors, no missing files, no surprises — exactly the experience the skill was designed to deliver.
