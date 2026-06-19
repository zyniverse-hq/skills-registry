#!/usr/bin/env python3
"""
verify_fixes.py - Confirm a fix pass improved a skill and did not regress it.

Compares a "before" skill-reviewer JSON report against a freshly-run "after"
review of the (now-fixed) skill. Confirms the target findings cleared and that no
new finding appeared and the gate/score did not get worse. Use this at the end of
a skill-fixer run so the branch is never left in a worse state.

Instruction findings (check `instruction:*`) are LLM-judged, so the script cannot
regenerate them. Re-judge the fixed skill and pass the result via
--after-instruction-findings so they compare like any other finding. Without it, a
before report that had instruction findings is reported INCOMPLETE - they are never
silently treated as cleared.

Exit code: 0 if no regression and nothing left unverified; 1 on a regression or an
incomplete (un-re-judged) instruction comparison.

Usage:
    python3 verify_fixes.py --before before.json --skill <folder> \
        --reviewer <path/to/review_skill.py> [--after-json after.json] \
        [--after-instruction-findings after-instr.json]
"""

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

GATE_RANK = {"FAILS SPEC": 0, "NEEDS FIXES": 1, "NEEDS REVIEW": 2, "CLEAN (static)": 3}
PROBLEM = {"BLOCKER", "MAJOR", "MINOR"}


def review(reviewer, skill, out, instr=None):
    cmd = [sys.executable, str(reviewer), str(skill), "--json", str(out)]
    if instr:
        cmd += ["--instruction-findings", str(instr)]
    subprocess.run(cmd, capture_output=True, text=True)
    if not Path(out).exists():
        raise SystemExit("Re-review failed to produce JSON.")
    return json.loads(Path(out).read_text())


def key(f):
    return (f["check"], f["message"])


def is_instruction(f):
    return f.get("check", "").startswith("instruction:")


def main():
    ap = argparse.ArgumentParser(description="Verify a fix pass did not regress a skill.")
    ap.add_argument("--before", required=True, help="pre-fix review JSON")
    ap.add_argument("--skill", required=True)
    ap.add_argument("--reviewer", required=True, help="path to review_skill.py")
    ap.add_argument("--after-json", default=None,
                    help="where to write the fresh review JSON (default: an OS temp file).")
    ap.add_argument("--after-instruction-findings", dest="after_instr",
                    help="JSON of instruction findings re-judged on the FIXED skill, folded "
                         "into the 'after' review so instruction:* findings compare like any "
                         "other. Pass an empty array ([]) if none remain. Omit only when the "
                         "before report had no instruction findings.")
    args = ap.parse_args()

    after_json = args.after_json or str(Path(tempfile.gettempdir()) / "skill-after-review.json")
    before = json.loads(Path(args.before).read_text())
    after = review(args.reviewer, Path(args.skill).resolve(), after_json, args.after_instr)

    rejudged = bool(args.after_instr)
    before_has_instr = any(is_instruction(f) for f in before.get("findings", []))
    # Instruction findings live only in a re-judged report. If we didn't re-judge,
    # the after run has none, so they can't be compared - exclude them from the
    # accounting (no false "cleared") and flag the run INCOMPLETE instead of "OK".
    incomplete = before_has_instr and not rejudged

    def problems(report):
        out = set()
        for f in report.get("findings", []):
            if f["severity"] not in PROBLEM:
                continue
            if incomplete and is_instruction(f):
                continue
            out.add(key(f))
        return out

    b_problems = problems(before)
    a_problems = problems(after)
    cleared = b_problems - a_problems
    new = a_problems - b_problems

    b_gate = GATE_RANK.get(before.get("gate"), -1)
    a_gate = GATE_RANK.get(after.get("gate"), -1)
    b_score = (before.get("metrics", {}).get("score", {}) or {}).get("overall", 0)
    a_score = (after.get("metrics", {}).get("score", {}) or {}).get("overall", 0)
    # Gate/score only compare when both reports are on the same basis; if the before
    # report had instruction findings we didn't re-judge, skip that part of the check.
    note = "  (instruction findings not re-judged; gate/score not comparable)" if incomplete else ""

    print(f"\n=== Fix verification: {after.get('skill')} ===")
    print(f"Gate: {before.get('gate')} -> {after.get('gate')}{note}")
    print(f"Score: {b_score} -> {a_score}")
    print(f"Cleared {len(cleared)} problem(s); {len(new)} new problem(s).")
    if cleared:
        print("\n-- cleared --")
        for c, m in sorted(cleared):
            print(f"  + [{c}] {m}")
    if new:
        print("\n-- NEW (regression) --")
        for c, m in sorted(new):
            print(f"  ! [{c}] {m}")
    if incomplete:
        n = sum(1 for f in before.get("findings", [])
                if is_instruction(f) and f["severity"] in PROBLEM)
        print(f"\n-- INCOMPLETE --\n  {n} instruction finding(s) not re-judged. Re-judge the "
              "fixed skill and re-run with --after-instruction-findings; they are not "
              "treated as cleared.")

    regressed = bool(new) or (not incomplete and (a_gate < b_gate or a_score < b_score))
    if regressed:
        result = "REGRESSION DETECTED"
    elif incomplete:
        result = "INCOMPLETE (instruction findings unverified)"
    else:
        result = "OK (no regression)"
    print("\nRESULT:", result, "\n")
    sys.exit(1 if (regressed or incomplete) else 0)


if __name__ == "__main__":
    main()
