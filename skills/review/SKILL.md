---
name: review
description: "Run multi-persona review of resume. Use when: 'review resume', 'get feedback', 'critique resume', 'evaluate resume'."
argument-hint: "[optional: path to JD for context]"
---

# /review — Multi-Persona Resume Review

## Purpose
Invoke up to 7 independent review personas, each evaluating the resume from their professional perspective. Enrich every persona with all available prior context (company research, match analysis, qualification, tailoring decisions, scores) so reviews are informed rather than cold reads. Consolidate into prioritized action items.

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

If a JD is provided, extract the company name/slug and role, then discover all available prior context:

1. **CompanyProfile**: Check `knowledge/companies/{slug}.yaml`. If found, load it — this enables the sales-strategist persona and enriches all personas with buyer context (pain points, tech stack, culture, key people).

2. **Session artifacts**: Check `knowledge/sessions/` for any matching sessions for this company/role. Load all that exist:
   - `match_{date}_{slug}_{role}.yaml` — gap analysis, skill coverage percentages, missing skills. Tells personas what the resume is strong/weak on relative to this JD.
   - `qualify_{date}_{slug}_{role}.yaml` — weighted qualification score, dimension breakdown, pursuit recommendation. Gives personas strategic context on overall fit.
   - `tailor_{date}_{slug}_{role}.yaml` — tailoring decisions made (emphasized, trimmed, rephrased), before/after scores. Critical for technical-reviewer: distinguishes intentional reframing from accidental fabrication.
   - `score_{date}_{slug}_{role}.yaml` — ATS/HR score breakdown. Gives personas quantitative baseline to reference.
   - `research_{date}_{slug}.yaml` — research session metadata (redundant if CompanyProfile exists, but load if CompanyProfile is missing).

   Use glob matching (e.g., `*_{slug}_{role}.yaml`) since dates vary. If multiple sessions exist for the same type, use the most recent.

3. **Resume source**: If a tailor session exists, check whether a tailored resume exists at the path in `tailor.output_dir`. If so, review the **tailored** resume (not the base resume.yaml) unless the user explicitly requests otherwise. Note which resume is being reviewed in the output.

Assemble all discovered context into a **context bundle** that will be passed to every persona in Step 2.

### Step 2 — Load and Invoke Personas

For each persona, read its agent definition file to load the full evaluation criteria,
then adopt that persona and evaluate the resume. **Pass the full context bundle from Step 1 to every persona** — each persona uses what's relevant to its lens:

| Persona | Key context consumed |
|---------|---------------------|
| ats-bot | score session (keyword breakdown), match session (gap list) |
| recruiter | qualify session (pursuit recommendation), score session (HR score) |
| hiring-manager | match session (skill coverage), qualify session (dimension scores), score session (ATS+HR) |
| hr-screener | CompanyProfile (culture), qualify session (red flags) |
| technical-reviewer | tailor session (tailoring decisions — use to distinguish intentional reframing from fabrication), match session (technical gaps) |
| engineer-peer | match session (technical depth gaps), tailor session (what was rephrased) |
| sales-strategist | CompanyProfile (pain points), qualify session (strategic fit, pursuit recommendation), match session (alignment %) |

Agent definitions (relative to this plugin's root):

1. **ats-bot**: Read `agents/ats-bot.agent.md`
2. **recruiter**: Read `agents/recruiter.agent.md`
3. **hiring-manager**: Read `agents/hiring-manager.agent.md`
4. **hr-screener**: Read `agents/hr-screener.agent.md`
5. **technical-reviewer**: Read `agents/technical-reviewer.agent.md`
6. **engineer-peer**: Read `agents/engineer-peer.agent.md`
7. **sales-strategist** *(conditional)*: Read `agents/sales-strategist.agent.md` — only invoke when a CompanyProfile exists for the target company.

For each persona, produce:
- **Strengths** (1-3 specific items with evidence)
- **Weaknesses** (1-3 specific items with evidence)
- **Score** (1-10)
- **Action Items** (1-3 concrete, specific recommendations)
- Any persona-specific extras defined in the agent file

When a persona references data from a prior session, it MUST cite the source (e.g., "per match session: 72% overall alignment" or "tailor session shows this was an intentional reframe, not fabrication").

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

### Step 4 — Log Session (MANDATORY — do not present results until this step is complete)
Save to `knowledge/sessions/review_{date}_{company-slug}_{role}.yaml` (use `general` for company/role if no JD provided):
```yaml
date: YYYY-MM-DD
type: review
company: Company Name | general
slug: company-slug | general
role: Role Title | general
resume_source: resume.yaml | tailored/{date}_{company-slug}_{role}/resume.yaml
context_loaded:
  company_profile: knowledge/companies/{slug}.yaml | null
  match_session: knowledge/sessions/match_{date}_{slug}_{role}.yaml | null
  qualify_session: knowledge/sessions/qualify_{date}_{slug}_{role}.yaml | null
  tailor_session: knowledge/sessions/tailor_{date}_{slug}_{role}.yaml | null
  score_session: knowledge/sessions/score_{date}_{slug}_{role}.yaml | null
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

When running multiple reviews in sequence, log EACH run individually as you complete it. Do not batch logging or defer it until after presentation.

Present the consolidated review (Step 3 output) to the user only after this step is complete.

## Options
- Review all personas: `/review`
- Specific persona: `/review --persona engineer-peer`
- With JD context: `/review --jd path/to/jd.txt`
