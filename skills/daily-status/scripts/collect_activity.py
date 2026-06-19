#!/usr/bin/env python3
"""
daily-status / collect_activity.py

Collects today's git + GitHub PR activity across all configured repos and
emits one structured JSON document on stdout.

Why this exists:
  The daily-status skill previously had Claude shell out 4–5 times per repo
  (git log, git status, git diff, git branch, gh pr list) and stitch the
  results together by hand. That was slow, fragile, and reinvented the same
  filtering logic on every run. This script does it once, in parallel, and
  hands Claude a clean payload to reason over.

Config:
  Reads ~/.claude/skills/daily-status/config.local.json (path overridable
  via $DAILY_STATUS_CONFIG). Expected keys:
    project_name   (str)
    signature      (str)
    default_hours  (int, default 8)
    repo_paths     (list[str])

Output:
  {
    "config":  { ...as loaded... },
    "today":   "YYYY-MM-DD",
    "gh_available": bool,
    "repos": [
      {
        "path": "/abs/path/to/repo",
        "branch": "feature/x",
        "commits": [
          {"sha": "abc1234", "subject": "...", "refs": "HEAD -> ..."}
        ],
        "uncommitted_files": ["M  app/Foo.php", "?? new/file.py"],
        "diff_stat": " app/Foo.php | 12 +-\n 1 file changed, 12 insertions(+)",
        "prs": [
          {"number": 42, "title": "...", "state": "OPEN",
           "url": "...", "headRefName": "feature/x"}
        ],
        "errors": []
      }
    ],
    "warnings": ["..."]
  }

Usage:
  python3 collect_activity.py             # emits JSON to stdout
  python3 collect_activity.py --pretty    # human-readable JSON
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

CONFIG_PATH = Path(
    os.environ.get(
        "DAILY_STATUS_CONFIG",
        Path.home() / ".claude" / "skills" / "daily-status" / "config.local.json",
    )
)

# Commit subjects matching this regex are dropped as noise. Keep generic
# `chore:` commits — they often describe real work (infra, scripts, config)
# the client cares about. Only the explicit dependency-bump form is dropped.
NOISE_COMMIT_RE = re.compile(
    r"^(wip\b|fix typo|lint\b|format\b|merge\b|chore\(deps\))",
    re.IGNORECASE,
)

# File entries to drop from the uncommitted list — pure noise, never
# meaningful for a status report.
NOISE_FILE_RE = re.compile(r"(^|/)(\.DS_Store|Thumbs\.db|\.idea/|\.vscode/)")


def run(cmd: list[str], cwd: Path, timeout: int = 15) -> tuple[int, str, str]:
    """Run a command, capturing stdout/stderr. Never raises on non-zero exit."""
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd),
            capture_output=True,
            text=True, encoding="utf-8", errors="replace",
            timeout=timeout,
            check=False,
        )
        return proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        return 124, "", f"timeout after {timeout}s: {' '.join(cmd)}"
    except FileNotFoundError as e:
        return 127, "", str(e)


def gh_available() -> bool:
    if shutil.which("gh") is None:
        return False
    code, _, _ = run(["gh", "auth", "status"], cwd=Path.cwd(), timeout=5)
    return code == 0


def collect_repo(repo_path: str, today_iso: str, use_gh: bool) -> dict:
    repo = Path(repo_path).expanduser()
    result: dict = {
        "path": str(repo),
        "branch": None,
        "commits": [],
        "uncommitted_files": [],
        "diff_stat": "",
        "prs": [],
        "errors": [],
    }

    if not repo.is_dir() or not (repo / ".git").exists():
        result["errors"].append(f"not a git repo: {repo}")
        return result

    # Author email (used to scope `git log` to the current user's commits)
    code, email, _ = run(["git", "config", "user.email"], cwd=repo)
    author_email = email.strip()

    # Current branch
    code, branch, err = run(["git", "branch", "--show-current"], cwd=repo)
    result["branch"] = branch.strip() or None

    # Today's commits (current user only, no merges)
    log_cmd = [
        "git", "log", "--since=midnight",
        f"--author={author_email}" if author_email else "--author=.",
        "--pretty=format:%H|%s|%D",
        "--no-merges",
    ]
    code, out, err = run(log_cmd, cwd=repo)
    if code == 0:
        for line in out.splitlines():
            if not line.strip():
                continue
            parts = line.split("|", 2)
            if len(parts) < 2:
                continue
            sha, subject = parts[0], parts[1]
            refs = parts[2] if len(parts) > 2 else ""
            if NOISE_COMMIT_RE.match(subject):
                continue
            result["commits"].append(
                {"sha": sha[:7], "subject": subject, "refs": refs}
            )
    else:
        result["errors"].append(f"git log failed: {err.strip()}")

    # Uncommitted (status + diff stat vs HEAD)
    code, status_out, err = run(["git", "status", "--short"], cwd=repo)
    if code == 0:
        for line in status_out.splitlines():
            if not line.strip():
                continue
            # status --short lines are "XY path"; the path starts at col 3
            path_part = line[3:] if len(line) > 3 else line
            if NOISE_FILE_RE.search(path_part):
                continue
            result["uncommitted_files"].append(line)
    else:
        result["errors"].append(f"git status failed: {err.strip()}")

    code, diff_out, err = run(["git", "diff", "HEAD", "--stat"], cwd=repo)
    if code == 0:
        result["diff_stat"] = diff_out.strip()
    # diff against HEAD can fail on a fresh repo with no commits — not fatal

    # PRs updated today (only if gh is auth'd)
    if use_gh:
        pr_cmd = [
            "gh", "pr", "list",
            "--author", "@me",
            "--state", "all",
            "--search", f"updated:>={today_iso}",
            "--json", "number,title,state,url,headRefName",
        ]
        code, pr_out, err = run(pr_cmd, cwd=repo, timeout=30)
        if code == 0 and pr_out.strip():
            try:
                result["prs"] = json.loads(pr_out)
            except json.JSONDecodeError as e:
                result["errors"].append(f"gh pr list JSON parse failed: {e}")
        elif code != 0:
            result["errors"].append(f"gh pr list failed: {err.strip()}")

    return result


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        return {}
    try:
        with CONFIG_PATH.open() as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"warning: failed to read {CONFIG_PATH}: {e}", file=sys.stderr)
        return {}


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    args = parser.parse_args()

    config = load_config()
    repo_paths = config.get("repo_paths") or []
    warnings: list[str] = []

    if not repo_paths:
        warnings.append(
            f"no repo_paths configured in {CONFIG_PATH} — "
            "the skill should prompt the user to populate it"
        )

    use_gh = gh_available()
    if not use_gh:
        warnings.append("gh CLI unavailable or not authenticated — running git-only")

    today_iso = date.today().isoformat()

    repos: list[dict] = []
    if repo_paths:
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(8, len(repo_paths))) as pool:
            futures = {
                pool.submit(collect_repo, p, today_iso, use_gh): p for p in repo_paths
            }
            for fut in concurrent.futures.as_completed(futures):
                repos.append(fut.result())

    payload = {
        "config": config,
        "today": today_iso,
        "gh_available": use_gh,
        "repos": repos,
        "warnings": warnings,
    }

    if args.pretty:
        json.dump(payload, sys.stdout, indent=2)
    else:
        json.dump(payload, sys.stdout)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
