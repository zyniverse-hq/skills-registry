#!/usr/bin/env python3
"""
review_skill.py - Deterministic static checks for an Anthropic Agent Skill.

Runs the objectively-verifiable parts of a skill review and emits findings,
a heuristic score, and a context-footprint metric:
  - Structure / spec compliance (would it upload?)
  - Quality heuristics (size, triggering cues, directive style, TOCs, dead refs)
  - Script hygiene (compiles? undisclosed third-party deps?)
  - Security (code pattern scan, real hardcoded-secret detection, prose/instruction
    scan of SKILL.md + references, and undeclared-binary detection)
  - Metrics (composite score per dimension, token/footprint estimate)

This script only READS files. It makes no network calls, runs no subprocess,
and deletes nothing - so reviewing a skill can never execute that skill's code.
The human (or Claude) layers qualitative judgement on top - see
references/checklist.md.

Dependencies: standard library only. PyYAML is used if available for exact
frontmatter parsing; otherwise a minimal built-in parser is used.

Usage:
    python3 review_skill.py <path/to/skill-folder> [--json OUTFILE]
                            [--fail-on {blocker,major,review}]
                            [--instruction-findings FILE]
"""

import argparse
import ast
import json
import re
import sys
import py_compile
import tempfile
from datetime import datetime, timezone
from pathlib import Path

# Bumped when checks change, so a stored JSON report is traceable to the ruleset
# that produced it (the skill-certifier records this in its audit stamp).
REVIEWER_VERSION = "1.1.0"

# ---- Spec constants (mirrors Anthropic's skill validator) -------------------
ALLOWED_PROPERTIES = {
    "name", "description", "license", "allowed-tools", "metadata", "compatibility",
}
NAME_MAX = 64
DESCRIPTION_MAX = 1024
COMPATIBILITY_MAX = 500
BODY_SOFT_LINE_LIMIT = 500
BODY_TOKEN_SOFT_LIMIT = 6000  # catches few-but-very-long lines under the line cap
REFERENCE_TOC_THRESHOLD = 300
DIRECTIVE_WARN_COUNT = 8
CHARS_PER_TOKEN = 4  # rough token estimate; see compute_metrics
# Names of bundled skills a custom skill should not collide with.
BUNDLED_NAMES = {"pdf", "docx", "pptx", "xlsx", "frontend-design", "skill-creator"}

# Word-level patterns flagged for human review (legitimate uses are common).
SECURITY_PATTERNS = {
    "network": [r"\brequests\.", r"\burllib\b", r"urlopen", r"http\.client",
                r"\bsocket\.", r"aiohttp", r"httpx", r"\bcurl\b", r"\bwget\b",
                r"fetch\(", r"axios"],
    "process_exec": [r"subprocess", r"os\.system", r"os\.popen", r"\beval\(",
                     r"\bexec\(", r"pickle\.loads", r"child_process",
                     r"shell\s*=\s*True"],
    "destructive_fs": [r"rm\s+-rf", r"shutil\.rmtree", r"os\.remove",
                       r"os\.unlink", r"\.unlink\(", r"\brmdir\b"],
    "secrets": [r"os\.environ", r"getenv", r"\.aws\b", r"\.ssh\b", r"\.env\b",
                r"SECRET", r"PRIVATE KEY", r"password\s*=", r"token\s*="],
    "obfuscation": [r"b64decode", r"codecs\.decode", r"exec\(.*decode"],
}
# Real credential material: matches generate Blockers, not "review this". Patterns
# are structured/high-confidence to keep false positives low.
SECRET_LITERALS = {
    "aws_access_key": r"AKIA[0-9A-Z]{16}",
    "private_key_block": r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    "github_token": r"gh[pousr]_[A-Za-z0-9]{36}",
    "slack_token": r"xox[baprs]-[A-Za-z0-9-]{10,}",
    "google_api_key": r"AIza[0-9A-Za-z_\-]{35}",
    "openai_key": r"sk-(?:proj-)?[A-Za-z0-9]{32,}",
    "stripe_secret": r"[sr]k_live_[0-9A-Za-z]{16,}",
    "npm_token": r"npm_[A-Za-z0-9]{36}",
    "gcp_service_account": r'"type"\s*:\s*"service_account"',
    "assigned_secret": r"""(?i)(api[_-]?key|secret|token|passwd|password)\s*[:=]\s*['"][A-Za-z0-9_\-/+]{16,}['"]""",
}
# Prose red flags. A skill is followed as natural-language instructions, so its
# SKILL.md and references are scanned (as REVIEW) for directions that would
# surprise a reader of the description - the primary attack surface for a skill is
# the instructions Claude obeys, not only the code it bundles.
PROSE_SECURITY_PATTERNS = {
    "pipe_to_shell": [r"(?:curl|wget|iwr|invoke-webrequest)\b[^\n|]*\|\s*"
                      r"(?:bash|sh|zsh|python3?|powershell|pwsh|iex)\b"],
    "exfiltration": [r"\b(?:send|post|upload|exfiltrate|transmit|forward)\b"
                     r"[^.\n]{0,60}?(?:https?://|\b\d{1,3}(?:\.\d{1,3}){3}\b)"],
}
URL_RE = re.compile(r"https?://([A-Za-z0-9.\-]+)")
# Negative lookarounds also exclude '=' so version pins (==4.9.0.80) and 'v'-prefixed
# versions aren't mistaken for IP addresses.
IP_RE = re.compile(r"(?<![\w.=])\d{1,3}(?:\.\d{1,3}){3}(?![\w.=])")
B64_RE = re.compile(r"[A-Za-z0-9+/]{80,}={0,2}")
BENIGN_HOSTS = {"localhost", "example.com", "example.org", "www.example.com"}
PROSE_SUFFIXES = {".md", ".markdown", ".txt", ".rst"}
# Opaque/executable artifacts whose contents can't be reviewed as text.
RISKY_BINARY_SUFFIXES = {".exe", ".dll", ".so", ".dylib", ".bin", ".pyc", ".pyo",
                         ".class", ".o", ".a", ".deb", ".dmg", ".msi", ".jar",
                         ".wasm", ".node"}
CODE_SUFFIXES = {".py", ".sh", ".bash", ".zsh", ".js", ".mjs", ".cjs", ".ts",
                 ".rb", ".pl", ".php", ".ps1"}
# Directories that are never part of the shipped skill; excluded from every walk
# so they can't inflate the footprint or get scanned as the skill's own content.
IGNORE_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv",
               ".mypy_cache", ".pytest_cache", ".tox", ".idea", ".ruff_cache"}
# Score penalties per severity, with rationale so the weights aren't arbitrary:
#   BLOCKER - fails upload or is a real security risk; should dominate the score.
#   MAJOR   - materially hurts reliability or trust.
#   MINOR   - a confirmed bit of polish.
#   REVIEW  - an UNCONFIRMED flag a human must judge (e.g. a scanned pattern); it
#             weighs no more than a confirmed minor and is capped per dimension, so a
#             pile of "please verify" hits can't tank a score on its own.
# Repeats of one check are additionally capped - see PER_CHECK_REPEAT_FACTOR.
SEVERITY_ORDER = {"BLOCKER": 0, "MAJOR": 1, "REVIEW": 2, "MINOR": 3, "INFO": 4, "ADVICE": 5}
SCORE_PENALTY = {"BLOCKER": 40, "MAJOR": 12, "REVIEW": 3, "MINOR": 3, "INFO": 0, "ADVICE": 0}
REVIEW_PENALTY_CAP = 15  # max total score hit from REVIEW findings, per dimension
# Repeats of the SAME check in one dimension count at most this many times at full
# weight (so e.g. N undisclosed deps from one missing requirements file, or a flood
# of identical minors, can't tank a dimension out of proportion to the root cause).
PER_CHECK_REPEAT_FACTOR = 2
# The four scored dimensions (see compute_metrics). Instruction findings folded in
# via --instruction-findings must target one of these so they move score + gate.
SCORED_DIMENSIONS = ("structure", "quality", "triggering", "security")
# Tokens that mark a path as an illustrative example, not a real bundled file.
PLACEHOLDER_TOKENS = {"their", "your", "name", "path", "folder", "topic", "foo",
                      "bar", "baz", "example", "changelog-gen", "my-skill"}
# Import name -> distribution name, for cases where they differ. Keeps the
# undisclosed-dependency check from false-flagging a declared package.
IMPORT_ALIASES = {
    "cv2": "opencv-python", "bs4": "beautifulsoup4", "sklearn": "scikit-learn",
    "PIL": "pillow", "yaml": "pyyaml", "dotenv": "python-dotenv", "attr": "attrs",
    "dateutil": "python-dateutil", "Crypto": "pycryptodome", "OpenSSL": "pyopenssl",
    "git": "gitpython", "jwt": "pyjwt", "serial": "pyserial", "usb": "pyusb",
}


def finding(dimension, severity, check, message):
    return {"dimension": dimension, "severity": severity, "check": check,
            "message": message}


def _ignored(path):
    """True if any path component is a tooling/build dir we never count as skill content."""
    return any(part in IGNORE_DIRS for part in path.parts)


# ---- Frontmatter parsing ----------------------------------------------------
def parse_frontmatter(content):
    """Return (data, body, error, used_yaml). used_yaml is True only when PyYAML
    actually parsed the block, so callers know whether structured keys
    (allowed-tools/metadata) were parsed exactly or by the line-based fallback."""
    if not content.startswith("---"):
        return None, content, "no YAML frontmatter (file must start with '---')", False
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", content, re.DOTALL)
    if not m:
        return None, content, "frontmatter opened with '---' but never closed", False
    fm_text, body = m.group(1), m.group(2)
    try:
        import yaml
        data = yaml.safe_load(fm_text)
        if not isinstance(data, dict):
            return None, body, "frontmatter is not a YAML mapping", True
        return data, body, None, True
    except ImportError:
        pass
    except Exception as e:  # noqa: BLE001
        return None, body, f"invalid YAML in frontmatter: {e}", False
    data = {}
    for line in fm_text.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line[0] in (" ", "\t"):
            continue
        mm = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if mm:
            key, val = mm.group(1), mm.group(2).strip()
            if (val.startswith('"') and val.endswith('"')) or \
               (val.startswith("'") and val.endswith("'")):
                val = val[1:-1]
            data[key] = val
    return data, body, None, False


# ---- Structure / spec checks ------------------------------------------------
def check_structure(skill_path, findings):
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        findings.append(finding("structure", "BLOCKER", "skill_md_present",
                                 "No SKILL.md at the skill root."))
        return None, None

    extra = [p for p in skill_path.rglob("SKILL.md")
             if p.resolve() != skill_md.resolve()
             and "__pycache__" not in p.parts and "node_modules" not in p.parts
             and p.relative_to(skill_path).parts[:1] != ("evals",)]
    if extra:
        rels = ", ".join(str(p.relative_to(skill_path)) for p in extra)
        findings.append(finding("structure", "BLOCKER", "single_skill_md",
                                 f"Multiple SKILL.md files found (rejected on upload): {rels}."))

    content = skill_md.read_text(encoding="utf-8", errors="replace")
    fm, body, err, used_yaml = parse_frontmatter(content)
    if err:
        findings.append(finding("structure", "BLOCKER", "frontmatter_valid", err))
        return fm, body

    unexpected = set(fm.keys()) - ALLOWED_PROPERTIES
    if unexpected:
        findings.append(finding("structure", "BLOCKER", "allowed_keys",
                                 f"Unexpected frontmatter key(s): {', '.join(sorted(unexpected))}. "
                                 f"Allowed: {', '.join(sorted(ALLOWED_PROPERTIES))}."))

    name = (fm.get("name") or "").strip()
    if not name:
        findings.append(finding("structure", "BLOCKER", "name_present", "Missing required 'name'."))
    else:
        if not re.match(r"^[a-z0-9-]+$", name):
            findings.append(finding("structure", "BLOCKER", "name_format",
                                     f"name '{name}' must be kebab-case."))
        elif name.startswith("-") or name.endswith("-") or "--" in name:
            findings.append(finding("structure", "BLOCKER", "name_format",
                                     f"name '{name}' cannot start/end with '-' or contain '--'."))
        if len(name) > NAME_MAX:
            findings.append(finding("structure", "BLOCKER", "name_length",
                                     f"name is {len(name)} chars; max {NAME_MAX}."))
        if name != skill_path.name:
            findings.append(finding("structure", "MINOR", "name_matches_folder",
                                     f"name '{name}' differs from folder '{skill_path.name}'."))
        if name in BUNDLED_NAMES:
            findings.append(finding("structure", "MAJOR", "name_collision",
                                     f"name '{name}' collides with a bundled skill; it may be "
                                     "shadowed or cause confusion. Choose a distinct name."))

    desc = (fm.get("description") or "").strip()
    if not desc:
        findings.append(finding("structure", "BLOCKER", "description_present", "Missing required 'description'."))
    else:
        if "<" in desc or ">" in desc:
            findings.append(finding("structure", "BLOCKER", "description_no_brackets",
                                     "description cannot contain angle brackets."))
        if len(desc) > DESCRIPTION_MAX:
            findings.append(finding("structure", "BLOCKER", "description_length",
                                     f"description is {len(desc)} chars; max {DESCRIPTION_MAX}."))

    compat = fm.get("compatibility")
    if isinstance(compat, str) and len(compat) > COMPATIBILITY_MAX:
        findings.append(finding("structure", "MAJOR", "compatibility_length",
                                 f"compatibility is {len(compat)} chars; max {COMPATIBILITY_MAX}."))

    # Structured keys: validate exactly when PyYAML parsed them; otherwise note that
    # the fallback parser can't see list/mapping values so they went unchecked.
    if used_yaml:
        at = fm.get("allowed-tools")
        if at is not None and not (
                (isinstance(at, str) and at.strip())
                or (isinstance(at, list) and all(isinstance(x, str) for x in at))):
            findings.append(finding("structure", "MAJOR", "allowed_tools_type",
                                     "allowed-tools must be a list of tool-name strings "
                                     "(or a comma-separated string)."))
        md_val = fm.get("metadata")
        if md_val is not None and not isinstance(md_val, dict):
            findings.append(finding("structure", "MAJOR", "metadata_type",
                                     "metadata must be a mapping (key/value object)."))
    elif "allowed-tools" in fm or "metadata" in fm:
        findings.append(finding("structure", "MINOR", "frontmatter_parser",
                                 "PyYAML is not installed, so structured keys "
                                 "(allowed-tools/metadata) were not fully parsed or validated. "
                                 "Install PyYAML for an exact check."))
    return fm, body


# ---- Quality heuristics -----------------------------------------------------
def _iter_referenced_paths(body):
    """Yield candidate bundled-resource paths mentioned in the body,
    skipping anything under an 'Example' heading and obvious placeholders."""
    in_example = False
    for line in body.splitlines():
        h = re.match(r"^#{1,6}\s+(.*)$", line)
        if h:
            in_example = "example" in h.group(1).lower()
            continue
        if in_example:
            continue
        for token in re.findall(r"`([^`]+)`", line) + [line]:
            for cand in re.findall(
                    r"(?:\./)?((?:scripts|references|assets)/[A-Za-z0-9_./-]+)", token):
                c = cand.strip().lstrip("./").rstrip(".,);:")
                low = c.lower()
                if any(ch in c for ch in "<>{}") or "..." in c or "…" in c:
                    continue
                if any(tok in low for tok in PLACEHOLDER_TOKENS):
                    continue
                yield c


def check_quality(skill_path, fm, body, findings):
    if body is not None:
        n_lines = len(body.splitlines())
        non_blank = sum(1 for ln in body.splitlines() if ln.strip())
        findings.append(finding("quality", "INFO", "body_size", f"SKILL.md body is {n_lines} lines."))
        if non_blank == 0:
            findings.append(finding("quality", "MAJOR", "empty_body",
                                     "SKILL.md has frontmatter but no body. The body is the "
                                     "on-trigger instruction Claude follows; add the procedure."))
        elif non_blank < 5:
            findings.append(finding("quality", "MINOR", "thin_body",
                                     f"SKILL.md body is very thin ({non_blank} non-blank lines); "
                                     "it may be too sparse to guide the model."))
        if n_lines > BODY_SOFT_LINE_LIMIT:
            findings.append(finding("quality", "MAJOR", "body_size",
                                     f"SKILL.md body is {n_lines} lines (> {BODY_SOFT_LINE_LIMIT}). "
                                     "Move detail into references/."))
        body_tokens = round(len(body) / CHARS_PER_TOKEN)
        if n_lines <= BODY_SOFT_LINE_LIMIT and body_tokens > BODY_TOKEN_SOFT_LIMIT:
            findings.append(finding("quality", "MAJOR", "body_tokens",
                                     f"SKILL.md body is ~{body_tokens} tokens (long lines) though "
                                     f"under the line cap. Trim or move detail into references/."))
        directives = len(re.findall(r"\b(ALWAYS|NEVER|MUST)\b", body))
        findings.append(finding("quality", "INFO", "directive_style",
                                 f"{directives} absolute directive(s) in body."))
        if directives >= DIRECTIVE_WARN_COUNT:
            findings.append(finding("quality", "MINOR", "directive_style",
                                     f"Heavy use of absolute directives ({directives}). Explain the 'why' instead."))
        # Dangling references to bundled resources.
        seen = set()
        for ref in _iter_referenced_paths(body):
            if ref in seen:
                continue
            seen.add(ref)
            if not (skill_path / ref).exists():
                findings.append(finding("quality", "MINOR", "dangling_reference",
                                         f"SKILL.md references '{ref}', which is not present. "
                                         "Fix the path or remove the reference."))

    if fm:
        desc = fm.get("description") or ""
        low = desc.lower()
        cue_substrings = ["when", "whenever", "use this", "use when", "use to",
                          "use for", "use it", "trigger", "if the user", "for any",
                          "for tasks", "any time", "after you", "before you"]
        # Catch imperative phrasings the substring list misses, e.g. "Use ... to
        # <verb>" or "for <gerund>", so a valid description isn't flagged as a Major.
        cue_regexes = [r"\buse\b[^.]{0,40}?\bto\b", r"\bfor\b\s+\w+ing\b"]
        has_cue = (any(c in low for c in cue_substrings)
                   or any(re.search(rx, low) for rx in cue_regexes))
        if desc and not has_cue:
            findings.append(finding("triggering", "MAJOR", "trigger_cues",
                                     "description lacks explicit 'when to use' cues."))
        if desc and len(desc) < 40:
            findings.append(finding("triggering", "MINOR", "description_detail",
                                     f"description is short ({len(desc)} chars)."))

    for sub in ("scripts", "references", "assets"):
        present = (skill_path / sub).is_dir()
        findings.append(finding("quality", "INFO", "resources",
                                 f"{sub}/ {'present' if present else 'absent'}."))

    for md in skill_path.rglob("*.md"):
        if md.name == "SKILL.md" or _ignored(md):
            continue
        lines = md.read_text(encoding="utf-8", errors="replace").splitlines()
        if len(lines) > REFERENCE_TOC_THRESHOLD:
            head = "\n".join(lines[:40]).lower()
            if not ("table of contents" in head or "## contents" in head or head.count("](#") >= 3):
                findings.append(finding("quality", "MINOR", "reference_toc",
                                         f"{md.relative_to(skill_path)} is {len(lines)} lines with no TOC."))

    # Orphaned scripts: bundled but never named in any doc (dead weight / surprise).
    scripts_dir = skill_path / "scripts"
    if scripts_dir.is_dir():
        corpus = "\n".join(md.read_text(encoding="utf-8", errors="replace")
                           for md in skill_path.rglob("*.md") if not _ignored(md))
        for sc in sorted(scripts_dir.rglob("*")):
            if (sc.is_file() and not _ignored(sc)
                    and sc.suffix.lower() in CODE_SUFFIXES
                    and sc.name not in corpus):
                findings.append(finding("quality", "MINOR", "orphaned_script",
                                         f"{sc.relative_to(skill_path)} is bundled but never "
                                         "referenced in SKILL.md or references. Remove it or "
                                         "document when to run it."))


# ---- Script hygiene: compile + dependency disclosure ------------------------
def _declared_deps_text(skill_path, fm):
    text = (fm or {}).get("compatibility", "") or ""
    for req in list(skill_path.rglob("requirements*.txt")) + list(skill_path.rglob("pyproject.toml")):
        text += "\n" + req.read_text(encoding="utf-8", errors="replace")
    return text.lower()


def check_scripts(skill_path, fm, findings):
    declared = _declared_deps_text(skill_path, fm)
    stdlib = set(getattr(sys, "stdlib_module_names", set()))
    for py in skill_path.rglob("*.py"):
        if "__pycache__" in py.parts:
            continue
        rel = py.relative_to(skill_path)
        # Compile check (in-process, no execution). Write the byte-cache to a
        # throwaway temp path so we never touch the (possibly read-only) source dir.
        try:
            with tempfile.NamedTemporaryFile(suffix=".pyc", delete=True) as tf:
                py_compile.compile(str(py), cfile=tf.name, doraise=True)
        except py_compile.PyCompileError as e:
            findings.append(finding("quality", "MAJOR", "script_compile",
                                     f"{rel} does not compile: {str(e).splitlines()[0]}"))
            continue
        except OSError:
            pass  # could not write cache; skip compile check rather than crash
        # Undisclosed third-party imports.
        try:
            tree = ast.parse(py.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue
        roots = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                roots.update(a.name.split(".")[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                roots.add(node.module.split(".")[0])
        third_party = sorted(r for r in roots if r and r not in stdlib)
        for mod in third_party:
            # Match the import name or its distribution alias (cv2 -> opencv-python).
            names = {mod.lower(), IMPORT_ALIASES.get(mod, "").lower()} - {""}
            if not any(n in declared for n in names):
                findings.append(finding("quality", "MINOR", "undisclosed_dependency",
                                         f"{rel} imports third-party '{mod}' not declared in "
                                         "compatibility or a requirements file."))


# ---- Security ---------------------------------------------------------------
def _file_scan_text(f, suffix):
    """Return the text to security-scan for a file, or None to skip it. Handles
    code files, Jupyter notebooks (code cells only), and shebang scripts that have
    no recognized extension."""
    if suffix == ".ipynb":
        try:
            nb = json.loads(f.read_text(encoding="utf-8", errors="replace"))
        except (ValueError, OSError):
            return None
        cells = nb.get("cells", []) if isinstance(nb, dict) else []
        src = []
        for c in cells:
            if isinstance(c, dict) and c.get("cell_type") == "code":
                s = c.get("source", "")
                src.append("".join(s) if isinstance(s, list) else str(s))
        return "\n".join(src)
    if suffix in CODE_SUFFIXES:
        return f.read_text(encoding="utf-8", errors="replace")
    # No recognized code extension: scan only if it begins with a shebang, so a
    # `scripts/run` bash file isn't a blind spot, without full-reading binaries.
    try:
        with open(f, "r", encoding="utf-8", errors="replace") as fh:
            if fh.read(2) != "#!":
                return None
    except OSError:
        return None
    return f.read_text(encoding="utf-8", errors="replace")


def check_security(skill_path, findings):
    pattern_hits = 0
    for f in sorted(skill_path.rglob("*")):
        if not f.is_file() or _ignored(f):
            continue
        rel = f.relative_to(skill_path)
        suffix = f.suffix.lower()
        # Undeclared binaries/executables are a surprise regardless of content.
        if suffix in RISKY_BINARY_SUFFIXES:
            findings.append(finding("security", "REVIEW", "binary_artifact",
                                     f"{rel} is a binary/executable artifact ({suffix}); its "
                                     "contents can't be reviewed as text. Confirm why it ships."))
            continue
        text = _file_scan_text(f, suffix)
        if text is None:
            continue
        # Real secrets first (Blocker).
        for label, pat in SECRET_LITERALS.items():
            for ln_no, line in enumerate(text.splitlines(), 1):
                if re.search(pat, line):
                    findings.append(finding("security", "BLOCKER", f"secret:{label}",
                                             f"{rel}:{ln_no} looks like a hardcoded {label}. "
                                             "Remove it and rotate the credential."))
        for ln_no, line in enumerate(text.splitlines(), 1):
            for category, patterns in SECURITY_PATTERNS.items():
                for pat in patterns:
                    if re.search(pat, line):
                        pattern_hits += 1
                        findings.append(finding(
                            "security", "REVIEW", f"scan:{category}",
                            f"{rel}:{ln_no} matched {category} /{pat}/ -> `{line.strip()[:100]}`. "
                            "Confirm it's expected for the skill's stated purpose."))
    if pattern_hits == 0:
        findings.append(finding("security", "INFO", "scan",
                                 "No network / exec / destructive-FS / secret / obfuscation patterns found."))


def check_prose_security(skill_path, findings):
    """Scan SKILL.md and reference prose for instructions that would surprise a
    reader of the description: pipe-to-shell, exfiltration, raw IPs, encoded blobs.
    All REVIEW - a human confirms intent; external hosts are summarized as INFO."""
    hosts = set()
    for f in sorted(skill_path.rglob("*")):
        if not f.is_file() or _ignored(f) or f.suffix.lower() not in PROSE_SUFFIXES:
            continue
        # Dependency manifests aren't instructions; their version pins look like IPs.
        if f.name.lower().startswith("requirements") or f.suffix.lower() == ".lock":
            continue
        rel = f.relative_to(skill_path)
        text = f.read_text(encoding="utf-8", errors="replace")
        for ln_no, line in enumerate(text.splitlines(), 1):
            for category, patterns in PROSE_SECURITY_PATTERNS.items():
                for pat in patterns:
                    if re.search(pat, line, re.IGNORECASE):
                        findings.append(finding(
                            "security", "REVIEW", f"prose:{category}",
                            f"{rel}:{ln_no} instruction matches {category} -> "
                            f"`{line.strip()[:100]}`. Confirm the description discloses this."))
            for ip in IP_RE.findall(line):
                findings.append(finding(
                    "security", "REVIEW", "prose:ip_literal",
                    f"{rel}:{ln_no} hardcoded IP {ip} in prose -> `{line.strip()[:80]}`. "
                    "Confirm it's expected."))
            for blob in B64_RE.findall(line):
                if any(c in blob for c in "+/="):
                    findings.append(finding(
                        "security", "REVIEW", "prose:base64_blob",
                        f"{rel}:{ln_no} long base64-like blob ({len(blob)} chars) in prose. "
                        "Confirm it is not an encoded payload."))
            for host in URL_RE.findall(line):
                if host.lower() not in BENIGN_HOSTS:
                    hosts.add(host.lower())
    if hosts:
        findings.append(finding("security", "INFO", "prose:external_hosts",
                                 f"External hosts referenced in docs: "
                                 f"{', '.join(sorted(hosts)[:12])}."))


# ---- Instruction-review pointers (leads for the mandatory LLM-judge review) --
# Mechanical proxies (vague wording, long sections, ...) that point Claude at spots
# to inspect. They are ADVICE severity in the non-scored 'opportunity' dimension, so
# they never move the grade or gate by themselves. They are NOT the deliverable: the
# real instruction findings come from Claude's review (references/instruction-
# review.md), which confirms/promotes a pointer to a Major/Minor finding or discards
# it. That LLM-judge pass is the skill's core value, not these mechanical hits.
VAGUE_TERMS = ["appropriately", "as appropriate", "as needed", "as necessary",
               "accordingly", "properly", "correctly", "various", "and so on",
               "if needed", "etc."]
# Headings that signpost nothing about their content.
VAGUE_HEADINGS = {"notes", "misc", "miscellaneous", "other", "others", "stuff",
                  "more", "things", "extra", "additional", "general", "etc"}
# Cap on emitted pointers, so the list stays sharp instead of flooding.
MAX_OPPORTUNITIES = 8


def _sentences(text):
    # Strip code fences and inline code so code isn't counted as prose.
    prose = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    prose = re.sub(r"`[^`]*`", "", prose)
    # Drop markdown headers and list markers, and treat line breaks as boundaries
    # so a header never merges into the following sentence.
    out = []
    for line in prose.splitlines():
        s = re.sub(r"^\s*(#{1,6}\s+|[-*+]\s+|\d+\.\s+)", "", line)
        out.append(s)
    flat = "\n".join(out)
    parts = re.split(r"(?<=[.!?])\s+|\n{2,}", flat)
    return [p.strip() for p in parts if p.strip()]


def _vague_stats(text):
    """Distinct vague terms present and total occurrences, word-boundary matched
    so 'correctly' doesn't match inside another word."""
    low = text.lower()
    distinct, total = [], 0
    for t in VAGUE_TERMS:
        n = len(re.findall(r"(?<!\w)" + re.escape(t) + r"(?!\w)", low))
        if n:
            distinct.append(t)
            total += n
    return distinct, total


def _vague_density_hit(text):
    """True if a body/reference leans on vague terms: >=3 distinct terms AND at
    least ~1 occurrence per 100 lines, so length alone can't trip it."""
    distinct, total = _vague_stats(text)
    n_lines = max(1, len(text.splitlines()))
    return distinct if (len(distinct) >= 3 and total / n_lines * 100 >= 1.0) else []


def _vague_headings(text):
    out = []
    for line in text.splitlines():
        m = re.match(r"^#{1,6}\s+(.*\S)\s*$", line)
        if m and m.group(1).strip().lower().rstrip(":") in VAGUE_HEADINGS:
            out.append(m.group(1).strip())
    return out


def _redundant_sentences(text):
    """Sentences (>=6 words, to skip boilerplate) that appear near-verbatim more
    than once after normalization."""
    counts = {}
    for s in _sentences(text):
        key = re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", "", s.lower())).strip()
        if len(key.split()) >= 6:
            counts[key] = counts.get(key, 0) + 1
    return [k for k, n in counts.items() if n >= 2]


def check_opportunities(skill_path, fm, body, findings):
    opps = []  # collected, then prioritized and capped so the report isn't flooded

    def adv(area, msg):
        opps.append((area, msg))

    # --- Prompt clarity & instruction quality (body) ---
    if body:
        vague = _vague_density_hit(body)
        if vague:
            adv("clarity", f"Body leans on vague terms ({', '.join(vague[:5])}). "
                           "Consider replacing with concrete, testable instructions.")
        long_sents = [s for s in _sentences(body) if len(s.split()) > 45]
        if long_sents:
            adv("clarity", f"{len(long_sents)} very long sentence(s) (>45 words). "
                           "Consider splitting for readability; first: "
                           f"\"{long_sents[0][:60]}...\"")
        dups = _redundant_sentences(body)
        if dups:
            adv("clarity", f"{len(dups)} sentence(s) repeated near-verbatim. "
                           "Consider stating each instruction once.")
        for h in _vague_headings(body):
            adv("structure", f"Heading '{h}' is a vague signpost. Consider a heading "
                             "that names the content.")

    # --- Structure & conciseness (body) ---
    if body:
        lines = body.splitlines()
        # lines per top-level section
        sections, cur, cur_lines = [], None, 0
        for ln in lines:
            if re.match(r"^##\s+", ln):
                if cur is not None:
                    sections.append((cur, cur_lines))
                cur, cur_lines = ln[3:].strip(), 0
            else:
                cur_lines += 1
        if cur is not None:
            sections.append((cur, cur_lines))
        for title, n in sections:
            if n > 80:
                adv("structure", f"Section '{title}' is {n} lines. Consider moving "
                                 "detail into a references/ file.")
        n_body = len(lines)
        if BODY_SOFT_LINE_LIMIT * 0.8 <= n_body <= BODY_SOFT_LINE_LIMIT:
            adv("structure", f"Body is {n_body} lines, nearing the ~{BODY_SOFT_LINE_LIMIT} "
                             "soft cap. Consider trimming before it grows.")

    # --- Description / triggering sharpness ---
    if fm:
        desc = (fm.get("description") or "").strip()
        if desc:
            ds = _sentences(desc)
            if len(ds) == 1 and len(desc) > 180:
                adv("triggering", "Description is one long sentence. Consider 'what it "
                                  "does' then a separate 'use when ...' for sharper triggering.")
            cues_present = sum(1 for c in ("when", "whenever", "use this", "use when",
                                           "trigger", "if the user", "any time")
                               if c in desc.lower())
            if cues_present == 1:
                adv("triggering", "Description has a single trigger phrasing. Consider "
                                  "adding varied phrasings users might actually type.")
            if '"' not in desc and "'" not in desc:
                adv("triggering", "Description gives no example user phrasing. Consider "
                                  "quoting a phrase a user might say, to widen triggering.")

    # --- Examples & output specs (body) ---
    if body:
        low = body.lower()
        has_example = "example" in low
        has_fence = "```" in body
        if not has_example:
            adv("examples", "No worked example in the body. Consider adding one: it is "
                            "the strongest signal of correct usage.")
        produces_output = any(w in low for w in ("output", "format", "report",
                                                 "json", "template", "produce"))
        if produces_output and not has_fence and not (skill_path / "references").is_dir():
            adv("examples", "Skill mentions producing output but shows no concrete "
                            "format. Consider an input/output sample or a template.")

    # --- Reference files: detail lives here, so scan it for the same issues ---
    for md in sorted(skill_path.rglob("*.md")):
        if md.name == "SKILL.md" or _ignored(md):
            continue
        try:
            rtext = md.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        rel = md.relative_to(skill_path)
        rvague = _vague_density_hit(rtext)
        if rvague:
            adv("clarity", f"{rel}: leans on vague terms ({', '.join(rvague[:5])}). "
                           "Consider concrete, testable wording.")
        rlong = [s for s in _sentences(rtext) if len(s.split()) > 45]
        if rlong:
            adv("clarity", f"{rel}: {len(rlong)} very long sentence(s) (>45 words). "
                           "Consider splitting for readability.")
        for h in _vague_headings(rtext):
            adv("structure", f"{rel}: heading '{h}' is a vague signpost. Consider a "
                             "heading that names the content.")

    # Prioritize (highest-leverage area first) and cap so the list stays actionable.
    order = {"triggering": 0, "clarity": 1, "examples": 2, "structure": 3}
    opps.sort(key=lambda o: order.get(o[0], 9))
    for area, msg in opps[:MAX_OPPORTUNITIES]:
        findings.append(finding("opportunity", "ADVICE", f"opp:{area}", msg))


def compute_metrics(skill_path, fm, body, findings):
    # Composite score per dimension (heuristic: 100 minus severity penalties).
    dims = {"structure": 100, "quality": 100, "triggering": 100, "security": 100}
    review_hit = {d: 0 for d in dims}
    check_hit = {}  # (dimension, check) -> penalty already applied to that check
    for f in findings:
        d = f["dimension"]
        if d not in dims:
            continue
        sev = f["severity"]
        if sev == "REVIEW":
            review_hit[d] = min(REVIEW_PENALTY_CAP, review_hit[d] + SCORE_PENALTY["REVIEW"])
            continue
        pen = SCORE_PENALTY[sev]
        if pen == 0:
            continue
        # Count at most PER_CHECK_REPEAT_FACTOR hits of the same check at full
        # weight; further repeats of that same check add nothing.
        key = (d, f["check"])
        add = min(pen, max(0, PER_CHECK_REPEAT_FACTOR * pen - check_hit.get(key, 0)))
        if add <= 0:
            continue
        check_hit[key] = check_hit.get(key, 0) + add
        dims[d] = max(0, dims[d] - add)
    for d in dims:
        dims[d] = max(0, dims[d] - review_hit[d])
    overall = round(sum(dims.values()) / len(dims))
    # Gate-cap: averaging four dimensions otherwise dilutes a single fatal finding
    # (a hardcoded secret lands only in `security`, leaving a misleading A/B). Clamp
    # the overall so it can never outrank what the gate implies.
    sev_present = {f["severity"] for f in findings}
    if "BLOCKER" in sev_present:
        overall = min(overall, 40)
    elif "MAJOR" in sev_present:
        overall = min(overall, 79)
    elif "REVIEW" in sev_present:
        overall = min(overall, 89)
    grade = ("A" if overall >= 90 else "B" if overall >= 80 else
             "C" if overall >= 70 else "D" if overall >= 60 else "F")

    # Context footprint (token estimates, chars/4).
    def toks(s):
        return round(len(s) / CHARS_PER_TOKEN)
    fm_text = ""
    if fm:
        fm_text = (fm.get("name", "") or "") + (fm.get("description", "") or "")
    refs = {}
    for md in skill_path.rglob("*.md"):
        if md.name == "SKILL.md" or _ignored(md):
            continue
        refs[str(md.relative_to(skill_path))] = toks(md.read_text(encoding="utf-8", errors="replace"))
    total_bytes = sum(f.stat().st_size for f in skill_path.rglob("*")
                      if f.is_file() and not _ignored(f))

    return {
        "score": {"overall": overall, "grade": grade, **dims},
        "footprint": {
            "always_on_tokens_est": toks(fm_text),          # name+description, always in context
            "on_trigger_tokens_est": toks(body or ""),       # SKILL.md body, loaded when triggered
            "reference_tokens_est": refs,                    # loaded on demand
            "bundle_bytes": total_bytes,
        },
    }


# ---- LLM-judge instruction findings (folded in from a Claude-authored file) -----
def load_instruction_findings(path):
    """Load Claude-authored instruction-review findings (the mandatory LLM-judge
    pass) and normalize them into the script's finding schema, so they flow through
    scoring, the gate, the JSON, and downstream skill-fixer exactly like a script
    finding - this is how the LLM-judge results reach the fixer.

    Input: a JSON array of objects with `severity` (MAJOR|MINOR - instruction issues
    are mandatory fixes, never advisory), `message` (problem + where + why + fix), an
    optional `dimension` (a scored dimension; default 'quality'), and an optional
    `check` slug (auto-prefixed 'instruction:'). Raises ValueError on malformed input
    so a bad hand-authored file fails loudly instead of silently dropping findings.
    """
    data = json.loads(Path(path).read_text(encoding="utf-8-sig"))  # tolerate a BOM
    if not isinstance(data, list):
        raise ValueError("must be a JSON array of finding objects.")
    out = []
    for i, it in enumerate(data):
        if not isinstance(it, dict):
            raise ValueError(f"item {i}: not an object.")
        sev = str(it.get("severity", "")).upper()
        if sev not in ("MAJOR", "MINOR"):
            raise ValueError(f"item {i}: 'severity' must be MAJOR or MINOR.")
        msg = it.get("message")
        if not isinstance(msg, str) or not msg.strip():
            raise ValueError(f"item {i}: missing or empty 'message'.")
        dim = str(it.get("dimension", "quality")).lower()
        if dim not in SCORED_DIMENSIONS:
            raise ValueError(f"item {i}: 'dimension' must be one of {list(SCORED_DIMENSIONS)}.")
        check = str(it.get("check", "")).strip() or "finding"
        if not check.startswith("instruction:"):
            check = "instruction:" + check
        out.append(finding(dim, sev, check, msg.strip()))
    return out


# ---- Orchestration ----------------------------------------------------------
def review(skill_path, extra_findings=None):
    skill_path = Path(skill_path).resolve()
    findings = []
    if not skill_path.is_dir():
        findings.append(finding("structure", "BLOCKER", "path", f"Not a directory: {skill_path}"))
        return findings, {}, skill_path
    fm, body = check_structure(skill_path, findings)
    check_quality(skill_path, fm, body, findings)
    check_scripts(skill_path, fm, findings)
    check_security(skill_path, findings)
    check_prose_security(skill_path, findings)
    check_opportunities(skill_path, fm, body, findings)
    # Fold in the LLM-judge instruction findings (if any) before scoring, so the
    # gate, counts, and per-dimension score all reflect them.
    if extra_findings:
        findings.extend(extra_findings)
    metrics = compute_metrics(skill_path, fm, body, findings)
    return findings, metrics, skill_path


def summarize(findings):
    counts = {"BLOCKER": 0, "MAJOR": 0, "REVIEW": 0, "MINOR": 0, "INFO": 0, "ADVICE": 0}
    for f in findings:
        counts[f["severity"]] += 1
    # ADVICE rows are non-authoritative pointers, intentionally excluded from the gate.
    gate = ("FAILS SPEC" if counts["BLOCKER"] else
            "NEEDS FIXES" if counts["MAJOR"] else
            "NEEDS REVIEW" if counts["REVIEW"] else
            "CLEAN (static)")
    return counts, gate


def print_report(findings, metrics, skill_path):
    counts, gate = summarize(findings)
    print(f"\n=== Static review: {skill_path.name} ===")
    print(f"Path: {skill_path}")
    print(f"Gate: {gate}  (blocker={counts['BLOCKER']} major={counts['MAJOR']} "
          f"review={counts['REVIEW']} minor={counts['MINOR']} info={counts['INFO']})")
    if metrics:
        s = metrics["score"]
        fp = metrics["footprint"]
        print(f"Score: {s['overall']}/100 ({s['grade']})  "
              f"[structure {s['structure']}, quality {s['quality']}, "
              f"triggering {s['triggering']}, security {s['security']}]")
        print(f"Footprint: ~{fp['always_on_tokens_est']} always-on tok, "
              f"~{fp['on_trigger_tokens_est']} on-trigger tok, "
              f"{fp['bundle_bytes']} bytes total\n")
    for sev in ("BLOCKER", "MAJOR", "REVIEW", "MINOR", "INFO"):
        rows = [f for f in findings if f["severity"] == sev]
        if not rows:
            continue
        print(f"-- {sev} --")
        for f in rows:
            print(f"  [{f['dimension']}/{f['check']}] {f['message']}")
        print()
    advice = [f for f in findings if f["severity"] == "ADVICE"]
    if advice:
        print("-- INSTRUCTION-REVIEW POINTERS (leads to confirm in the LLM review; not findings) --")
        for f in advice:
            area = f["check"].split(":", 1)[-1]
            print(f"  [{area}] {f['message']}")
        print()


def main():
    ap = argparse.ArgumentParser(description="Static review of an Agent Skill.")
    ap.add_argument("skill_path", help="Path to the skill folder")
    ap.add_argument("--json", dest="json_out", help="Write findings + metrics as JSON")
    ap.add_argument("--fail-on", dest="fail_on", choices=("blocker", "major", "review"),
                    default="blocker",
                    help="Exit non-zero if any finding is at or above this severity "
                         "(default: blocker). Use 'major' or 'review' for stricter CI gating.")
    ap.add_argument("--instruction-findings", dest="instr_file",
                    help="JSON array of LLM-judge instruction findings to fold into the "
                         "review (severity MAJOR/MINOR, message, optional dimension/check). "
                         "They count toward the score, gate, and JSON, so skill-fixer "
                         "ingests them like any other finding.")
    args = ap.parse_args()

    extra = []
    if args.instr_file:
        try:
            extra = load_instruction_findings(args.instr_file)
        except (ValueError, OSError, json.JSONDecodeError) as e:
            print(f"Error in --instruction-findings: {e}", file=sys.stderr)
            sys.exit(2)

    findings, metrics, skill_path = review(args.skill_path, extra_findings=extra)
    # Deterministic order: severity, then dimension/check/message, so reports are
    # reproducible across machines (rglob walk order is filesystem-dependent).
    findings.sort(key=lambda f: (SEVERITY_ORDER[f["severity"]], f["dimension"],
                                 f["check"], f["message"]))
    print_report(findings, metrics, skill_path)

    if args.json_out:
        counts, gate = summarize(findings)
        Path(args.json_out).write_text(json.dumps(
            {"skill": skill_path.name, "path": str(skill_path), "gate": gate,
             "reviewer_version": REVIEWER_VERSION,
             "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
             "counts": counts, "metrics": metrics, "findings": findings}, indent=2))
        print(f"JSON written to {args.json_out}")

    threshold = SEVERITY_ORDER[args.fail_on.upper()]
    sys.exit(1 if any(SEVERITY_ORDER[f["severity"]] <= threshold for f in findings) else 0)


if __name__ == "__main__":
    main()
