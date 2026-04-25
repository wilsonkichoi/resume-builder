---
name: review
description: "Run multi-persona review of resume. Use when: 'review resume', 'get feedback', 'critique resume', 'evaluate resume'."
argument-hint: "[optional: path to JD for context]"
---

# /review — Multi-Persona Resume Review

## Purpose
Invoke 6 independent review personas, each evaluating the resume from their professional perspective. Consolidate into prioritized action items.

## Personas
1. **ats-bot** — ATS parser simulation (keyword parsing, format compliance)
2. **recruiter** — 6-second scan (first impression, standout bullets)
3. **hiring-manager** — Technical depth (domain expertise, impact, "would I interview?")
4. **hr-screener** — Compliance (gaps, red flags, culture fit)
5. **technical-reviewer** — Peer review (technical accuracy, overstatement)
6. **engineer-peer** — Staff/principal engineer (architecture depth, hands-on signal, overclaim detection)

## Process

### Step 1 — Prepare Context
Read resume.yaml (and optionally a JD for targeted feedback).

### Step 2 — Invoke Personas
For each persona, evaluate the resume and produce:
- **Strengths** (1-3 specific items with evidence)
- **Weaknesses** (1-3 specific items with evidence)
- **Score** (1-10)
- **Action Items** (1-3 concrete, specific recommendations)

### Step 3 — Consolidate
Merge all persona feedback into:
```
## Review Summary

| Persona | Score | Top Strength | Top Weakness |
|---------|-------|-------------|-------------|
| ATS Bot | X/10 | ... | ... |
| Recruiter | X/10 | ... | ... |
| Hiring Manager | X/10 | ... | ... |
| HR Screener | X/10 | ... | ... |
| Technical Reviewer | X/10 | ... | ... |
| Engineer Peer | X/10 | ... | ... |

## Prioritized Action Items (by impact)
1. ...
2. ...
3. ...
4. ...
5. ...

## Consensus Strengths
- ...

## Consensus Weaknesses
- ...
```

## Options
- Review all personas: `/review`
- Specific persona: `/review --persona engineer-peer`
- With JD context: `/review --jd path/to/jd.txt`
