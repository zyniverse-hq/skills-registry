# Plan: Including skill-reviewer and skill-fixer in Zyniverse Skills Registry

## 📋 Executive Summary

We need to include two complex skills (`skill-reviewer` and `skill-fixer`) from personal skills directory to the Zyniverse skills registry. Both skills have multi-file structures (scripts/, references/) that differ from the registry's simple template.

## 🎯 Key Challenges & Solutions

### Challenge 1: Complex Directory Structure
**Current State:**
- `skill-reviewer/`: SKILL.md + scripts/ + references/ 
- `skill-fixer/`: SKILL.md + scripts/ + references/

**Registry Template:**
- `your-skill/`: SKILL.md only

**Solution:** The registry can accommodate multi-file skills. We'll preserve the complete structure as both skills need their scripts and references to function properly.

### Challenge 2: Frontmatter Requirements
**Current Frontmatter (skill-reviewer):**
```yaml
---
name: skill-reviewer
compatibility: "Python 3.8+..."
description: "..."
---
```

**Registry Requirements:**
- Required: `name`, `description`
- Extended Zyniverse fields: `version`, `author`, `email`, `category`, `tags`, `product`, `sprint`, `tested_with`

**Solution:** Add Zyniverse extended fields while preserving existing `compatibility` field.

### Challenge 3: One Skill Per PR Rule
**Problem:** Contribution guide states "One skill per PR" but we need to include TWO skills.

**Options:**
1. **Option A (Recommended):** Two separate PRs
   - PR #1: skill-reviewer 
   - PR #2: skill-fixer
   - ✅ Follows contribution rules exactly
   - ✅ Easier to review and validate
   - ❌ Takes more time

2. **Option B:** Single PR with both skills
   - One PR for both skills
   - ✅ Faster
   - ❌ Violates contribution rules
   - ❌ Harder to review
   - ❌ CI might reject

**Recommendation:** Use Option A (two separate PRs) to follow contribution guidelines.

## 📅 Implementation Plan

### Phase 1: Frontmatter Adaptation

#### skill-reviewer Frontmatter Update:
```yaml
---
name: skill-reviewer
description: Review, audit, or quality-check an Anthropic Agent Skill (a SKILL.md folder) and produce a detailed review report. Use this whenever someone asks to review, audit, evaluate, vet, grade, or QA a skill, check whether a SKILL.md is well-formed or upload-ready, assess a skill's triggering, description, or instruction quality, or security-review a skill before sharing or installing it.
version: 1.1.0
author: Deepak Padmanabha
email: deepak@zysk.tech
category: engineering-practice
tags:
  - review
  - quality-assurance
  - skill-audit
  - linting
  - validation
product: zysk
sprint: 1
tested_with: claude-sonnet-4-6
compatibility: "Python 3.8+. No required third-party packages. PyYAML is used for exact frontmatter parsing only if it is already installed; otherwise a built-in parser is used."
---
```

#### skill-fixer Frontmatter Update:
```yaml
---
name: skill-fixer
description: Fix the findings in a skill-reviewer report by editing the reviewed skill on a new git branch. Use this whenever someone wants to remediate, fix, address, or resolve the issues a skill review surfaced, or asks to "apply the fixes from the report" or "clean up this skill based on the review".
version: 1.1.0
author: Deepak Padmanabha
email: deepak@zysk.tech
category: engineering-practice
tags:
  - fix
  - remediation
  - skill-improvement
  - refactoring
  - automation
product: zysk
sprint: 1
tested_with: claude-sonnet-4-6
compatibility: "Python 3.8+ and git. No required third-party packages; PyYAML is used only if already installed. Operates on a git repository and creates a new branch."
---
```

### Phase 2: Branch Strategy

#### Branch 1: skill/skill-reviewer
```bash
# Sync first
git fetch upstream
git checkout main
git merge upstream/main

# Create branch
git checkout -b skill/skill-reviewer

# Copy skill
cp -r C:/Users/VikasM/.claude/skills/skill-reviewer skills/skill-reviewer

# Validate
python3 scripts/validate_skill.py skills/skill-reviewer/SKILL.md

# Commit and push
git add skills/skill-reviewer/
git commit -m "feat(skill): add skill-reviewer"
git push origin skill/skill-reviewer
```

#### Branch 2: skill/skill-fixer
```bash
# Start from main again
git checkout main
git pull

# Create branch
git checkout -b skill/skill-fixer

# Copy skill  
cp -r C:/Users/VikasM/.claude/skills/skill-fixer skills/skill-fixer

# Validate
python3 scripts/validate_skill.py skills/skill-fixer/SKILL.md

# Commit and push
git add skills/skill-fixer/
git commit -m "feat(skill): add skill-fixer"
git push origin skill/skill-fixer
```

### Phase 3: File Structure Preservation

Both skills will maintain their complete directory structure:

```
skills/
├── skill-reviewer/
│   ├── SKILL.md
│   ├── scripts/
│   │   ├── review_skill.py
│   │   ├── find_skill_creator.py
│   │   └── validate_eval_set.py
│   └── references/
│       ├── checklist.md
│       ├── functional-testing.md
│       ├── instruction-review.md
│       └── report-template.md
│
└── skill-fixer/
    ├── SKILL.md
    ├── scripts/
    │   ├── prepare_fixes.py
    │   └── verify_fixes.py
    └── references/
        └── fix-strategies.md
```

### Phase 4: Validation Strategy

#### Pre-Push Validation:
```bash
# For each skill
python3 scripts/validate_skill.py skills/skill-reviewer/SKILL.md
python3 scripts/validate_skill.py skills/skill-fixer/SKILL.md
```

#### Expected Validation Checks:
- ✅ Folder name matches `name` frontmatter
- ✅ Required fields present (name, description)
- ✅ Frontmatter is valid YAML
- ✅ Name is kebab-case
- ✅ Description is verb-first
- ✅ Category is valid

### Phase 5: PR Creation

#### PR #1: skill-reviewer
- **Title:** `feat(skill): add skill-reviewer`
- **Base:** `zyniverse-hq/skills-registry/main`
- **Head:** `vikas-m-zy/skills-registry/skill/skill-reviewer`
- **Description:** Use PR template with skill details

#### PR #2: skill-fixer  
- **Title:** `feat(skill): add skill-fixer`
- **Base:** `zyniverse-hq/skills-registry/main`
- **Head:** `vikas-m-zy/skills-registry/skill/skill-fixer`
- **Description:** Use PR template with skill details

## 🔧 Technical Considerations

### 1. Dependency Management
Both skills use Python scripts. Ensure:
- Scripts are executable (`chmod +x`)
- No absolute paths in scripts
- Cross-platform compatibility (Windows/Linux)

### 2. __pycache__ Files
- **Action:** Exclude `__pycache__/` directories from commit
- **Reason:** These are build artifacts, not source code
- **Implementation:** Add to `.gitignore` if not present

### 3. Line Endings
- **Issue:** Windows (CRLF) vs Linux (LF)
- **Solution:** Ensure scripts use LF line endings for cross-platform compatibility

### 4. Script Permissions
- **Issue:** Scripts may not be executable on Linux/Mac
- **Solution:** Add git permissions configuration if needed

## 📋 Pre-Flight Checklist

Before creating PRs, verify:

- [ ] Both skills copied to `skills/` directory
- [ ] Folder names match frontmatter `name` fields
- [ ] Frontmatter updated with Zyniverse fields
- [ ] All required fields present (name, description)
- [ ] Category is valid (`engineering-practice`)
- [ ] Tags are lowercase kebab-case
- [ ] Version set to `1.1.0`
- [ ] Author and email populated correctly
- [ ] `product` set to `zysk`
- [ ] `tested_with` specified
- [ ] `compatibility` field preserved
- [ ] No `__pycache__/` directories included
- [ ] Scripts use LF line endings
- [ ] Local validation passes for both skills
- [ ] Branch names follow `skill/<skill-name>` pattern
- [ ] Commits follow `feat(skill): add <skill-name>` pattern

## 🎯 Success Criteria

- ✅ Both PRs pass CI validation
- ✅ No merge conflicts
- ✅ Skills function correctly when installed
- ✅ Reviewers can understand skill purpose from description
- ✅ Skills integrate properly with registry tooling

## 📞 Next Steps

1. **Execute Phase 1:** Update frontmatter for both skills
2. **Execute Phase 2:** Create branches following the strategy
3. **Execute Phase 3:** Copy skills preserving directory structure
4. **Execute Phase 4:** Validate both skills locally
5. **Execute Phase 5:** Create both PRs following contribution guidelines

## ⚠️ Risk Mitigation

### Risk 1: CI Validation Failure
- **Mitigation:** Run local validation before pushing
- **Fallback:** Fix validation issues before PR creation

### Risk 2: Merge Conflicts
- **Mitigation:** Keep branches separate and sync with upstream
- **Fallback:** Resolve conflicts manually before PR

### Risk 3: Script Compatibility
- **Mitigation:** Test scripts on both Windows and Linux if possible
- **Fallback:** Add platform-specific handling if needed

---

**Plan Status:** Ready for execution
**Estimated Time:** 2-3 hours for both skills
**Priority:** High (part of skills registry enhancement)
