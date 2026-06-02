# Resume Hiring Manager — Change Log & Impact Report

**Skill:** `resume-hiring-manager`
**Previous version:** 1.0.0
**Updated version:** 2.0.0
**Updated on:** 28 May 2026
**Updated by:** Zysk Tech

---

## Overview

Version 1.0.0 had the right concept but was not production-ready. It collected a resume from the user but never used it, produced final scores that could not be explained, opened interviews abruptly without any warm-up, and gave no visual progress to the user during the session.

Version 2.0.0 closes all 20 identified gaps — 4 Critical, 5 High, 6 Medium, and 5 Minor — and transforms the skill into a consistent, professional, fully structured mock interview experience ready for real users.

---

## What Changed at a Glance

| Category | Gaps found | Gaps fixed | Status |
|---|---|---|---|
| Critical | 4 | 4 | All fixed |
| High | 5 | 5 | All fixed |
| Medium | 6 | 6 | All fixed |
| Minor | 5 | 5 | All fixed |
| **Total** | **20** | **20** | **Production ready** |

---

## Critical Fixes

These were breaking issues — the skill could not be trusted in production without them.

---

### C1 — Resume is now actually read and used

**Before:**
The skill asked the user to paste their resume but gave the AI no instruction on what to do with it. In practice, questions were generic and could apply to any candidate regardless of background.

**After:**
Step 2 now explicitly instructs the AI to extract specific resume content before writing a single question:
- Last 3–5 roles (company, title, duration)
- Specific projects and achievements with numbers
- Key skills, tools, and certifications
- Gaps, short tenures, or career pivots

Every question must now reference at least one specific detail from the resume. Generic questions are explicitly prohibited.

**Impact:** Interviews feel tailored and personal rather than off-the-shelf. Users immediately notice their real experience is being acknowledged. This is the single most important differentiator from generic interview prep tools.

---

### C2 — Final score is now fully defined and explainable

**Before:**
8 questions were scored out of 10, but the final "hireability score" was out of 100. No formula existed. The AI invented a different calculation every session, making scores meaningless and inconsistent.

**After:**
A clear weighted scoring system is now defined:

| Question type | Count | Weight | Max points |
|---|---|---|---|
| Warm-up | 1 | × 0.5 | 5 |
| Technical | 5 | × 1.0 | 50 |
| Behavioural | 3 | × 1.5 | 45 |
| **Total** | | | **100** |

Behavioural questions carry more weight because they reveal how someone actually operates under pressure — harder to fake than technical knowledge.

**Impact:** Scores are now reproducible, explainable, and defensible. If a user asks "why did I get 67?", the AI can walk through the math. Trust in the tool increases significantly.

---

### C3 — Interview now opens like a real interview

**Before:**
The skill jumped straight from collecting inputs to asking the hardest technical question, with no introduction, no context-setting, and no warm-up. This felt robotic and unnatural.

**After:**
Step 3 defines a full interview opening:
- The AI introduces itself with a name and title appropriate to the company type
- The company is fictional but plausible (e.g., a startup interviewer works at a growth-stage tech company, not a corporation)
- Expectations for the session are set clearly
- A warm-up question ("Tell me about yourself") is asked first before scored rounds begin

**Impact:** The experience now feels like a real interview from the first message. Users settle into the format naturally rather than being thrown into high-stakes questions with no context.

---

### C4 — Users can always see where they are in the interview

**Before:**
There was no progress indicator. Users had no idea if they were halfway through, near the end, or just starting. This created anxiety and a sense of disorientation.

**After:**
Every question now carries a visible label:
- `Round 1 — Question 3 of 5`
- `Round 2 — Behavioural Question 2 of 3`

**Impact:** Users feel in control. They can pace their effort (save energy for the behavioural round), and the structure reinforces that this is a serious, organised interview — not a random Q&A.

---

## High Fixes

These significantly reduced quality and realism without being outright breaking.

---

### H1 — Push-back mechanics are now defined

**Before:**
The rules said "push back if the user answers vaguely" but gave no definition of vague, no script for how to push back, and no limit on how many follow-ups to allow.

**After:**
- A clear trigger: if the answer lacks specifics, the AI says exactly: *"I want to push on that — can you give me a specific example? What exactly did you do, and what was the measurable outcome?"*
- One follow-up maximum
- If still vague after the second answer, the AI scores it accordingly, explains that lack of specifics caused the lower score, and moves on

**Impact:** The interview stays realistic without becoming adversarial or stuck in loops. Users learn the exact habit interviewers dislike — vague, un-evidenced answers — and feel the consequence of it in their score.

---

### H2 — Study plan is now structured and actionable

**Before:**
The closing report promised "a short study plan for gap areas" with no definition of short, no format, and no timeframe. Output varied wildly from a single sentence to an unstructured paragraph.

**After:**
The study plan is a defined table with four columns:

| Gap area | What to study | Resource type | Timeframe |
|---|---|---|---|
| [Topic] | [Specific sub-topic] | [Book / course / practice / cases] | [e.g. 3 days] |

Followed by a single "next step" sentence telling the user when to re-run the interview.

**Impact:** Users leave the session with a concrete action plan they can actually follow, not vague advice. The resource type column (book, course, practice problems) means they do not have to figure out how to study — just where to start.

---

### H3 — Seniority level now changes the interview

**Before:**
The skill collected JUNIOR / MID / SENIOR / LEAD but never used that information. A junior candidate and a principal engineer would receive the same questions.

**After:**
Full calibration table added:

| Level | Question focus |
|---|---|
| JUNIOR | Fundamentals, learning mindset, first principles |
| MID | Ownership, execution, cross-team collaboration |
| SENIOR | Systems thinking, architectural decisions, influencing without authority |
| LEAD | Org strategy, hiring and culture, business impact of technical decisions |

**Impact:** Every seniority tier now has a distinctly different interview. A junior candidate is not intimidated by strategy questions above their level; a senior candidate is not bored by questions they solved five years ago.

---

### H4 — Interviewer persona is now grounded in company type

**Before:**
The interviewer persona was just "someone with 8+ years of experience." There was no company culture, no personality, no sense of what the hiring manager actually cared about.

**After:**
Full calibration table added across 7 company types:

| Company type | What they prioritise |
|---|---|
| Startup / scale-up | Speed, ownership, ambiguity tolerance |
| Large enterprise | Process, governance, stakeholder management |
| Consultancy | Client management, delivery under pressure |
| Government / public sector | Risk management, documentation, long timelines |
| Healthcare / non-profit | Mission alignment, compliance, non-technical communication |
| Agency | Juggling projects, client relationships, deadlines |
| Fintech / financial services | Precision, regulatory awareness, data integrity |

**Impact:** A startup interviewer and an enterprise interviewer now feel genuinely different. Users prepare for the actual culture they will walk into, not a generic average of all cultures.

---

### H5 — Behavioural scoring now has clear criteria

**Before:**
The skill said "score how well the user structures their answer using STAR" with no definition of what strong or weak looks like for each component.

**After:**
A full STAR scoring rubric defines strong vs. weak for every component:

| Component | Strong | Weak |
|---|---|---|
| Situation | Specific, real, sets scene clearly | Vague, hypothetical, or over-explained |
| Task | Personal responsibility, not the team's | Blurs individual vs. team ownership |
| Action | Specific steps with reasoning, uses "I" | Generic — no specifics on what or why |
| Result | Measurable outcome or business impact | "It went well" with no data |

A 9–10 requires all four to be strong. Points are deducted per weak component.

**Impact:** Behavioural scores are now consistent across sessions. Two different users giving the same quality of answer will receive the same score range. The rubric also becomes a teaching tool — users can see exactly which component of their answer failed.

---

## Medium Fixes

These affected polish and professional consistency.

---

### M1 — Category corrected

**Before:** `business-sales`
**After:** `career`

**Impact:** The skill now appears in the correct category in any directory or marketplace listing.

---

### M2 — Output format standardised

**Before:** No defined format for questions, per-answer feedback, or the final report. Output structure varied every session.

**After:**
- Per-answer feedback follows a fixed four-part format: score, acknowledgment, top-candidate example, and the one thing to change
- Final report follows a fixed five-section template: score + verdict, three weakest answers, three questions to rehearse, study plan table, and next step
- Questions are always labelled with their round and position

**Impact:** Users get a consistent, professional experience every time. The output can be saved and shared without looking like it was improvised.

---

### M3 — Company type options expanded

**Before:** 3 examples (SaaS startup, Fortune 500 fintech, mid-size agency)
**After:** 7 defined types covering the full range of where people work

**Impact:** Users who work in government, healthcare, or consultancy are no longer forced to pick an irrelevant category or leave it blank. Their interview now reflects their actual target environment.

---

### M4 — Graceful session controls added

**Before:** No way to pause, stop, or restart mid-interview. A user who quit early received nothing.

**After:** Four commands defined:

| Command | What it does |
|---|---|
| `stop` / `end interview` | Delivers a partial report for all answered questions |
| `skip` | Skips current question, scores it 0, moves on |
| `restart` | Restarts from beginning with same inputs |
| `redo` | Re-answers the most recent question, replaces previous score |

**Impact:** Users feel in control of their session. If something comes up or they are unhappy with an answer, they have options. Partial reports mean even an incomplete session delivers value.

---

### M5 — Regional interview style support added

**Before:** One generic interview style applied to everyone regardless of location.

**After:** Optional region input with style adjustments for US, UK, India, and Australia.

| Region | Style |
|---|---|
| US | Quantifiable results, direct storytelling |
| UK | Competency-based, formal STAR phrasing |
| India | Technical depth mixed with relational questions |
| Australia | Relaxed but professional, cultural fit emphasis |

**Impact:** A user preparing for a UK civil service interview and one preparing for a US tech company interview now get meaningfully different preparation.

---

### M6 — "30-minute interview" framing removed

**Before:** The skill described itself as simulating a "30-minute interview," creating a false expectation of a timed session.
**After:** This framing is removed. The structure is described by question count (9 questions across 2 rounds), which is accurate.

**Impact:** Users are not confused about timing. Expectations match the actual experience.

---

## Minor Fixes

Small rough edges, all resolved.

---

### N1 — Skill description updated to trigger on natural language

**Before:** Passive description that only matched formal requests like "run a mock interview."

**After:** Description now includes everyday phrasings: "I have an interview on Friday", "quiz me", "prep me", "am I hireable", "help me practice."

**Impact:** Users do not need to know the skill exists or use specific keywords. It triggers naturally from how people actually talk about interview prep.

---

### N2 — Tags expanded

**Before:** 5 tags — resume, interview, mock-interview, career, hiring
**After:** 10 tags — added job-prep, career-coaching, feedback, scoring, practice

**Impact:** The skill is more discoverable in any search or filtering system.

---

### N3 — Scoring anchors added via STAR rubric examples

**Before:** No examples of what a strong or weak answer looks like. The AI calibrated on instinct, leading to score variance.

**After:** The STAR rubric includes concrete descriptions of strong vs. weak for each of the four components, giving the AI clear anchors to score against.

**Impact:** Two sessions with the same quality of answer will return the same score. Scoring is now calibrated, not improvised.

---

### N4 — Acknowledgment step added before critique

**Before:** The AI moved directly from the user's answer to the score and criticism with no transition. This felt cold and robotic.

**After:** The per-answer format now requires one sentence acknowledging the answer before any critique. For example: "You touched on the right area here" or "There's a strong instinct in that answer."

**Impact:** The interaction feels more like a real professional coaching conversation. Users are more receptive to tough feedback when they feel heard first.

---

### N5 — Version bumped to 2.0.0

**Before:** Version 1.0.0
**After:** Version 2.0.0

**Impact:** Teams can track which version is deployed. The major version bump signals that this is a substantial rewrite, not a patch.

---

## Files Changed

| File | Change type | Description |
|---|---|---|
| `skills/resume-hiring-manager/SKILL.md` | Modified | Full rewrite from v1.0.0 to v2.0.0 — all 20 gaps addressed |
| `skills/resume-hiring-manager/CHANGES.md` | Created | This document |

---

## Before vs. After Summary

| Dimension | Version 1.0.0 | Version 2.0.0 |
|---|---|---|
| Resume usage | Collected but ignored | Actively read; every question references it |
| Score calculation | Undefined / inconsistent | Weighted formula, sums to exactly 100 |
| Interview opening | Abrupt, no intro | Natural opener with persona + warm-up question |
| Progress visibility | None | Every question labelled with round and position |
| Push-back | Mentioned but undefined | Script defined, one follow-up limit |
| Study plan | Vague sentence | Structured table with topic, resource, timeframe |
| Seniority impact | Collected, ignored | Full calibration per level (Junior → Lead) |
| Company type impact | 3 narrow examples | 7 types with distinct interviewer priorities |
| Behavioural scoring | "Score using STAR" | Full rubric with strong/weak per component |
| Output format | Inconsistent | Standardised templates for questions + report |
| Session control | None | stop / skip / restart / redo |
| Regional styles | None | US / UK / India / Australia |
| Time framing | "30-minute interview" (false) | Removed; replaced with question count |
| Skill triggering | Passive description | Catches natural everyday language |
| Tags | 5 | 10 |
| Category | business-sales (wrong) | career (correct) |
| Version | 1.0.0 | 2.0.0 |
