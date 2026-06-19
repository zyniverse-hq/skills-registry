#!/usr/bin/env python3
"""
Zyniverse Skills Registry — index.json generator.

Scans skills/*/SKILL.md, parses YAML frontmatter, and rebuilds the
`skills[]` array in index.json. Categories/groups metadata is preserved.

Skips skills/_template/ and any SKILL.md with invalid/missing frontmatter
(prints a warning rather than crashing — the PR-time validator is the gate).

Usage:
  python3 scripts/generate_index.py            # rewrite index.json
  python3 scripts/generate_index.py --check    # exit 1 if index.json would change
"""

import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
INDEX_PATH = ROOT / "index.json"

GROUP_BY_MODEL_PREFIX = {
    "claude-opus":   "opus",
    "claude-sonnet": "sonnet",
    "claude-haiku":  "haiku",
}
CATEGORY_ICON = {
    "qa-testing": "🧪",
    "pre-deploy-safety": "🛡️",
    "business-sales": "💼",
    "engineering-practice": "🛠️",
    "frontend-integration": "🔌",
    "infra-security": "🔐",
    "documents": "📄",
    "ai-agents": "🤖",
    "data": "📊",
    "comms": "💬",
}


def parse_frontmatter(path: Path):
    text = path.read_text()
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    return yaml.safe_load(parts[1])


def get_field(fm: dict, key: str):
    """Read a field from the top level, falling back to a nested `metadata:` map.
    Mirrors scripts/validate_skill.py so spec-style skills that nest non-spec
    fields under `metadata:` still populate the registry index."""
    val = fm.get(key)
    if val not in (None, ""):
        return val
    meta = fm.get("metadata")
    if isinstance(meta, dict):
        return meta.get(key)
    return None


def derive_group(tested_with: str) -> str:
    if not tested_with:
        return "opus"
    for prefix, group in GROUP_BY_MODEL_PREFIX.items():
        if tested_with.startswith(prefix):
            return group
    return "opus"


def build_entry(folder: Path):
    skill_md = folder / "SKILL.md"
    if not skill_md.exists():
        return None
    try:
        fm = parse_frontmatter(skill_md)
    except yaml.YAMLError as e:
        print(f"⚠️  Skipping {folder.name}: invalid YAML frontmatter ({e})", file=sys.stderr)
        return None
    if not fm or not isinstance(fm, dict):
        print(f"⚠️  Skipping {folder.name}: no frontmatter", file=sys.stderr)
        return None
    if "name" not in fm or "description" not in fm:
        print(f"⚠️  Skipping {folder.name}: missing required name/description", file=sys.stderr)
        return None

    category = get_field(fm, "category") or ""
    return {
        "slug":        folder.name,
        "name":        fm["name"],
        "description": fm["description"],
        "version":     get_field(fm, "version") or "0.1.0",
        "author":      get_field(fm, "author") or "",
        "email":       get_field(fm, "email") or "",
        "category":    category,
        "group":       derive_group(get_field(fm, "tested_with") or ""),
        "tags":        get_field(fm, "tags") or [],
        "product":     get_field(fm, "product") or "",
        "tested_with": get_field(fm, "tested_with") or "",
        "icon":        CATEGORY_ICON.get(category, "🧩"),
    }


def collect_skills():
    entries = []
    for folder in sorted(SKILLS_DIR.iterdir()):
        if not folder.is_dir() or folder.name.startswith("_"):
            continue
        entry = build_entry(folder)
        if entry:
            entries.append(entry)
    return entries


def main():
    check_mode = "--check" in sys.argv

    index = json.loads(INDEX_PATH.read_text())
    new_skills = collect_skills()
    old_skills = index.get("skills", [])

    if check_mode:
        if old_skills != new_skills:
            print("❌ index.json is out of date. Run: python3 scripts/generate_index.py")
            sys.exit(1)
        print("✅ index.json is up to date.")
        return

    index["skills"] = new_skills
    INDEX_PATH.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n")
    print(f"✅ Wrote {len(new_skills)} skill(s) to index.json")


if __name__ == "__main__":
    main()
