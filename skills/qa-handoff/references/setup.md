# First-time setup

Run through this once before your team's first use of the skill. Estimated time: 15–20 minutes.

---

## Step 1 — Install and authenticate the GitHub CLI

```bash
# Check if already installed
gh --version

# If not installed: https://cli.github.com/
# After installing, authenticate:
gh auth login
```

Verify it works:

```bash
gh api user --jq '.login'
# Should print your GitHub username — no error messages
```

If this fails, the skill cannot create issues, read PRs, or update project boards. Fix authentication before proceeding.

---

## Step 2 — Fill in the configuration placeholders

The skill uses angle-bracket placeholders throughout its files. Replace each one with the real value for your project. A global find-replace across the skill folder is the fastest approach (VS Code: `Ctrl+Shift+H`, scope to the skill folder).

| Placeholder | What it is | Where to find it |
|---|---|---|
| `<your-org>` | GitHub organisation name | The part before your repo in `github.com/<your-org>/<your-repo>` |
| `<your-repo>` | Repository name | The repo name after the org |
| `<dev-url>` | Dev environment URL | The URL your team uses to preview merged-but-unreleased changes (e.g. `dev.yourapp.com`) |
| `<prod-url>` | Production URL | Your live app URL (e.g. `yourapp.com`) |
| `<your-project-id>` | QA project board GraphQL ID | See "Finding project IDs" below |
| `<secondary-project-id>` | Auto-add project board GraphQL ID | See "Finding project IDs" below |
| `<your-status-field-id>` | The Status field ID on your QA board | See "Finding project IDs" below |
| `<ready-for-qa-option-id>` | The "Ready for QA" status option ID | See "Finding project IDs" below |

**Files that contain placeholders:**

- `SKILL.md` — Steps 0.5a, 0.5b, 6, 7c, 7d
- `references/project-board.md` — all GraphQL queries
- `references/report-templates.md` — example issue URLs
- `references/smoke-test.md` — example commands

### Finding project IDs

**List your organisation's projects:**

```bash
gh api graphql -f query='
query {
  organization(login: "<your-org>") {
    projectsV2(first: 20) {
      nodes { number title id }
    }
  }
}'
```

Find your QA project in the list. Its `id` (a long string starting with `PVT_`) is `<your-project-id>`. Find the auto-add project the same way.

**Get field IDs and status option IDs for your QA project:**

```bash
gh api graphql -f query='
query {
  organization(login: "<your-org>") {
    projectV2(number: <your-project-number>) {
      fields(first: 20) {
        nodes {
          ... on ProjectV2SingleSelectField {
            id
            name
            options { id name }
          }
        }
      }
    }
  }
}'
```

Look for the field named `Status`. Its `id` is `<your-status-field-id>`. Under `options`, find `Ready for QA` — its `id` is `<ready-for-qa-option-id>`.

---

## Step 3 — Update the URL mapping table

The file-path-to-URL mapping table in `SKILL.md` Step 5 is written for the TMS project's folder structure. Update it to match your project's routing conventions before using the skill.

The table maps paths like `src/app/(authenticated)/(app)/exams/page.tsx` → `https://<dev-url>/exams`. If your project uses a different folder structure, update each row to match your actual routes.

---

## Step 4 — Add test accounts reference

Test plans tell QA to "sign in as a premium user" or "sign in as an admin" — QA needs to know where to find those credentials. Store them in your team's password manager or a pinned wiki page, then add the link here:

```
Dev test accounts: <link-to-team-password-manager-or-wiki>
```

Update this once; every future QA handoff will reference this location.

---

## Step 5 — Add the gitignore entry

The skill saves the QA assignee's username to a local file (`.qa-assignee.local`). This file must never be committed to Git — it is per-user config, not project config.

Add this line to your project's root `.gitignore`:

```
**/.qa-assignee.local
```

Or run:

```bash
echo "**/.qa-assignee.local" >> .gitignore
git add .gitignore
git commit -m "chore: gitignore qa-handoff local assignee config"
```

---

## Step 6 — Verify the setup

**Test config mode (no side effects):**

```bash
/qa-handoff --qa qa-tester --set-default
```

Expected output:
```
✅ Config updated: default QA assignee set to @qa-tester
```

**Test a single PR in dry-run (no issue filed):**

```bash
/qa-handoff <recent-merged-PR-number> --dry-run
```

Review the generated file:

```bash
cat docs/qa-handoffs/PR-<N>.md
```

Check that:
- Modules are correct for the files changed
- "Where to test" shows real URLs (not `[the affected page(s)]`)
- No `<placeholder>` values remain in the body
- The header block shows correctly formatted dates (e.g. `16 May 2026`, not `2026-05-16T14:23:11Z`)

Clean up the dry-run file:

```bash
rm docs/qa-handoffs/PR-<N>.md
```

Once the dry-run output looks correct, you're ready to use the skill for real.

---

## Handling GitHub API slowness or rate limits

If `gh` commands hang or fail with a rate-limit error (`HTTP 403: rate limit exceeded`):

1. **Check your rate limit:** `gh api rate_limit --jq '.rate'`
2. **If limited:** wait until the `reset` timestamp and re-run.
3. **If a batch run fails mid-way:** the partial failures are listed in the Step 8 report. Re-run targeting only the failed PRs: `/qa-handoff <failed-PR-1> <failed-PR-2>`
4. **For persistent hangs:** add `--timeout 30` to the failing `gh` command and check your network connection to `api.github.com`.
