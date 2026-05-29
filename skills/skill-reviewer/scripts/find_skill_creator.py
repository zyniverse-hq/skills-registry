#!/usr/bin/env python3
"""
find_skill_creator.py - Locate an installed skill-creator skill.

skill-reviewer delegates the measured trigger-rate run to skill-creator's
runner (scripts/run_eval.py) rather than re-implementing it, so this finds a
valid skill-creator install. It prints the absolute path on success (exit 0),
or NOT FOUND (exit 1) so the workflow can fall back to qualitative reasoning.

A directory counts only if it actually contains scripts/run_eval.py.

Usage:
    python3 find_skill_creator.py [extra_candidate_dir ...]
"""

import os
import sys
from pathlib import Path


def candidates(extra):
    home = Path.home()
    cwd = Path.cwd()
    paths = [
        home / ".claude" / "skills" / "skill-creator",
        cwd / ".claude" / "skills" / "skill-creator",
    ]
    env = os.environ.get("SKILL_CREATOR_PATH")
    if env:
        paths.insert(0, Path(env))
    paths.extend(Path(p) for p in extra)
    return paths


def find(extra):
    for p in candidates(extra):
        if (p / "scripts" / "run_eval.py").is_file():
            return p.resolve()
    return None


def main():
    found = find(sys.argv[1:])
    if found:
        print(found)
        sys.exit(0)
    print("NOT FOUND")
    sys.exit(1)


if __name__ == "__main__":
    main()
