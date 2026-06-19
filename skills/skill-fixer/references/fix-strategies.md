# Fix Strategies

How to remediate each finding type skill-reviewer can emit. The script handles the
"auto" rows; this is for the "draft" rows you fix by hand, plus what to tell the
user for "human" rows. Always read the file before editing it.

## Contents

- [Auto (script already did these)](#auto)
- [Draft (you fix on the branch)](#draft)
- [Human-required (never auto-fix)](#human-required)

## Auto

- **reference_toc** - script inserts a `## Contents` list built from the file's
  `##`/`###` headings, after the H1. Verify the anchors look right.
- **name_matches_folder** - script sets the frontmatter `name` to the folder name
  (the folder is the install location, so it is the safer side to keep). If the
  name was the intended one, rename the folder instead and revert the field.

## Draft

- **trigger_cues** (MAJOR) - the description has no "when to use" signal. Rewrite it
  to state both what the skill does and when to invoke it, including casual
  phrasings a user might type. This is the highest-leverage triggering fix.
- **description_detail** (MINOR) - description too short to trigger reliably. Expand
  with concrete tasks and trigger contexts.
- **description_length / name_length / compatibility_length** - over the limit. Trim
  to the cap (description 1024, name 64, compatibility 500 chars) without losing the
  trigger cues.
- **description_no_brackets** - remove `<`/`>` from the description (reword, e.g.
  "a SKILL.md folder" instead of angle-bracket placeholders).
- **name_format** - make the name kebab-case: lowercase, digits, single hyphens, no
  leading/trailing hyphen.
- **name_collision** (MAJOR) - the name shadows a bundled skill (pdf, docx, etc.).
  Rename to something distinct and update the folder to match. Confirm the new name
  with the user if the skill is already installed somewhere.
- **script_compile** (MAJOR) - a bundled script does not parse. Read it, fix the
  syntax error, and re-check it compiles (`python3 -m py_compile <file>`).
- **body_size** (MAJOR) - SKILL.md body too long. Move detailed sections into
  `references/<topic>.md` and leave a one-line pointer, preserving the workflow.
- **undisclosed_dependency** (MINOR) - a script imports a third-party package not
  declared anywhere. Either remove the dependency (prefer stdlib) or declare it: add
  a `requirements.txt`, or note it in the `compatibility` field. Explain the why.
- **dangling_reference** (MINOR) - SKILL.md points to a `scripts/`/`references/`
  file that does not exist. Decide with care: if the referenced file was meant to
  exist, create it (or a clear stub); if the reference is stale, remove it. Do not
  invent substantive content silently - if unsure, leave a TODO and tell the user.
- **single_skill_md** (BLOCKER, but fixable) - more than one SKILL.md. Rename the
  non-root ones to descriptive names under `references/`, and update any links.
- **allowed_keys** (BLOCKER) - an unexpected frontmatter key. Remove it or move it
  under `metadata`.
- **directive_style** (MINOR) - heavy ALWAYS/NEVER/MUST. Rewrite the strongest ones
  as guidance that explains the reason; keep hard rules only where they are truly
  hard.
- **body_tokens** (MAJOR) - body is light on lines but heavy on tokens (a few very
  long lines). Same fix as body_size: move detail into `references/` and tighten the
  prose so the always-loaded body stays cheap.
- **instruction:structure / progressive-disclosure** (MAJOR/MINOR) - an
  instruction-review finding from the reviewer's *Structure / progressive disclosure*
  lens (`dimension: structure`). Two directions, per the finding's `Fix:`: (a)
  reference-worthy detail - long tables, exhaustive option lists, worked examples,
  edge-case catalogues - move it into `references/<topic>.md` and leave a one-line
  pointer, preserving the workflow (same recipe as body_size); (b) a deterministic,
  repeated procedure the body asks the model to reconstruct each run - extract it into
  a `scripts/` helper, reference it from SKILL.md with when-to-run guidance, and verify
  it compiles (`python3 -m py_compile <file>`). Only relocate what the reviewer
  confirmed is movable: if it is all-essential procedure that must stay inline to steer
  the model, leave it and note the finding as not applied rather than gutting the body.
- **empty_body** (MAJOR) - SKILL.md has frontmatter but no body. Write the actual
  procedure - inputs, workflow steps, a worked example. The body is the on-trigger
  instruction, so an empty one is the whole skill missing.
- **thin_body** (MINOR) - body is only a line or two. Flesh out the workflow and add
  an example so the model has enough to act on.
- **orphaned_script** (MINOR) - a `scripts/` file is bundled but never referenced in
  any doc. Either reference it from SKILL.md with when-to-run guidance, or remove it
  if it is dead weight. Confirm with the user before deleting anything substantive.
- **allowed_tools_type / metadata_type** (MAJOR) - a frontmatter key has the wrong
  shape. Make `allowed-tools` a list of tool-name strings (or a comma-separated
  string); make `metadata` a key/value mapping.
- **frontmatter_parser** (MINOR) - PyYAML was not installed during the review, so
  structured keys went unvalidated. This is an environment note, not a skill defect:
  record it (suggest installing PyYAML and re-reviewing) - no file edit resolves it.
- **instruction:*** (MAJOR/MINOR) - an LLM-judge instruction finding folded in from
  the reviewer: a gap, contradiction, ambiguity, misdirection, or unspecified output.
  The `message` names the problem, where it is, and a **Fix:** - apply that fix on the
  branch. These are mandatory (the skill is not production-grade until they clear).
  Read the cited section/step first, and re-judge after editing to confirm the
  instruction now reads cleanly and consistently with the rest of the skill.

## Human-required

- **secret:*** (BLOCKER) - a hardcoded credential. Do NOT edit and claim fixed. Tell
  the user the exact file:line, that the credential is compromised the moment it was
  committed, and that they must remove it from the code, move it to an environment
  variable or secret store, and rotate the key. Removing it from the latest commit
  does not purge git history - mention they may need history rewriting too.
- **scan:*** (REVIEW) - an unconfirmed network/exec/destructive pattern. Judge it
  against the skill's stated purpose. If it is legitimate, note it as accepted in
  your report (no code change). If you confirm it is malicious or undisclosed, stop
  and escalate to the user; do not quietly rewrite it.
- **prose:*** (REVIEW) - an instruction in SKILL.md or a reference that would
  surprise a reader of the description: pipe-to-shell, exfiltration phrasing, a
  hardcoded IP, or an encoded blob. Judge it like a `scan:` flag. If legitimate, note
  it as accepted; if it is a genuine exfiltration or backdoor instruction, stop and
  escalate. Do not quietly delete the line and call it fixed.
- **binary_artifact** (REVIEW) - the skill ships an opaque/executable file whose
  contents can't be reviewed as text. Ask the user why it is bundled; a text edit
  can't make it safe. Remove it only with their confirmation.
