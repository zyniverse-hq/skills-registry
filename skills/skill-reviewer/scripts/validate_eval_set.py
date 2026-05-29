#!/usr/bin/env python3
"""
validate_eval_set.py - Sanity-check a trigger eval set before measuring trigger rate.

The eval set is a JSON array of {"query": str, "should_trigger": bool}. Claude
drafts the queries (that needs judgement); this script checks they are well-formed
and balanced, because bad eval queries produce meaningless trigger metrics.

Checks: schema validity, should/should-not balance (aim ~8-10 each), duplicates,
and weak queries (too short or too generic to test triggering meaningfully).

Usage:
    python3 validate_eval_set.py <eval-set.json>
"""

import argparse
import json
import re
import sys
from pathlib import Path

MIN_PER_CLASS = 8
MIN_QUERY_CHARS = 25
GENERIC_QUERIES = {"format this data", "extract text from pdf", "create a chart",
                   "fix this", "help me", "review this"}


def validate(items):
    problems, warnings = [], []
    if not isinstance(items, list) or not items:
        return ["Eval set must be a non-empty JSON array."], []

    seen = set()
    pos = neg = 0
    for i, it in enumerate(items):
        where = f"item {i}"
        if not isinstance(it, dict):
            problems.append(f"{where}: not an object.")
            continue
        q = it.get("query")
        st = it.get("should_trigger")
        if not isinstance(q, str) or not q.strip():
            problems.append(f"{where}: missing/empty 'query'.")
            continue
        if not isinstance(st, bool):
            problems.append(f"{where}: 'should_trigger' must be true/false.")
        key = q.strip().lower()
        if key in seen:
            warnings.append(f"{where}: duplicate query -> {q[:50]!r}")
        seen.add(key)
        if st is True:
            pos += 1
        elif st is False:
            neg += 1
        if len(q.strip()) < MIN_QUERY_CHARS:
            warnings.append(f"{where}: very short ({len(q.strip())} chars); add realistic detail.")
        if key in GENERIC_QUERIES or re.fullmatch(r"[\w\s]{0,20}", key):
            warnings.append(f"{where}: generic query {q[:50]!r}; weak triggering test.")

    if pos < MIN_PER_CLASS:
        warnings.append(f"Only {pos} should-trigger queries; aim for >= {MIN_PER_CLASS}.")
    if neg < MIN_PER_CLASS:
        warnings.append(f"Only {neg} should-not-trigger queries; aim for >= {MIN_PER_CLASS} "
                        "(the tricky near-misses are the valuable ones).")
    return problems, warnings


def main():
    ap = argparse.ArgumentParser(description="Validate a trigger eval set JSON.")
    ap.add_argument("eval_set", help="Path to the eval-set JSON file")
    args = ap.parse_args()

    try:
        items = json.loads(Path(args.eval_set).read_text())
    except Exception as e:  # noqa: BLE001
        print(f"Could not read JSON: {e}")
        sys.exit(1)

    problems, warnings = validate(items)
    pos = sum(1 for it in items if isinstance(it, dict) and it.get("should_trigger") is True)
    neg = sum(1 for it in items if isinstance(it, dict) and it.get("should_trigger") is False)
    print(f"Eval set: {len(items)} queries ({pos} should-trigger, {neg} should-not-trigger)")
    for p in problems:
        print(f"  ERROR: {p}")
    for w in warnings:
        print(f"  WARN:  {w}")
    if not problems and not warnings:
        print("  OK: well-formed and balanced.")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
