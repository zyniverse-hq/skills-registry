#!/usr/bin/env python3
"""
Zyniverse Skills Registry — SKILL.md Validator
Checks that a SKILL.md file meets the contribution standard.
Usage: python3 scripts/validate_skill.py skills/my-skill/SKILL.md
"""

import sys
import re
import os
import yaml

VALID_CATEGORIES = {
    "qa-testing", "pre-deploy-safety", "business-sales", "engineering-practice",
    "frontend-integration", "infra-security", "documents", "ai-agents", "data", "comms"
}
VALID_PRODUCTS = {"zysk", "tms", "zyniverse"}
REQUIRED_SECTIONS = ["## When to use", "## Steps", "## Output"]

# ── Template placeholder strings that must not appear in a real submission ───
FRONTMATTER_PLACEHOLDERS = {
    "name":        ["your-skill-name"],
    "description": ["verb-first", "your description", "one sentence that tells claude"],
    "author":      ["your full name", "your name"],
    "email":       ["you@zysk.tech"],
}
BODY_PLACEHOLDERS = [
    "your-skill-name",
    "your full name",
    "you@zysk.tech",
    "verb-first one sentence",
    "[specific condition]",
    "[instructions for claude]",
    "[action name]",
    "prerequisite 1",
    "prerequisite 2",
    "tag-one",
    "tag-two",
]

ERRORS = []
WARNINGS = []


def error(msg):
    ERRORS.append(f"  ❌ {msg}")


def warn(msg):
    WARNINGS.append(f"  ⚠️  {msg}")


def parse_frontmatter(path):
    with open(path) as f:
        content = f.read()
    if not content.startswith("---"):
        error("File does not start with YAML frontmatter (---)")
        return None, content
    parts = content.split("---", 2)
    if len(parts) < 3:
        error("Frontmatter is not properly closed with ---")
        return None, content
    try:
        fm = yaml.safe_load(parts[1])
        return fm, parts[2]
    except yaml.YAMLError as e:
        error(f"Invalid YAML frontmatter: {e}")
        return None, content


def validate_semver(version):
    return bool(re.match(r"^\d+\.\d+\.\d+$", str(version)))


def get_field(fm, key):
    """Return a frontmatter field from the top level, falling back to a nested
    `metadata:` map. The agentskills.io spec allows non-spec fields (author,
    version, category, tags, …) to live under `metadata:`, so accept either
    placement rather than emitting a spurious 'missing field' warning."""
    val = fm.get(key)
    if val not in (None, ""):
        return val
    meta = fm.get("metadata")
    if isinstance(meta, dict):
        return meta.get(key)
    return None


def validate_name(name):
    """Validate `name` against the agentskills.io spec: 1-64 chars, lowercase
    alphanumerics and single hyphens, no leading/trailing or consecutive
    hyphens. Emits specific errors; returns True if valid."""
    ok = True
    if len(name) > 64:
        error(f"'name' must be at most 64 characters — got {len(name)}")
        ok = False
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        error(
            "'name' must be lowercase alphanumerics separated by single hyphens, "
            "with no leading/trailing or consecutive hyphens — got: " + name
        )
        ok = False
    return ok


def get_existing_names(skip_folder=None):
    """Collect all skill names already registered in the repo."""
    names = {}
    if not os.path.isdir("skills"):
        return names
    for entry in os.scandir("skills"):
        if not entry.is_dir() or entry.name.startswith("_"):
            continue
        if skip_folder and entry.name == skip_folder:
            continue
        skill_path = os.path.join(entry.path, "SKILL.md")
        if not os.path.exists(skill_path):
            continue
        try:
            with open(skill_path) as f:
                content = f.read()
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    fm = yaml.safe_load(parts[1])
                    if fm and fm.get("name"):
                        names[str(fm["name"])] = skill_path
        except Exception:
            pass
    return names


def check_placeholders_in_frontmatter(fm):
    """Fail if any frontmatter field still contains template placeholder text."""
    for field, placeholders in FRONTMATTER_PLACEHOLDERS.items():
        value = str(fm.get(field, "")).strip().lower()
        if not value:
            continue
        for placeholder in placeholders:
            if placeholder in value:
                error(
                    f"'{field}' still contains template placeholder text "
                    f"(\"{placeholder}\") — replace it with your actual value"
                )
                break


def check_placeholders_in_body(body):
    """Fail if the body still contains template placeholder text."""
    body_lower = body.lower()
    found = [p for p in BODY_PLACEHOLDERS if p in body_lower]
    if found:
        error(
            f"Skill body still contains template placeholder text: "
            f"{', '.join(repr(p) for p in found)} — replace all placeholders before submitting"
        )


def validate_description_quality(description):
    """Check description doesn't contain placeholder text and starts correctly."""
    desc = str(description).strip()
    desc_lower = desc.lower()

    # Placeholder check (already covered in frontmatter check, but double-guard)
    for placeholder in FRONTMATTER_PLACEHOLDERS.get("description", []):
        if placeholder in desc_lower:
            error(
                f"'description' still contains placeholder text (\"{placeholder}\") "
                f"— write a real description of what your skill does"
            )
            return

    # Must not be a question
    if desc.endswith("?"):
        error("'description' must be a statement, not a question")

    # Should start with a capital letter
    if desc and not desc[0].isupper():
        warn("'description' should start with a capital letter")


def validate_file(path, existing_names):
    print(f"\nValidating: {path}")

    # ── File location ────────────────────────────────────────────────────────
    parts = path.replace("\\", "/").split("/")
    if len(parts) < 3 or parts[0] != "skills" or parts[-1] != "SKILL.md":
        error(f"File must be at skills/<skill-name>/SKILL.md — got: {path}")

    folder_name = parts[1] if len(parts) >= 3 else None

    # ── Parse frontmatter ────────────────────────────────────────────────────
    fm, body = parse_frontmatter(path)
    if fm is None:
        return

    # ── Template placeholder checks ──────────────────────────────────────────
    check_placeholders_in_frontmatter(fm)
    check_placeholders_in_body(body)

    # ── Required fields ──────────────────────────────────────────────────────
    name = fm.get("name")
    if not name:
        error("Missing required field: name")
    else:
        name = str(name)
        name_ok = validate_name(name)
        if folder_name and name != folder_name:
            error(f"'name' ({name}) must match folder name ({folder_name})")
        if name_ok and name in existing_names:
            error(
                f"'name' ({name}) already exists in the registry at "
                f"{existing_names[name]} — choose a unique name"
            )

    description = fm.get("description")
    if not description:
        error("Missing required field: description")
    else:
        desc = str(description).strip()
        if len(desc) < 10:
            error("'description' is too short — write a meaningful one-sentence description")
        elif len(desc) > 1024:
            error(f"'description' exceeds the 1024-character spec limit — got {len(desc)}")
        else:
            if len(desc) > 200:
                warn("'description' is very long — keep it under 200 characters for registry display")
            validate_description_quality(description)

    # ── Optional spec fields ─────────────────────────────────────────────────
    compatibility = fm.get("compatibility")
    if compatibility is not None and len(str(compatibility)) > 500:
        error(f"'compatibility' must be at most 500 characters — got {len(str(compatibility))}")

    allowed_tools = fm.get("allowed-tools")
    if allowed_tools is not None and not isinstance(allowed_tools, str):
        error(
            "'allowed-tools' must be a space-separated string "
            '(e.g. "Read Write Bash"), not a YAML list'
        )

    # ── Extended fields (warn only; accepted top-level or under metadata:) ────
    version = get_field(fm, "version")
    if not version:
        warn("Missing 'version' — add version: 1.0.0")
    elif not validate_semver(version):
        error(f"'version' must be semver (e.g. 1.0.0) — got: {version}")

    if not get_field(fm, "author"):
        warn("Missing 'author' — add your name")

    category = get_field(fm, "category")
    if not category:
        warn("Missing 'category' — add one of: " + ", ".join(sorted(VALID_CATEGORIES)))
    elif category not in VALID_CATEGORIES:
        error(f"Invalid 'category': {category}. Must be one of: {', '.join(sorted(VALID_CATEGORIES))}")

    tags = get_field(fm, "tags") or []
    if not tags:
        warn("Missing 'tags' — add 2–5 lowercase kebab-case tags")
    elif len(tags) < 2:
        warn("Add at least 2 tags")
    elif len(tags) > 5:
        warn("Keep tags to 5 or fewer")
    else:
        for t in tags:
            if not re.match(r"^[a-z][a-z0-9-]*$", str(t)):
                error(f"Tag '{t}' must be lowercase kebab-case")

    product = get_field(fm, "product")
    if product and product not in VALID_PRODUCTS:
        error(f"Invalid 'product': {product}. Must be one of: {', '.join(VALID_PRODUCTS)}")

    # ── Body content ─────────────────────────────────────────────────────────
    for section in REQUIRED_SECTIONS:
        if section not in body:
            error(f"Missing required section: {section}")

    if len(body.strip()) < 100:
        warn("Skill content is very short — add more detail to help Claude use it correctly")


def main():
    paths = sys.argv[1:]
    if not paths:
        # Discover all SKILL.md files in skills/ (skip _template)
        for root, dirs, files in os.walk("skills"):
            dirs[:] = [d for d in dirs if not d.startswith("_")]
            if "SKILL.md" in files:
                paths.append(os.path.join(root, "SKILL.md"))

    if not paths:
        print("No SKILL.md files found.")
        sys.exit(0)

    # Build the existing name registry once (skip the folder being validated
    # so a skill isn't flagged as a duplicate of itself when updating)
    incoming_folders = set()
    for p in paths:
        parts = p.replace("\\", "/").split("/")
        if len(parts) >= 3:
            incoming_folders.add(parts[1])

    existing_names = get_existing_names(
        skip_folder=next(iter(incoming_folders), None)
    )

    for path in paths:
        validate_file(path.strip(), existing_names)

    print()
    if WARNINGS:
        print("Warnings:")
        for w in WARNINGS:
            print(w)

    if ERRORS:
        print("\nErrors:")
        for e in ERRORS:
            print(e)
        print(f"\n💥 Validation failed — {len(ERRORS)} error(s), {len(WARNINGS)} warning(s)")
        sys.exit(1)
    else:
        print(f"✅ Validation passed — {len(WARNINGS)} warning(s)")
        sys.exit(0)


if __name__ == "__main__":
    main()
