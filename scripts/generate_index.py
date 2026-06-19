#!/usr/bin/env python3
"""
Zyniverse Skills Registry — index.json generator.

Scans skills/*/SKILL.md, parses YAML frontmatter, and rebuilds the `skills[]`
array plus the `categories[]` array (from scripts/categories.json, including only
categories in use) in index.json. The `groups` metadata is preserved. Also
regenerates .claude-plugin/marketplace.json (one plugin per skill).

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
MARKETPLACE_PATH = ROOT / ".claude-plugin" / "marketplace.json"
REPO_URL = "https://github.com/zyniverse-hq/skills-registry"

GROUP_BY_MODEL_PREFIX = {
    "claude-opus":   "opus",
    "claude-sonnet": "sonnet",
    "claude-haiku":  "haiku",
}
# Single source of truth for the category taxonomy (slug -> label + icon),
# shared with scripts/validate_skill.py. Add a category there once.
CATEGORIES_PATH = ROOT / "scripts" / "categories.json"
CANONICAL_CATEGORIES = json.loads(CATEGORIES_PATH.read_text(encoding="utf-8"))
CATEGORY_ICON = {c["slug"]: c["icon"] for c in CANONICAL_CATEGORIES}


def parse_frontmatter(path: Path):
    text = path.read_text(encoding="utf-8")
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


def build_categories(skills):
    """Derive index `categories[]` from the canonical list, including only
    categories actually used by >= 1 skill — so a new category slug can never
    silently orphan a skill, and unused categories don't render empty filters."""
    used = {s["category"] for s in skills if s.get("category")}
    return [c for c in CANONICAL_CATEGORIES if c["slug"] in used]


def build_marketplace(skills):
    """Generate the Claude Code plugin marketplace from skills/, one plugin per
    skill (source ./skills/<slug> — the single SKILL.md makes it a single-skill
    plugin). Generated so each skill is individually installable and new skills
    appear automatically. Metadata comes from the skill's frontmatter."""
    plugins = []
    for s in skills:
        slug = s["slug"]
        entry = {"name": slug, "source": f"./skills/{slug}", "description": s["description"]}
        if s.get("version"):
            entry["version"] = s["version"]
        author = {}
        if s.get("author"):
            author["name"] = s["author"]
        if s.get("email"):
            author["email"] = s["email"]
        if author:
            entry["author"] = author
        entry["license"] = "Apache-2.0"
        if s.get("category"):
            entry["category"] = s["category"]
        if s.get("tags"):
            entry["keywords"] = s["tags"]
        entry["homepage"] = f"{REPO_URL}/tree/main/skills/{slug}"
        entry["repository"] = REPO_URL
        plugins.append(entry)
    return {
        "name": "zyniverse-skills",
        "owner": {"name": "Zyni Innovations Pvt. Ltd.", "email": "varun@zysk.tech"},
        "description": "Curated registry of production-grade agent skills by Zyni Innovations.",
        "plugins": plugins,
    }


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    check_mode = "--check" in sys.argv

    index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    new_skills = collect_skills()
    new_categories = build_categories(new_skills)
    new_marketplace = build_marketplace(new_skills)
    old_skills = index.get("skills", [])
    old_categories = index.get("categories", [])
    old_marketplace = (
        json.loads(MARKETPLACE_PATH.read_text(encoding="utf-8"))
        if MARKETPLACE_PATH.exists() else None
    )

    if check_mode:
        if (old_skills != new_skills or old_categories != new_categories
                or old_marketplace != new_marketplace):
            print("❌ index.json/marketplace.json is out of date. Run: python3 scripts/generate_index.py")
            sys.exit(1)
        print("✅ index.json and marketplace.json are up to date.")
        return

    index["skills"] = new_skills
    index["categories"] = new_categories
    INDEX_PATH.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    MARKETPLACE_PATH.write_text(json.dumps(new_marketplace, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"✅ Wrote {len(new_skills)} skill(s), {len(new_categories)} categor(ies), "
          f"and {len(new_marketplace['plugins'])} marketplace plugin(s)")


if __name__ == "__main__":
    main()
