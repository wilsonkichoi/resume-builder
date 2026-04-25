---
name: qualify
description: "Assess how much a company needs you — flip the match lens. Use when: 'qualify opportunity', 'should I apply', 'is this worth my time', 'how much do they need me', 'qualify this company'."
argument-hint: "[company name or path to job description]"
---

# /qualify — Strategic Opportunity Qualification

## Purpose
Flip the `/match` lens. Instead of "do I meet their bar?", assess "how much do they need me?" Score the opportunity across 6 strategic dimensions to help decide where to invest your time and how to position yourself.

This is the "Sell me this pen" approach — uncover the buyer's needs before pitching.

## Anti-Fabrication Rules (MANDATORY)
1. Scores are assessments, not claims — they represent judgment, not fact
2. Every score MUST cite what evidence drove it
3. Missing evidence = lower confidence, NOT a lower score — distinguish "I don't know" from "it's bad"
4. NEVER inflate scores to encourage applying — honesty serves the user
5. Cultural fit is inherently subjective — label it as such
6. If CompanyProfile data is thin, say so explicitly and recommend running `/research` with more sources

## Process

### Step 1 — Gather Inputs
- Check `knowledge/companies/` for an existing CompanyProfile. If none exists, tell the user: "No company profile found. Run `/research {company}` first for a sharper qualification, or I can do a lightweight assessment from the JD alone."
- Read `resume.yaml` from the project root.
- Accept JD as file path or pasted text (optional but recommended).
- If a CompanyProfile exists, check its `researched_at` date. If older than 30 days, warn: "This profile was researched on {date}. Company data may be outdated. Consider re-running `/research`."

### Step 2 — Run /match if Needed
If a JD is provided and no existing `/match` session exists for this company/role, run `/match` analysis. This provides the baseline skills-based fit data. `/qualify` layers the strategic assessment on top — they are complementary, not redundant.

### Step 3 — Dimensional Scoring
Score each dimension 1-10. For each score, cite the specific evidence from CompanyProfile and resume.yaml that drove it. If evidence is insufficient, note it as "insufficient data" with a confidence qualifier.

#### 1. Pain-Solution Match (weight: 25%)
Map CompanyProfile pain points against resume.yaml experience bullets.
- 1-3: Your experience doesn't address their core problems
- 4-6: Some overlap, but you'd be learning on the job
- 7-8: Direct experience with 1-2 of their key pain points
- 9-10: You've solved exactly this problem before, with metrics to prove it

**Evidence format**: "{pain point} ← {your bullet/experience that addresses it}"

#### 2. Value Density (weight: 20%)
Of their total needs (from JD + pain points), what percentage can you uniquely address vs. any qualified candidate?
- 1-3: You meet minimum requirements, same as dozens of other candidates
- 4-6: You cover their needs plus have 1-2 differentiators
- 7-8: Your specific combination of skills is uncommon and highly relevant
- 9-10: You are one of very few people who can address their full problem space

**Evidence format**: "{unique combination} — rare because {reason}"

#### 3. Growth Alignment (weight: 15%)
Compare CompanyProfile growth signals and tech stack trajectory against your recent experience trajectory.
- 1-3: They're heading in a direction you're moving away from
- 4-6: Neutral — no strong alignment or misalignment
- 7-8: Your growth trajectory matches their investment direction
- 9-10: You're already ahead of where they're trying to go

**Evidence format**: "They're investing in {X}, you've been deepening in {Y}"

#### 4. Culture Fit (weight: 15%)
Compare CompanyProfile culture signals against what you want. This is bidirectional — do THEY fit YOU?
- 1-3: Clear misalignment on work style, values, or environment
- 4-6: No strong signals either way
- 7-8: Positive alignment on most dimensions
- 9-10: Strong match on the things that matter most to you

**Evidence format**: "Signal: {culture signal} — Alignment: {your preference}"

Note: If the user hasn't stated preferences, ask before scoring. Don't assume.

#### 5. Leverage Position (weight: 15%)
Assess supply/demand dynamics. Are you entering from a position of strength or weakness?
- 1-3: They have many qualified candidates; you need them more than they need you
- 4-6: Balanced — standard competitive position
- 7-8: Your skill combination is in high demand at this company
- 9-10: They are urgently hiring for exactly your profile and the talent pool is thin

**Evidence format**: "Demand signal: {evidence}. Supply signal: {evidence}."

#### 6. ROI Potential (weight: 10%)
Can you articulate specific, quantifiable value you'd deliver? Map your proven metrics to their pain points.
- 1-3: No direct mapping between your past metrics and their needs
- 4-6: Some transferable metrics, but context is different
- 7-8: Clear metric-to-pain-point mapping for 1-2 areas
- 9-10: You can say "I did exactly this at Company X, here are the numbers"

**Evidence format**: "Your metric: {metric} → Their pain: {pain point}"

### Step 4 — Strategic Brief
Calculate weighted average. Then produce a strategic brief:

**Strong Pursue (weighted avg >= 7.0)**:
- Positioning angle: what story to tell, leading with their pain
- Unique leverage points: what only you can offer
- Cover letter hook suggestion: which hook type and specific angle
- Interview talking points: discovery questions to ask them

**Pursue with Caution (weighted avg 5.0-6.9)**:
- Worth applying, but here's what to watch for
- Where you're strong vs. where you'll need to compensate
- Questions to ask in the interview to validate fit
- What would need to be true for this to be a great role

**Consider Passing (weighted avg < 5.0)**:
- Why this may not be worth your time
- What would need to change to make it viable
- Alternative: is there a different role at this company that fits better?

### Step 5 — Log Session
Save to `knowledge/sessions/qualify_{date}_{company-slug}_{role}.yaml`:
```yaml
date: YYYY-MM-DD
type: qualify
company: Company Name
slug: company-slug
role: Role Title
company_profile_used: true/false
match_session_used: session-id or null
scores:
  pain_solution_match: { score: X, confidence: high/medium/low }
  value_density: { score: X, confidence: high/medium/low }
  growth_alignment: { score: X, confidence: high/medium/low }
  culture_fit: { score: X, confidence: high/medium/low }
  leverage_position: { score: X, confidence: high/medium/low }
  roi_potential: { score: X, confidence: high/medium/low }
  weighted_average: X.X
recommendation: strong-pursue | pursue-with-caution | consider-passing
```

## Output
Present the dimensional scores as a table, followed by the strategic brief. Format:

```
## Qualification: {Company} — {Role}

| Dimension | Score | Confidence | Key Evidence |
|-----------|-------|------------|-------------|
| Pain-Solution Match (25%) | X/10 | high/med/low | one-liner |
| Value Density (20%) | X/10 | high/med/low | one-liner |
| Growth Alignment (15%) | X/10 | high/med/low | one-liner |
| Culture Fit (15%) | X/10 | high/med/low | one-liner |
| Leverage Position (15%) | X/10 | high/med/low | one-liner |
| ROI Potential (10%) | X/10 | high/med/low | one-liner |
| **Weighted Average** | **X.X/10** | | |

## Strategic Brief
{positioning angle, leverage points, or reasons to pass}
```

## Options
- With company name: `/qualify Acme Corp`
- With JD: `/qualify path/to/jd.txt`
- Both: `/qualify Acme Corp path/to/jd.txt`
