#!/usr/bin/env python3
"""
fetch_review_queue.py — Fetch open PRs where the current user is a requested reviewer.

Usage:
    python3 fetch_review_queue.py [--repo ORG/REPO] [--pretty]

Auto-detects repo from the current git remote if not provided.

Output: JSON with current user login, repo, and an array of PRs with their
full state (CI, review decision, unresolved threads, latest Claude comment).
"""

import argparse
import json
import subprocess
import sys

PR_VIEW_FIELDS = (
    "number,title,url,author,isDraft,headRefName,updatedAt,"
    "additions,deletions,changedFiles,body,"
    "mergeStateStatus,reviewDecision,statusCheckRollup,"
    "closingIssuesReferences,reviewThreads,comments,reviews"
)


def run(cmd, capture=True):
    result = subprocess.run(cmd, shell=True, capture_output=capture, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"Command failed: {cmd}")
    return result.stdout.strip() if capture else None


def resolve_repo():
    try:
        return run("gh repo view --json owner,name --jq '\"\\(.owner.login)/\\(.name)\"'").strip('"')
    except RuntimeError:
        return None


def resolve_login():
    try:
        return run("gh api user --jq '.login'")
    except RuntimeError:
        return None


def fetch_prs(repo, me):
    try:
        raw = run(
            f'gh search prs --repo "{repo}" --state open --review-requested "@me" '
            f'--json number,title,author,isDraft,updatedAt,url'
        )
        prs = json.loads(raw)
    except (RuntimeError, json.JSONDecodeError) as e:
        raise RuntimeError(f"Failed to search PRs: {e}")

    # Drop drafts and own PRs (defense-in-depth)
    return [p for p in prs if not p.get("isDraft") and p.get("author", {}).get("login") != me]


def fetch_pr_detail(repo, number, me):
    cmd = (
        f'gh pr view {number} --repo "{repo}" '
        f'--json {PR_VIEW_FIELDS}'
    )
    try:
        raw = run(cmd)
        pr = json.loads(raw)
    except (RuntimeError, json.JSONDecodeError) as e:
        return {"number": number, "error": str(e)}

    # CI state
    checks = pr.get("statusCheckRollup") or []
    ci_failing = any(
        c.get("conclusion") in ("FAILURE", "CANCELLED") for c in checks
    )
    ci_running = any(
        c.get("status") in ("IN_PROGRESS", "QUEUED") for c in checks
    )

    # Unresolved review threads
    threads = pr.get("reviewThreads", {}).get("nodes") or []
    unresolved_threads = sum(1 for t in threads if not t.get("isResolved"))

    # Whether current user already submitted a review
    reviews = pr.get("reviews", {})
    if isinstance(reviews, dict):
        review_nodes = reviews.get("nodes") or []
    else:
        review_nodes = reviews or []
    you_already_reviewed = any(
        r.get("author", {}).get("login") == me for r in review_nodes
    )

    # Latest Claude auto-review comment
    comments = pr.get("comments", {})
    if isinstance(comments, dict):
        comment_nodes = comments.get("nodes") or []
    else:
        comment_nodes = comments or []
    claude_comments = [
        c for c in comment_nodes
        if c.get("author", {}).get("login") == "claude"
    ]
    latest_claude_comment = (
        sorted(claude_comments, key=lambda c: c.get("createdAt", ""))[-1].get("body")
        if claude_comments else None
    )

    # Closing issues
    closing = pr.get("closingIssuesReferences", {})
    if isinstance(closing, dict):
        closing_nodes = closing.get("nodes") or []
    else:
        closing_nodes = []
    closes = [i.get("number") for i in closing_nodes if i.get("number")]

    return {
        "number":               pr.get("number"),
        "title":                pr.get("title"),
        "url":                  pr.get("url"),
        "author":               pr.get("author", {}).get("login"),
        "branch":               pr.get("headRefName"),
        "updatedAt":            pr.get("updatedAt"),
        "additions":            pr.get("additions"),
        "deletions":            pr.get("deletions"),
        "changedFiles":         pr.get("changedFiles"),
        "body":                 pr.get("body", ""),
        "state":                pr.get("state", "OPEN"),
        "isDraft":              pr.get("isDraft", False),
        "mergeStateStatus":     pr.get("mergeStateStatus"),
        "reviewDecision":       pr.get("reviewDecision"),
        "ciFailing":            ci_failing,
        "ciRunning":            ci_running,
        "unresolvedThreads":    unresolved_threads,
        "youAlreadyReviewed":   you_already_reviewed,
        "latestClaudeComment":  latest_claude_comment,
        "closes":               closes,
    }


def main():
    parser = argparse.ArgumentParser(description="Fetch PRs awaiting your review")
    parser.add_argument("--repo",   help="GitHub org/repo (auto-detected from git remote if omitted)")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    args = parser.parse_args()

    repo = args.repo or resolve_repo()
    if not repo:
        print("ERROR: Could not detect repo from git remote. Pass --repo org/repo explicitly.", file=sys.stderr)
        sys.exit(1)

    me = resolve_login()
    if not me:
        print("ERROR: Could not resolve GitHub login. Run `gh auth login` first.", file=sys.stderr)
        sys.exit(1)

    try:
        prs = fetch_prs(repo, me)
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    details = []
    for pr in prs:
        details.append(fetch_pr_detail(repo, pr["number"], me))

    output = {
        "repo":    repo,
        "me":      me,
        "count":   len(details),
        "prs":     details,
    }

    indent = 2 if args.pretty else None
    print(json.dumps(output, indent=indent))


if __name__ == "__main__":
    main()
