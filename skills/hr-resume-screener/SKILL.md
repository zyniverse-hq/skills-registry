---
name: hr-resume-screener
description: For recruiters and HR. Screen a candidate resume against a Job Description and return a FIT / PARTIAL FIT / NOT A FIT verdict (displayed with emoji indicators) with requirement match, strengths, gaps, salary check, and an Excel-ready summary row. Use when you have both a job description and a candidate resume to evaluate. Trigger on phrases like "screen this resume against the JD," "is this candidate a fit for this role," or "compare this profile to the job requirements."
metadata:
  version: 1.1.1
  author: Deepak Padmanabha
  email: deepak@zysk.tech
  category: hr-recruiting
  tags:
    - hr
    - resume
    - screening
    - jd-matching
    - recruitment
  product: zysk
  sprint: 1
  tested_with: claude-sonnet-4-6
---

# HR Resume Screener

> Screen a resume against a JD and instantly determine FIT, PARTIAL FIT, or NOT A FIT — with a structured breakdown ready to paste into Excel.

## When to use

- Activate when: the user uploads or shares both a Job Description and a candidate resume together.
- Activate when: the user asks "is this candidate fit for this role?", "check this resume against the JD", "screen this profile", or any variation of matching one resume to one job description.
- Do NOT activate when: only a resume or only a JD is provided — ask for the missing document first before proceeding.
- Do NOT activate when: the user is improving their own resume, or no JD is involved — use resume-recruiter instead.

## Prerequisites

- [ ] Job Description (JD) — PDF, Word file, or pasted text
- [ ] Candidate Resume / CV — PDF, Word file, or pasted text

## Steps

### Step 0: Collect Both Inputs

You need exactly two things before proceeding: the Job Description and the candidate's resume. Both can be provided as a file upload (PDF or Word .docx) or text pasted directly in chat.

If the JD is missing, ask:
> "Please share the Job Description — you can upload the file (PDF or Word) or paste the text."

If the resume is missing, ask:
> "Please share the candidate's resume — you can upload the file or paste the text."

If a file cannot be read (corrupted, unsupported format, or unreadable), inform the user immediately and ask them to provide the document as pasted text or in a supported format.

If both are present and readable, proceed immediately. Do not ask any further questions.

### Step 1: Extract from the JD

Read the JD and identify:

```
Role Title:
Department / Team:
Experience Required: (years and level)
Must-Have Requirements: (list every hard requirement explicitly stated)
Good-to-Have Requirements: (preferred but optional)
Key Responsibilities: (top 3–5 in your own words)
Industry / Domain: (if specified)
Location / Work Mode: (city, on-site / hybrid / remote)
Budget / CTC Band: (if mentioned)
```

### Step 2: Extract from the Resume

Read the resume and identify:

```
Candidate Name:
Current Role / Title:
Total Experience: (years)
Current Location:
Notice Period / Availability:
Education:
Core Skills:
Industry Background:
Key Achievements: (top 2–3 if quantified)
Current CTC: (if mentioned)
Expected CTC: (if mentioned)
```

### Step 3: Match Every Must-Have Requirement

For each Must-Have requirement from the JD, mark:

- ✅ **MET** — clearly evidenced in the resume
- ⚠️ **PARTIAL** — some evidence but incomplete or not current
- ❌ **NOT MET** — no evidence in the resume

**Verdict Logic:**

| Situation | Verdict |
|---|---|
| At least 80% of Must-Haves are ✅ (e.g., 4 out of 5, or 8 out of 10) | **FIT** |
| Most Must-Haves ✅ but 1–2 are ⚠️ (60-79% are ✅) | **PARTIAL FIT** |
| 2 or more Must-Haves are ❌ (less than 60% are ✅) | **NOT A FIT** |
| Any single critical Must-Have is ❌ (e.g. mandatory cert, minimum years) | **NOT A FIT** regardless of other scores |

### Step 4: Salary Band Check

| Situation | Salary Fit Label |
|---|---|
| Expected CTC within JD budget | 💰 FIT |
| Expected CTC up to 15% above the JD budget amount | ⚠️ STRETCH |
| Expected CTC 15–30% above the JD budget amount | ⚠️ BUDGET RISK |
| Expected CTC 30%+ above the JD budget amount | ❌ MISMATCH |
| CTC not mentioned in either | UNKNOWN — verify in screening call |

### Step 5: Produce the Structured Report

Use this exact structure. Keep it verdict-first and readable in under 90 seconds.

---

## 📋 Resume Screening Report

**Candidate:** [Name]  
**Role Applied:** [Role from JD]  
**Screened by:** Zysk HR Screening Assistant  
**Date:** [today's date]

---

### [🟢 FIT / 🟡 PARTIAL FIT / 🔴 NOT A FIT]

> *[One sentence explaining the verdict — e.g. "Candidate meets all core requirements and has directly relevant industry experience." or "Strong on skills but does not meet the minimum experience requirement."]*

---

### 📊 Profile Snapshot

| Field | Details |
|---|---|
| Current Role | |
| Total Experience | |
| Education | |
| Location / Notice | |
| Current CTC | |
| Expected CTC | |
| Salary Fit | |

---

### ✅ JD Requirements Match

| Requirement (from JD) | Status | Evidence from Resume |
|---|---|---|
| [Requirement 1] | ✅ MET | [What the resume shows] |
| [Requirement 2] | ⚠️ PARTIAL | [What is there vs. what is missing] |
| [Requirement 3] | ❌ NOT MET | [Completely absent or below bar] |

*(Extract 4–6 key requirements from the JD using these criteria: prioritize requirements that are explicitly marked as required or "must have," include any with specific experience thresholds (e.g., "5+ years"), mention mandatory certifications or qualifications, and reference specific tools/technologies essential to the role. Include all Must-Have requirements up to 6, starting with those containing year counts or critical qualifications.)*

---

### 💪 Strengths

- [Strength 1]
- [Strength 2]
- [Strength 3]

### 🚩 Gaps

- [Gap 1 — specific, not vague]
- [Gap 2]

*(Write "None identified" if there are no gaps)*

---

### 📞 Recommendation

> [One clear sentence — exactly what HR should do next. E.g. "Schedule technical round immediately." or "Arrange a 15-minute screening call to clarify the S/4HANA experience before advancing." or "Reject — does not meet minimum experience and module requirements."]*

---

### 📤 Excel Row Summary *(copy-paste ready)*

| Candidate | Role | Experience | Verdict | Score | Salary Fit | Strengths | Gaps | Next Step |
|---|---|---|---|---|---|---|---|---|
| [Name] | [Role] | [X yrs] | [FIT/PARTIAL/NOT A FIT] | [0-100] | [FIT/STRETCH/MISMATCH/UNKNOWN] | [top strength] | [top gap] | [action] |

## Output

- **Format:** structured report in chat, delivered after both inputs are collected
- **Location:** the conversation
- **Example:** verdict header (🟢 FIT), profile snapshot table, JD requirements match table with ✅/⚠️/❌ statuses, strengths and gaps bullets, one-line recommendation, and a copy-paste Excel row

## Decision Framework & Edge Cases

- Works for any role — tech, non-tech, ERP, sales, operations, finance, HR, and more
- **Verdict first** — HR sees the decision before anything else
- **Never invent** — if something is not in the resume, mark it NOT MET, do not infer
- **Be direct** — "Does not meet the 5-year requirement" not "may have slightly less experience"
- **Only judge against the JD** — don't penalise for skills the JD never asked for

**Edge cases:**

| Situation | How to Handle |
|---|---|
| JD is vague / missing some details | Extract what you can; note which requirements are inferred |
| Resume is very thin | Flag: "Sparse profile — low match confidence. Recommend a brief call to verify basics." |
| Candidate appears overqualified | Flag: "Candidate may be overqualified — verify role scope and salary expectations." |
| No salary in JD or resume | Label salary fit as UNKNOWN; recommend verifying in first call |
| Resume is not in English | Translate key fields, note the original language, proceed with the match |
