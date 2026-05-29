#!/usr/bin/env python3
"""
prepare_fixes.py - Set up a remediation branch from a skill-reviewer report.

Reads the JSON report produced by skill-reviewer's review_skill.py, classifies
each finding into auto / draft / human, creates an isolated git branch, applies
the deterministic auto-fixes, and writes a manifest telling the caller (Claude)
what to fix by hand and what to escalate to the user.

Safety boundaries (held regardless of caller instructions):
  - Secrets are NEVER auto-edited. A hardcoded credential cannot be rotated by a
    text edit; silently rewriting it would falsely imply the leak is resolved.
    Secrets go in the 'human' bucket only.
  - Unconfirmed security flags (any REVIEW finding: scan:, prose:, binary
    artifacts) also go to 'human' - never silently rewritten. The reviewer's ADVICE
    rows are non-authoritative pointers, not findings, and are not fixed here; the
    substantive instruction-quality findings arrive as Major/Minor.
  - Only operates on a clean git working tree, and only by creating a NEW branch
    off the current HEAD. It never commits to the existing branch, never pushes,
    never force-anything, never deletes.

Dependencies: standard library only. PyYAML used if present, else a tiny parser.

Usage:
    python3 prepare_fixes.py --report <review.json> --skill <skill-folder> \
        [--branch-prefix skill-fix] [--no-branch] [--json OUTFILE]
"""

import argparse
import datetime
import json
import re
import subprocess
import sys
from pathlib import Path

# Disposition of finding types. Routing happens in classify() by prefix/severity:
# secrets and any REVIEW / scan: / prose: flag go to "human" (unrotatable or
# unconfirmed); INFO and ADVICE are skipped; everything else defaults to "draft"
# (Claude attempts the fix). AUTO lists the deterministic fixes the script applies.
AUTO = {"reference_toc", "name_matches_folder", "allowed_keys"}
HUMAN = set()  # extra checks to force human; secrets/REVIEW already routed in classify()
# Reference list of fixable defects. Not used by classify() (the else-branch catches
# them) - kept as documentation of what "draft" covers.
DRAFT_KNOWN = {
    "trigger_cues", "description_detail", "script_compile", "body_size",
    "body_tokens", "empty_body", "thin_body", "orphaned_script",
    "name_collision", "undisclosed_dependency", "dangling_reference",
    "compatibility_length", "description_length", "name_length",
    "directive_style", "single_skill_md",
    "name_format", "description_no_brackets",
    "allowed_tools_type", "metadata_type",
}


def classify(findings):
    buckets = {"auto": [], "draft": [], "human": []}
    for f in findings:
        check = f.get("check", "")
        sev = f.get("severity", "")
        # INFO is informational; ADVICE is a non-authoritative reviewer pointer (a
        # lead, not a finding). Neither is a fix target - skip first, so an INFO
        # summary (e.g. prose:external_hosts) isn't mistaken for a human action.
        if sev in ("INFO", "ADVICE"):
            continue
        # Secrets can't be fixed by a text edit (they must be rotated): always human.
        if check.startswith("secret:"):
            buckets["human"].append(f)
        # Unconfirmed flags the reviewer wants a human to judge: any REVIEW finding
        # (scan:, prose:, binary_artifact, ...) - never silently rewrite a security
        # question. The prefix check keeps this true even if such a flag is escalated.
        elif sev == "REVIEW" or check.startswith(("scan:", "prose:")):
            buckets["human"].append(f)
        elif check in AUTO:
            buckets["auto"].append(f)
        elif check in HUMAN:
            buckets["human"].append(f)
        else:
            buckets["draft"].append(f)
    return buckets


# ---- git helpers ------------------------------------------------------------
def git(args, cwd):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)


def repo_root(path):
    r = git(["rev-parse", "--show-toplevel"], path)
    return Path(r.stdout.strip()) if r.returncode == 0 else None


def working_tree_clean(root):
    # Review/fix artifacts live in .skill-review/ (see SKILL.md). They are throwaway
    # analysis output, not a reason to refuse to branch, so ignore any status line
    # pointing into that folder when judging cleanliness.
    r = git(["status", "--porcelain"], root)
    if r.returncode != 0:
        return False
    for line in r.stdout.splitlines():
        path = line[3:].strip().strip('"')  # strip the XY status prefix
        path = path.split(" -> ")[-1]        # rename: keep the destination path
        if path == ".skill-review" or path.startswith(".skill-review/"):
            continue
        if path.strip():
            return False
    return True


def current_branch(root):
    r = git(["rev-parse", "--abbrev-ref", "HEAD"], root)
    return r.stdout.strip() if r.returncode == 0 else "?"


def make_branch(root, name):
    return git(["checkout", "-b", name], root)


def commit_all(root, message):
    git(["add", "-A"], root)
    return git(["commit", "-m", message], root)


def stash_artifacts(root):
    """Park the .skill-review/ artifact folder out of the working tree for the branch
    setup. It is throwaway review/fix output, but if it is present and not ignored it
    would otherwise block the checkout or be swept into the deterministic-fix commit by
    `git add -A`. Stash only that path (with untracked) so it survives the branch+commit
    and can be popped straight back. Returns True if anything was stashed."""
    status = git(["status", "--porcelain", "--", ".skill-review"], root)
    if status.returncode != 0 or not status.stdout.strip():
        return False  # nothing there, or it is gitignored (then add -A won't touch it)
    r = git(["stash", "push", "-u", "-m", "skill-fix: park .skill-review artifacts",
             "--", ".skill-review"], root)
    return r.returncode == 0


def pop_artifacts(root):
    """Restore artifacts parked by stash_artifacts so report.md / findings.json are
    available again after the branch is set up."""
    return git(["stash", "pop"], root)


# ---- frontmatter (for name sync) -------------------------------------------
def read_frontmatter(skill_md):
    content = skill_md.read_text(encoding="utf-8", errors="replace")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", content, re.DOTALL)
    if not m:
        return None, None, content
    return m.group(1), m.group(2), content


# ---- deterministic auto-fixes ----------------------------------------------
def fix_name_matches_folder(skill_path, applied):
    skill_md = skill_path / "SKILL.md"
    fm_text, body, content = read_frontmatter(skill_md)
    if fm_text is None:
        return
    folder = skill_path.name
    new_fm, n = re.subn(r"(?m)^(name:\s*).*$", lambda mm: mm.group(1) + folder, fm_text)
    if n and new_fm != fm_text:
        skill_md.write_text(f"---\n{new_fm}\n---\n{body}", encoding="utf-8")
        applied.append(f"Synced SKILL.md 'name' to folder '{folder}'.")


def build_toc(lines):
    """Build a markdown TOC from ## / ### headings (skip the H1 title)."""
    entries = []
    for ln in lines:
        m = re.match(r"^(#{2,3})\s+(.*)$", ln)
        if not m:
            continue
        level = len(m.group(1)) - 2
        title = m.group(2).strip()
        anchor = re.sub(r"[^a-z0-9\s-]", "", title.lower()).replace(" ", "-")
        entries.append(("  " * level) + f"- [{title}](#{anchor})")
    return entries


def fix_allowed_keys(skill_path, applied):
    """Move non-standard frontmatter keys to the metadata object."""
    skill_md = skill_path / "SKILL.md"
    content = skill_md.read_text(encoding="utf-8", errors="replace")

    # Parse frontmatter using regex (same approach as read_frontmatter)
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", content, re.DOTALL)
    if not m:
        return  # No frontmatter found

    fm_text = m.group(1)
    body = m.group(2)

    # Parse YAML frontmatter
    try:
        import yaml
        fm_data = yaml.safe_load(fm_text) or {}
    except ImportError:
        # Fallback: simple YAML parser for common cases
        fm_data = {}
        for line in fm_text.splitlines():
            if ":" in line and not line.strip().startswith("#"):
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()
                # Handle simple lists and values
                if value.startswith("- "):
                    value = [v.strip().lstrip("- ") for v in value.split("-") if v.strip()]
                fm_data[key] = value
    except Exception:
        return  # Skip if parsing fails

    # Allowed frontmatter keys per Agent Skill spec
    ALLOWED_KEYS = {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}

    # Separate standard keys from non-standard keys
    standard_keys = {k: v for k, v in fm_data.items() if k in ALLOWED_KEYS}
    non_standard_keys = {k: v for k, v in fm_data.items() if k not in ALLOWED_KEYS}

    if not non_standard_keys:
        return  # Nothing to fix

    # Move non-standard keys to metadata
    if "metadata" in standard_keys:
        if isinstance(standard_keys["metadata"], dict):
            # Merge with existing metadata
            standard_keys["metadata"].update(non_standard_keys)
        else:
            # Replace existing metadata with dict containing old + new
            existing = standard_keys["metadata"]
            standard_keys["metadata"] = non_standard_keys
            standard_keys["metadata"]["_existing_value"] = existing
    else:
        standard_keys["metadata"] = non_standard_keys

    # Write back the fixed frontmatter
    try:
        import yaml
        new_fm_text = yaml.dump(standard_keys, default_flow_style=False, sort_keys=False)
    except ImportError:
        # Fallback: simple YAML generator
        lines = []
        for key, value in standard_keys.items():
            if isinstance(value, dict):
                lines.append(f"{key}:")
                for k, v in value.items():
                    if isinstance(v, list):
                        lines.append(f"  {k}:")
                        for item in v:
                            lines.append(f"    - {item}")
                    else:
                        lines.append(f"  {k}: {v}")
            elif isinstance(value, list):
                lines.append(f"{key}:")
                for item in value:
                    lines.append(f"  - {item}")
            else:
                lines.append(f"{key}: {value}")
        new_fm_text = "\n".join(lines)

    skill_md.write_text(f"---\n{new_fm_text}\n---\n{body}", encoding="utf-8")

    # List what was moved
    moved_keys = ", ".join(sorted(non_standard_keys.keys()))
    applied.append(f"Moved non-standard frontmatter keys to metadata: {moved_keys}.")


def fix_reference_toc(skill_path, finding, applied):
    # finding message starts with "<relpath> is N lines ..."
    msg = finding.get("message", "")
    m = re.match(r"^([^\s]+)\s+is\s+\d+\s+lines", msg)
    if not m:
        return
    target = skill_path / m.group(1)
    if not target.exists():
        return
    lines = target.read_text(encoding="utf-8", errors="replace").splitlines()
    toc = build_toc(lines)
    if not toc:
        return
    # Insert after the first H1 (or at top if none).
    insert_at = 0
    for i, ln in enumerate(lines):
        if ln.startswith("# "):
            insert_at = i + 1
            break
    block = ["", "## Contents", "", *toc, ""]
    new_lines = lines[:insert_at] + block + lines[insert_at:]
    target.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    applied.append(f"Inserted a Contents TOC into {m.group(1)}.")


def apply_auto(skill_path, auto_findings):
    applied = []
    for f in auto_findings:
        if f["check"] == "name_matches_folder":
            fix_name_matches_folder(skill_path, applied)
        elif f["check"] == "allowed_keys":
            fix_allowed_keys(skill_path, applied)
        elif f["check"] == "reference_toc":
            fix_reference_toc(skill_path, f, applied)
    return applied


# ---- orchestration ----------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Prepare a fix branch from a review report.")
    ap.add_argument("--report", required=True, help="skill-reviewer JSON report")
    ap.add_argument("--skill", required=True, help="Path to the skill folder to fix")
    ap.add_argument("--branch-prefix", default="skill-fix")
    ap.add_argument("--no-branch", action="store_true", help="Skip git branch creation")
    ap.add_argument("--json", dest="json_out", help="Write the manifest as JSON")
    args = ap.parse_args()

    skill_path = Path(args.skill).resolve()
    if not (skill_path / "SKILL.md").exists():
        print(f"Error: no SKILL.md at {skill_path}", file=sys.stderr)
        sys.exit(1)
    try:
        report = json.loads(Path(args.report).read_text())
    except Exception as e:  # noqa: BLE001
        print(f"Error reading report: {e}", file=sys.stderr)
        sys.exit(1)

    findings = report.get("findings", [])
    buckets = classify(findings)

    # --- git branch setup ---
    branch = None
    stashed = False
    root = None
    git_note = "branch creation skipped (--no-branch)"
    if not args.no_branch:
        root = repo_root(skill_path)
        if root is None:
            git_note = ("NOT a git repo - no branch created. Initialize git or run "
                        "with --no-branch, then commit manually.")
        elif not working_tree_clean(root):
            git_note = (f"working tree at {root} is DIRTY - refusing to branch. "
                        "Commit or stash your changes first, then re-run.")
        else:
            # Park the artifact folder so it can't block the checkout or be captured
            # by the auto-fix commit; popped back after branch setup below.
            stashed = stash_artifacts(root)
            ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            origin_branch = current_branch(root)
            branch = f"{args.branch_prefix}/{skill_path.name}-{ts}"
            r = make_branch(root, branch)
            if r.returncode != 0:
                git_note = f"failed to create branch: {r.stderr.strip()}"
                branch = None
            else:
                git_note = f"created branch '{branch}' off '{origin_branch}' at {root}"
                if stashed:
                    git_note += " (parked .skill-review/ artifacts during setup)"

    # --- apply deterministic auto-fixes ---
    applied = apply_auto(skill_path, buckets["auto"]) if branch or args.no_branch else []
    if applied and branch:
        commit_all(root, f"skill-fix: deterministic fixes for {skill_path.name}\n\n"
                         + "\n".join(f"- {a}" for a in applied))

    # --- restore parked artifacts (after branch + commit, on the new branch) ---
    if stashed and root is not None:
        pr = pop_artifacts(root)
        if pr.returncode != 0:
            git_note += (" | WARNING: could not pop .skill-review/ artifacts back "
                         f"(recover with `git stash pop`): {pr.stderr.strip()}")

    manifest = {
        "skill": skill_path.name,
        "skill_path": str(skill_path),
        "branch": branch,
        "git": git_note,
        "auto_applied": applied,
        "draft_todo": buckets["draft"],
        "human_required": buckets["human"],
        "counts": {k: len(v) for k, v in buckets.items()},
    }

    # --- print summary ---
    print(f"\n=== Fix plan: {skill_path.name} ===")
    print(f"git: {git_note}")
    print(f"auto-applied: {len(applied)}   draft-to-fix: {len(buckets['draft'])}   "
          f"human-required: {len(buckets['human'])}\n")
    if applied:
        print("-- AUTO-APPLIED (committed) --")
        for a in applied:
            print(f"  + {a}")
        print()
    if buckets["draft"]:
        print("-- DRAFT (Claude to fix on the branch) --")
        for f in buckets["draft"]:
            print(f"  ~ [{f['severity']}/{f['check']}] {f['message']}")
        print()
    if buckets["human"]:
        print("-- HUMAN-REQUIRED (do NOT auto-fix) --")
        for f in buckets["human"]:
            print(f"  ! [{f['severity']}/{f['check']}] {f['message']}")
        print()

    if args.json_out:
        Path(args.json_out).write_text(json.dumps(manifest, indent=2))
        print(f"Manifest written to {args.json_out}")


if __name__ == "__main__":
    main()
