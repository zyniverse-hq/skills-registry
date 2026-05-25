#!/usr/bin/env python3
"""
match_question.py — deterministic question matcher for the investor-form-filler skill.

Given a new investor form question, finds the closest canonical Q&A block in a
topic-tagged markdown file. Uses weighted token overlap with tag bonuses, which is
more robust than plain keyword matching when blocks share vocabulary.

Stdlib only. No installs.

Expected file format (any markdown):

    ### Q-T1: Founder names and roles
    **Tags:** founders, team, leadership
    **Answer:**
    - ...

Usage:
    python3 match_question.py --question "What's your moat?" --truth path/to/company-truth.md
    python3 match_question.py --questions-json '[{"q": "..."}, ...]' --truth ...
    python3 match_question.py --question "..." --top 3 --verbose

Output is JSON with the top N matches per question.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# ---- Tokenisation ----------------------------------------------------------

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "doing",
    "will", "would", "could", "should", "may", "might", "must", "can",
    "of", "in", "on", "at", "to", "for", "with", "by", "from", "into",
    "and", "or", "but", "if", "then", "than", "so", "as", "that", "this",
    "what", "which", "who", "whom", "whose", "where", "when", "why", "how",
    "you", "your", "yours", "we", "our", "ours", "us", "i", "me", "my",
    "they", "them", "their", "theirs", "it", "its",
    "tell", "describe", "explain", "share", "give", "list", "provide",
    "please", "thanks", "thank", "kindly", "briefly", "shortly",
    "yes", "no", "not", "n",
}

SUFFIXES = ("ing", "ed", "er", "est", "tion", "ation", "ion", "ness",
            "ment", "ity", "ize", "ise", "ly", "s")


def stem(word: str) -> str:
    """Lightweight suffix stripping — not Porter, just enough to fold related forms."""
    for suf in SUFFIXES:
        if len(word) > len(suf) + 2 and word.endswith(suf):
            return word[: -len(suf)]
    return word


def tokenize(text: str) -> List[str]:
    """Lowercase, strip punctuation, drop stopwords, light stem."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    tokens = text.split()
    tokens = [t for t in tokens if t not in STOPWORDS and len(t) > 1]
    return [stem(t) for t in tokens]


# ---- Q&A loader ------------------------------------------------------------

BLOCK_HEADER = re.compile(r"^###\s+(Q-?[A-Z]?\d+):\s*(.+?)$")
TAGS_LINE = re.compile(r"^\*\*Tags:\*\*\s*(.+?)$")


def parse_truth_file(path: Path) -> List[Dict]:
    """
    Parse a markdown Q&A bank into structured blocks.

    Each block must look like:
        ### Q-T1: Question heading
        **Tags:** tag1, tag2, tag3
        **Answer:**
        ... body ...

    Returns a list of dicts: [{id, question, tags, answer_start_line}, ...]
    """
    lines = path.read_text(encoding="utf-8").split("\n")
    blocks: List[Dict] = []
    current: Dict | None = None

    for i, line in enumerate(lines):
        m = BLOCK_HEADER.match(line.strip())
        if m:
            if current is not None:
                blocks.append(current)
            current = {
                "id": m.group(1),
                "question": m.group(2).strip(),
                "tags": [],
                "answer_start_line": None,
            }
            continue

        if current is None:
            continue

        m = TAGS_LINE.match(line.strip())
        if m:
            current["tags"] = [t.strip() for t in m.group(1).split(",") if t.strip()]
            continue

        if line.strip().startswith("**Answer") and current["answer_start_line"] is None:
            current["answer_start_line"] = i + 1
            continue

    if current is not None:
        blocks.append(current)
    return blocks


# ---- Scoring ---------------------------------------------------------------

def score_match(query_tokens: List[str], block: Dict) -> Tuple[float, Dict]:
    """
    Score how well a query matches a canonical block.

      * Tag tokens carry 2× weight (curated, high signal)
      * Question-text tokens carry 1× weight
      * +0.10 bonus if any tag phrase appears verbatim in the query
      * +0.15 bonus if >50% of the block's tag tokens hit
    """
    q_tokens = set(query_tokens)
    if not q_tokens:
        return 0.0, {}

    tag_tokens = set(tokenize(" ".join(block["tags"])))
    question_tokens = set(tokenize(block["question"]))

    matched_in_tags = q_tokens & tag_tokens
    matched_in_question = q_tokens & question_tokens
    matched_in_either = matched_in_tags | matched_in_question

    base_score = len(matched_in_either) / len(q_tokens)

    bonus = 0.0
    q_text_normalised = " " + " ".join(query_tokens) + " "
    for tag in block["tags"]:
        tag_normalised = " " + " ".join(tokenize(tag)) + " "
        if tag_normalised.strip() and tag_normalised in q_text_normalised:
            bonus += 0.10
            break  # only count once

    if tag_tokens and len(matched_in_tags) / len(tag_tokens) > 0.5:
        bonus += 0.15

    return base_score + bonus, {
        "matched_in_tags": sorted(matched_in_tags),
        "matched_in_question": sorted(matched_in_question),
        "base_score": round(base_score, 3),
        "bonus": round(bonus, 3),
    }


def match_one(question_text: str, blocks: List[Dict], top: int = 3) -> List[Dict]:
    q_tokens = tokenize(question_text)
    scored: List[Dict] = []
    for block in blocks:
        score, debug = score_match(q_tokens, block)
        scored.append({
            "id": block["id"],
            "canonical_question": block["question"],
            "tags": block["tags"],
            "score": round(score, 3),
            "debug": debug,
        })
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top]


# ---- CLI -------------------------------------------------------------------

def main() -> None:
    p = argparse.ArgumentParser(description="Match form questions to canonical Q&A blocks")
    p.add_argument("--question", type=str, help="Single question to match")
    p.add_argument("--questions-json", type=str,
                   help='JSON list: [{"q": "..."}, ...] or ["q1", "q2", ...]')
    p.add_argument("--truth", type=str, required=True,
                   help="Path to the canonical Q&A markdown file")
    p.add_argument("--top", type=int, default=3, help="Return top N matches per question")
    p.add_argument("--verbose", action="store_true", help="Include scoring debug info")
    args = p.parse_args()

    truth_path = Path(args.truth)
    if not truth_path.exists():
        print(json.dumps({"error": f"Truth file not found: {args.truth}"}), file=sys.stderr)
        sys.exit(1)

    blocks = parse_truth_file(truth_path)
    if not blocks:
        print(json.dumps({"error": "No Q&A blocks parsed from truth file"}), file=sys.stderr)
        sys.exit(1)

    def strip_debug(matches):
        if not args.verbose:
            for m in matches:
                m.pop("debug", None)
        return matches

    if args.question:
        matches = strip_debug(match_one(args.question, blocks, top=args.top))
        print(json.dumps({"input_question": args.question, "matches": matches,
                          "canonical_blocks_total": len(blocks)}, indent=2))
        return

    if args.questions_json:
        try:
            questions = json.loads(args.questions_json)
        except json.JSONDecodeError as e:
            print(json.dumps({"error": f"Invalid JSON: {e}"}), file=sys.stderr)
            sys.exit(1)

        results = []
        for item in questions:
            q_text = item.get("q") if isinstance(item, dict) else str(item)
            if not q_text:
                continue
            results.append({"question": q_text,
                            "matches": strip_debug(match_one(q_text, blocks, top=args.top))})
        print(json.dumps({"results": results, "canonical_blocks_total": len(blocks)}, indent=2))
        return

    print(json.dumps({"error": "Pass either --question or --questions-json"}), file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
