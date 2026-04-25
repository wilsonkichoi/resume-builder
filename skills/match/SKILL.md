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
Extract and categorize:
- **Required skills** — explicitly stated as required/must-have
- **Preferred skills** — nice-to-have, bonus, preferred
- **Domain terminology** — industry-specific terms
- **Experience level** — years, seniority signals
- **Red flags** — overwork language, "rockstar", vague compensation

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
