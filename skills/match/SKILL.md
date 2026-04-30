---
name: match
description: "Match resume against a job description, analyze gaps, and report fit. Use when: 'match resume', 'how do I match', 'gap analysis', 'am I qualified', 'job fit'."
argument-hint: "[path to job description or paste JD text]"
---

# /match — JD Matching + Gap Analysis

## Purpose
Analyze how well resume.yaml matches a specific job description. Identify gaps, strengths, and strategic fit.

## Process

### Step 1 — Parse the Job Description
Parse the JD to extract requirements, preferences, experience level, domain terminology, and red flags.

### Step 2 — Match Against Resume
Read resume.yaml and skills.yaml, then score:
- **Required skills match**: weight 70% — how many required skills are demonstrated?
- **Preferred skills match**: weight 30% — how many preferred skills are present?
- For each skill: check both the Skills section AND Experience bullets for evidence

### Step 3 — Gap Analysis
Identify:
- **Missing required skills** — skills the JD requires that are not in resume.yaml
- **Weak areas** — skills mentioned but not demonstrated in experience bullets
- **Transferable skills** — things you have that map to requirements differently named
- **Overcovered areas** — sections with heavy emphasis that the JD doesn't care about

### Step 4 — Strategic Fit Assessment

| Score Range | Assessment | Recommendation |
|-------------|-----------|----------------|
| 90-100% | Overqualified | May be underleveled — check seniority |
| 75-89% | Excellent match | Strong apply — minor tailoring recommended |
| 60-74% | Good match | Apply with targeted tailoring |
| 50-59% | Stretch | Apply if strategic — address gaps in cover letter |
| Below 50% | Under-qualified | Skip unless you have insider referral |

### Step 5 — Next Steps
After presenting results, suggest:
- "Run `/qualify` for a deeper strategic assessment — it flips the lens to evaluate how much they need you, not just whether you meet their bar."
- "Run `/research {company}` first if you want company-specific pain points to inform your qualification."

### Step 6 — Log Session
Save to `knowledge/sessions/match_{date}_{company-slug}_{role}.yaml`:
```yaml
date: YYYY-MM-DD
type: match
company: Company Name
slug: company-slug
role: Role Title
jd_hash: first-8-chars-of-sha256
match_score:
  required: XX
  preferred: XX
  overall: XX
required_skills:
  matched: [list]
  missing: [list]
  total: N
preferred_skills:
  matched: [list]
  missing: [list]
  total: N
transferable_skills:
  - yours: "X"
    theirs: "Y"
gaps: [list of missing required skills]
red_flags: [JD red flags identified]
recommendations: [top tailoring recommendations]
```

## Output Format
```
## Match Score: XX%
Required: XX% (N/M skills matched)
Preferred: XX% (N/M skills matched)

## Strengths (what matches well)
- ...

## Gaps (what's missing)
- Required: ...
- Preferred: ...

## Transferable Skills
- Your [X] maps to their [Y]

## Tailoring Recommendations
1. Emphasize: ...
2. Rephrase: ...
3. Trim: ...

## Red Flags in JD
- ...
```
