# Zyniverse Skills Registry

> Production-grade Claude skills built by the Zysk & Zyni teams.

## Structure

```
skills-registry/
├── index.json          # Machine-readable skill manifest
├── skills/             # One folder per skill
│   └── skill-name/
│       └── SKILL.md
└── website/            # Registry UI
    └── index.html
```

## Usage

Reference any skill in your `CLAUDE.md`:

```yaml
- name: deployshield
  source: github:zyniverse-hq/skills-registry/skills/deployshield
```

## Sprint 1 — 22 Skills

| # | Skill | Author | Group | Category |
|---|-------|--------|-------|----------|
| 1 | The Skill That Ships (10-min Blog Machine) | Suman Pai | Opus | Business & Sales Automation |
| 2 | Safe Push Workflow | Ananth Raj L | Haiku | Pre-Deployment & Release Safety |
| 3 | Playwright Test Generation & Scenario Planning | Deepikaa Naganathan | Haiku | QA & Testing Automation |
| 4 | Automated QA Test Plans from Merged PRs | Rajashekhar V | Haiku | QA & Testing Automation |
| 5 | EDD — Evaluation Driven Development | Sharath S Rao | Sonnet | Engineering Practice & Decision Support |
| 6 | Debug Debrief — Bug Fixes into Engineering Learning | Ruthvika B | Opus | Engineering Practice & Decision Support |
| 7 | Tech Mentor — AI Research for Architecture Decisions | Vishnu B V | Opus | Engineering Practice & Decision Support |
| 8 | DeployShield — Pre-Deployment Risk Auditor | Akash R | Sonnet | Pre-Deployment & Release Safety |
| 9 | Expo Build & SDK Upgrade Checker | OM Chavan | Haiku | Pre-Deployment & Release Safety |
| 10 | PRD to QA Test Suite & GitHub Bug Raiser | Preethika Kulal | Haiku | QA & Testing Automation |
| 11 | Enterprise QA Test Case Generator | Ajay Kumar R | Sonnet | QA & Testing Automation |
| 12 | Razorpay Payment Gateway Integration | Tazeen Soudagar | Sonnet | Frontend & Backend Integration |
| 13 | Cloud Infra Planner to Ready-to-Apply | Nagendra K V | Opus | Infrastructure, Ops & Security |
| 14 | Test Case Review Skill | Rachayya | Sonnet | QA & Testing Automation |
| 15 | Automated Security Audit — Full-Stack Vulnerability Assessment | Jagadish Nayak | Haiku | Infrastructure, Ops & Security |
| 16 | Upwork Proposal Automation | Kruthi M N | Opus | Business & Sales Automation |
| 17 | Investor/Accelerator Form Filler + Pitch Deck Creator | T S Sarang | Opus | Business & Sales Automation |
| 18 | UI Consistency Guard | Ruthu Bahubali Jain | Opus | Frontend & Backend Integration |
| 19 | IntegrateKit — Frontend to Backend Wiring | Vishak Gowda | Sonnet | Frontend & Backend Integration |
| 20 | Daily Status Report Generator | Shilpa V P | Haiku | Business & Sales Automation |
| 21 | WordPress Maintenance Conductor | Stalin Marbhenn S | Sonnet | Pre-Deployment & Release Safety |
| 22 | Edge Case Discovery | Shreyas Bilugali | Haiku | QA & Testing Automation |

### Breakdown by category

| Category | Skills |
|----------|--------|
| QA & Testing Automation | 6 |
| Pre-Deployment & Release Safety | 4 |
| Business & Sales Automation | 4 |
| Engineering Practice & Decision Support | 3 |
| Frontend & Backend Integration | 3 |
| Infrastructure, Ops & Security | 2 |

### Breakdown by group

| Group | Skills |
|-------|--------|
| Haiku | 8 |
| Opus | 7 |
| Sonnet | 7 |

---

Built by [Zyni Innovations Pvt. Ltd.](https://zyniverse.ai) · Bengaluru
