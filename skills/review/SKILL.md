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
7. **sales-strategist** *(conditional)* — B2B sales lens: selling solutions vs. features (only when a CompanyProfile exists in `knowledge/companies/` for the target company)

## Process

### Step 1 — Prepare Context
Read resume.yaml (and optionally a JD for targeted feedback).

If a JD is provided, extract the company name and check `knowledge/companies/` for an existing CompanyProfile. If found, load it — this enables the sales-strategist persona and enriches other personas with buyer context.

### Step 2 — Load and Invoke Personas

For each persona, read its agent definition file to load the full evaluation criteria,
then adopt that persona and evaluate the resume.

Agent definitions (relative to this plugin's root):

1. **ats-bot**: Read `agents/ats-bot.agent.md`
2. **recruiter**: Read `agents/recruiter.agent.md`
3. **hiring-manager**: Read `agents/hiring-manager.agent.md`
4. **hr-screener**: Read `agents/hr-screener.agent.md`
5. **technical-reviewer**: Read `agents/technical-reviewer.agent.md`
6. **engineer-peer**: Read `agents/engineer-peer.agent.md`
7. **sales-strategist** *(conditional)*: Read `agents/sales-strategist.agent.md` — only invoke when a CompanyProfile exists for the target company. Pass the CompanyProfile as context.

For each persona, produce:
- **Strengths** (1-3 specific items with evidence)
- **Weaknesses** (1-3 specific items with evidence)
- **Score** (1-10)
- **Action Items** (1-3 concrete, specific recommendations)
- Any persona-specific extras defined in the agent file

If a specific persona is requested via `--persona <name>`, load only that agent file.

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
| Sales Strategist | X/10 | ... | ... |

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

### Step 4 — Log Session
Save to `knowledge/sessions/review_{date}_{company-slug}_{role}.yaml` (use `general` for company/role if no JD provided):
```yaml
date: YYYY-MM-DD
type: review
company: Company Name | general
slug: company-slug | general
role: Role Title | general
resume_source: resume.yaml | tailored_resume.yaml
personas_invoked: [ats-bot, recruiter, hiring-manager, hr-screener, technical-reviewer, engineer-peer, sales-strategist]
scores:
  ats_bot: X
  recruiter: X
  hiring_manager: X
  hr_screener: X
  technical_reviewer: X
  engineer_peer: X
  sales_strategist: X  # or null if not invoked
consensus_strengths:
  - "..."
consensus_weaknesses:
  - "..."
action_items:
  - "..."
  - "..."
  - "..."
```

## Options
- Review all personas: `/review`
- Specific persona: `/review --persona engineer-peer`
- With JD context: `/review --jd path/to/jd.txt`
