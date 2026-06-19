---
name: daily-status
description: Generate the end-of-day client status report by scanning today's git commits, uncommitted changes, and GitHub PRs, then interviewing the user to classify each item. Use whenever the user asks for their daily status, EOD report, or client update — or types /daily-status.
version: 1.3.0
author: Shilpa VP
email: shilpa@zysk.tech
category: comms
tags:
  - daily-status
  - eod-report
  - git
  - github
  - reporting
tested_with: claude-opus-4-7
---

<!-- ci: sample edit to exercise regenerate-index workflow -->
# Daily Status Report

> Generate the end-of-day client status report by scanning today's git activity and interviewing the user to classify and refine each item.

## When to use

- Activate when: the user types `/daily-status`
- Activate when: the user asks for their EOD report, daily status, or client update
- Activate when: the user says "send today's update" or "what should I send the client today"
- Do NOT activate when: the user wants a weekly / sprint summary, a standup transcript, or a retrospective — those are different artifacts with different formats

## Prerequisites

- [ ] A local config file at `~/.claude/skills/daily-status/config.local.json` (a template lives in `assets/config.example.json` — copy and edit it)
- [ ] Today's work is committed, or visible as uncommitted changes, in the configured repos
- [ ] (Optional) `gh` CLI authenticated — without it the skill runs in git-only mode

## Configuration

User-specific values live in a sidecar config file so the skill itself can be shared publicly without leaking names, signatures, or repo paths.

```
DEFAULT PATH = ~/.claude/skills/daily-status/config.local.json
ENV OVERRIDE = $DAILY_STATUS_CONFIG
```

Expected shape (see `assets/config.example.json` for a working sample):

**Single client:**
```json
{
  "project_name": "",
  "signature": "",
  "default_hours": 8,
  "product": "",
  "sprint": 1,
  "repo_paths": []
}
```

**Multiple clients:**
```json
{
  "clients": [
    {
      "project_name": "Client A",
      "signature": "Jane Doe",
      "default_hours": 8,
      "product": "Portal",
      "sprint": 3,
      "repo_paths": ["/path/to/client-a-repo"]
    },
    {
      "project_name": "Client B",
      "signature": "Jane Doe",
      "default_hours": 8,
      "product": "Store",
      "sprint": 5,
      "repo_paths": ["/path/to/client-b-repo"]
    }
  ]
}
```

**Before Step 1**, ensure the config exists and is populated:

- If the file does not exist, or any of `project_name` / `signature` / `repo_paths` is empty, prompt the user one question at a time, then write the file. Use `default_hours: 8` if not provided. Ask for `product` (enter once, never asked again) and `sprint` (enter once, checked each run).
- If the config has a `clients` array with more than one entry, ask: *"Which project are you reporting for today?"* and list the client names. Use the selected client's values for the rest of the flow.
- If the config has a `clients` array with only one entry, use it automatically without asking.
- **Sprint check (every run):** After resolving the active client, ask: *"Still on sprint <N>? (press Enter to keep / type new number to update)"*. If the user enters a new number, update `sprint` in `config.local.json` before continuing. This is the only field that gets a confirmation prompt on every run — all others are set once and reused silently.
- Never hardcode a project name, signature, product, sprint, or repo path in this skill file — they belong in `config.local.json` only.

The bundled `scripts/collect_activity.py` loads the same file, so once it's populated the rest of the flow is automatic.

## Steps

Follow these steps in order.

### Step 1 — Collect git activity

Run the bundled collector. Resolve the script's absolute path from the skill's own directory — do not use a relative path, since the user invokes this skill from their project repo, not the skill folder:

```bash
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SKILL_DIR/scripts/collect_activity.py" --pretty
```

It reads the config, runs `git log` / `git status` / `git diff` / `git branch` per repo in parallel, calls `gh pr list` when `gh` is authenticated, filters noise commits and noise files (`.DS_Store` etc.), and emits one JSON document covering every configured repo.

Why a script instead of inline bash: doing this in shell required ~5 commands per repo plus manual JSON stitching on every invocation. The script does it once, in parallel, with consistent filtering — so this skill stays focused on judgment (classify, summarize, interview) rather than orchestration.

If the script exits with a non-zero code, print the last line of stderr as the error reason, then ask: *"The activity collector failed — do you want to enter today's work manually instead?"* If yes, skip directly to Step 4's manual entry flow. If no, exit and suggest the user check their `config.local.json` and re-run.

If the script's `warnings` array reports `gh` unavailable, mention this to the user once and continue with git-only signals.

### Step 2 — Summarize into work items

Build the work item list from three signals in the collector output: `commits`, `uncommitted_files`, and `prs`.

- **From commits:** group multiple commits on the same branch / same PR into one item. Use the PR title if available, otherwise infer from commit subjects. The collector already drops noise commits (`wip`, `lint`, `merge`, `chore(deps)`, etc.), but keep generic `chore:` commits — they often describe real work (config, scripts, infra) the client cares about.
- **From PRs:** match PRs to commit groups by `headRefName` (branch name). If a branch matches an existing commit group, prefer the PR title as the item description (usually cleaner than inferring from commit messages) and do not double-add. PRs with no matching commit group become separate items.
- **From uncommitted changes:** see Step 2a below — this case needs more care, so it has its own recipe.

Truncate long titles to ~80 chars. Present the deduped list to the user before the interview, so they can see what was detected.

#### Step 2a — Describing uncommitted work

When a repo has staged or unstaged files, add **one item per branch** with a rich description built from the actual file list — *not* just the humanized branch name. Why this matters: branch names lie (a branch called `fix/email` might contain a whole new integration), and a vague description like "Email work" tells the client nothing. A descriptive item ("SendGrid integration — webhook controller, services layer, DB migrations") justifies the day's hours.

Recipe:

1. List the changed / new files (from `uncommitted_files`).
2. Identify the dominant theme. New files and new folders are the strongest signal — e.g. `app/Services/SendGrid/`, `SendGridWebhookController.php`, migrations named `*_sendgrid_*` → "SendGrid integration". Group related files by directory or naming pattern.
3. Mention the concrete components in parentheses, e.g. *"SendGrid implementation (webhook controller, services layer, PilotEmailDispatcher trait, DB migrations, integration into OTP/Pin/User controllers)"*.
4. If the changes are tiny and scattered (no clear theme), fall back to listing the touched areas: *"ACL trait + services config updates"*.
5. Avoid generic 1–2 word descriptions like *"SendGrid pilot"* or *"Explore"*. If nothing descriptive comes to mind, look again at `diff_stat` and `uncommitted_files` — there is almost always a concrete clause hiding in there.

Append a hint like `(uncommitted: 5 files)` for the interview prompt. Uncommitted items default to **In Progress** in Step 3 — they're not finished yet by definition.

### Step 3 — Interview per item

For each work item, ask:

```
[N/total] "<item description>"
  Bucket? [D]one / Done-but-[N]ot-tested / [I]n-progress / [S]kip:
  Refine description (Enter to keep):
```

For items derived from **uncommitted** changes, mark In Progress as the default in the prompt — pressing Enter accepts it. For items from commits or PRs there is no default; the user must pick a bucket.

Track answers. Skipped items are excluded entirely.

If zero items were detected, tell the user "no git activity found today" and fall through to Step 4 with manual entry: ask "What did you do today? (one item per line, blank line to finish)" and then ask the bucket for each entered item.

### Step 4 — Free-text extras

Ask these three questions **one at a time**, in order, waiting for each reply before moving on.

Why one at a time: when these are batched, users skim and drop the **Need Discussion** items, which are the most valuable part of the report — they surface the blockers and decisions the client owes you. Ask every question even if the previous answer was empty; *"no meetings today"* and *"no discussion points"* are still answers, and silently skipping a section creates ambiguity for the client.

1. **Meetings / non-code activities** — *"Any meetings or non-code activities today? (these go under Done — type 'skip' or 'no' if none)"*. Empty / "no" / "skip" → record none. Otherwise add each line to the **Done** section.
2. **Need Discussion points** — *"Any Need Discussion points? (one per line — say 'done' or 'skip' when finished)"*. Collect multi-line input until they signal done. Empty / "no" / "skip" / "none" → record none.
3. **Hours** — *"Hours spent today? (default: 8)"*. Empty / "default" → use 8.

Only after all three are answered, move to Step 5.

### Step 5 — Render the report

Render the report using the exact format in `assets/report-template.txt`. The placeholders (`<hours>`, `<PROJECT_NAME>`, `<bullets>`, `<SIGNATURE>`) map to the values gathered in Steps 3–4 and the config loaded in Step 1.

Two rules the template can't express on its own:

- **Omit empty sections entirely** — don't print a header followed by nothing. If no items landed in "Done (but not tested on staging)", the header doesn't appear.
- **Plain lines, no bullet markers** — items go on their own line under the section header without a leading `-` or `*`. The client's established format doesn't use them.

See `references/example-report.md` for a fully worked example.

After printing, tell the user: *"Report ready above — copy-paste into your email/Slack."*

## Output

- **Format:** plain-text status report rendered inline in the chat
- **Location:** appears as the assistant's final message; the user copy-pastes it into email or Slack
- **Sections:** `Time Spent`, `Today's Activities`, `Project`, `Done`, `Done (but not tested on staging)`, `In Progress`, `Need Discussion`, `Regards` — empty sections are omitted
- **Example:** see `references/example-report.md`

## Rules

- **Do not invent activities.** Only include what's in the collector output or what the user typed during the interview. The client trusts that this report reflects real work.
- **Do not edit the user's wording** beyond truncation. If they refine a description, use it verbatim — they know the project context better than the skill does.
- **Present as one project.** When multiple repos are configured, merge their results into a single list — do not group by repo in the output. The client sees one project, not the internal repo layout.
- **One question at a time** during the interview, for the reason described in Step 4.
- **Never auto-send** the report — the user typically tweaks wording before it goes to the client, so always require a manual copy.

## Example

**User says:** `/daily-status`

**Claude does:** Loads config, runs `scripts/collect_activity.py`, presents the detected work items, asks the user to classify each one, then asks three short follow-up questions (meetings, discussion points, hours), and finally renders the formatted report.

**Result:** see `references/example-report.md` for the full worked output.

## Files in this skill

- `SKILL.md` — this file
- `scripts/collect_activity.py` — runs all git + GitHub queries in parallel and emits structured JSON
- `assets/report-template.txt` — the exact output format the report follows
- `assets/config.example.json` — template the user copies to `~/.claude/skills/daily-status/config.local.json`
- `references/example-report.md` — fully worked example of a finished report

## Notes

- The collector script honors `$DAILY_STATUS_CONFIG` if you keep the config somewhere other than the default home path.
- `gh` CLI auth is optional — without it the script sets `gh_available: false` and the skill runs git-only.
- The output format is fixed because it goes to the client. Don't reformat section headers or add bullet markers.
