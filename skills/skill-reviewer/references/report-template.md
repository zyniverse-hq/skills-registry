# Review Report Template

Produce the report in this exact structure. Keep findings concrete and each one
paired with a fix. Use the severities defined in SKILL.md.

```markdown
# Skill Review: <skill-name>

**Path:** <path>
**Reviewed:** <date>
**Reviewer:** review_skill.py v<reviewer_version>, generated <generated_at>  (from the JSON report)
**Overall verdict:** <Pass | Pass with fixes | Fail>
**Static gate:** <CLEAN | NEEDS REVIEW | NEEDS FIXES | FAILS SPEC>  (blocker/major/review/minor counts)
**Score:** <overall>/100 (<grade>) — structure/quality/triggering/security
**Footprint:** ~<n> always-on tokens, ~<n> on-trigger tokens, <n> bytes

## Summary

<2-3 sentences: what the skill does, the headline finding, and the bottom line.>

| Dimension            | Verdict            | Notes                          |
|----------------------|--------------------|--------------------------------|
| Structure / spec     | Pass / Fail        | <one line>                     |
| Quality              | Pass / Fixes / Fail| <one line>                     |
| Triggering           | Pass / Fixes / Fail| <one line>                     |
| Security             | Pass / Fail        | <one line>                     |

## Findings

Instruction-review findings appear here too, tagged `[instruction]`, as Major or
Minor — they are mandatory fixes, not advice.

### Blockers
- **[dimension] <title>** - <what's wrong and why it matters>. **Fix:** <action>.
  (Omit the section if none; say "None.")

### Major
- **[dimension] <title>** - <detail>. **Fix:** <action>.

### Review (confirm in context)
- **[dimension] <title>** - <flagged code pattern, prose instruction, or binary
  artifact; file:line>. **Verdict:** justified by the skill's stated purpose /
  escalate to Blocker.

### Minor
- **[dimension] <title>** - <detail>. **Fix:** <action>.

## Instruction review (LLM-as-judge)

<The core qualitative pass: how the skill's instructions hold up as a prompt. State
which lenses surfaced problems — gaps, ambiguity, contradictions, description-vs-body
mismatch, misdirection, output contract — and your overall read of instruction
quality. Every concrete issue is a Major/Minor finding listed under Findings above,
each with a required fix; these are mandatory and gate the verdict. If the
instructions are genuinely sound, say so explicitly.>

## Triggering assessment

<The would-trigger / would-not-trigger queries you reasoned through, and whether
the current description handles them. Note if the quantitative optimizer was not
run and why.>

## Security assessment

<Give a verdict on every security signal - justified by the stated purpose, or a
surprise. Cover each kind that fired:
- **Code patterns** (`scan:*`) - network / exec / destructive-FS / secret /
  obfuscation hits in code, with file:line.
- **Prose / instructions** (`prose:*`) - pipe-to-shell, exfiltration phrasing,
  hardcoded IPs, or encoded blobs in SKILL.md or references, plus the external-host
  summary. A skill is followed as instructions, so its prose is part of the surface.
- **Binaries** (`binary_artifact`) - opaque/executable files that can't be reviewed
  as text; say why each ships or flag it.
- **Hardcoded secrets** (`secret:*`) - always a Blocker; name the file:line and the
  remove-and-rotate instruction.
State the principle-of-lack-of-surprise conclusion across all of the above.>

## Recommended next steps

<Ordered list of the highest-leverage fixes.>
```
