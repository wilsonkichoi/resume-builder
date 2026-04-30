---
name: score
description: "Score resume against a job description for ATS and HR readiness. Use when: 'score resume', 'ATS score', 'how does my resume score', 'rate my resume'."
argument-hint: "[path to job description or paste JD text]"
---

# /score — ATS + HR Resume Scoring

## Purpose
Evaluate resume against a job description using structured rubrics. Produces honest scores (target 75-85%, not inflated 100%).

## ATS Rubric (8 Components)

Score each 1-10, then compute weighted average:

1. **Keyword Match Rate** (weight: 25%)
   - Count exact phrase matches between JD requirements and resume
   - Exact phrases correlate 10.6x with callbacks vs partial matches
   - Score: 9-10 = 90%+ phrases matched, 7-8 = 70-89%, 5-6 = 50-69%, <5 = below 50%

2. **Keyword Density** (weight: 15%)
   - Critical keywords should appear 2-4x across resume
   - Important keywords 1-2x
   - Score: 9-10 = optimal density, 5-6 = sparse, <5 = missing critical keywords

3. **Section Completeness** (weight: 10%)
   - Must have: Summary, Skills, Experience, Education
   - Nice to have: Projects, Certifications
   - Score: 10 = all sections present, -2 per missing required section

4. **Format Compliance** (weight: 10%)
   - Single-column layout, standard section headers
   - No tables, no multi-column, no images
   - Contact info in document body (not headers/footers)
   - Score: 10 = fully compliant, -3 per violation

5. **Contact Info Completeness** (weight: 5%)
   - Name, email, phone, LinkedIn, location
   - Score: 10 = all present, -2 per missing

6. **Date Consistency** (weight: 5%)
   - Consistent format (Month Year or Year only)
   - No gaps without explanation
   - Chronological ordering
   - Score: 10 = consistent, -2 per inconsistency

7. **Length** (weight: 10%)
   - Target: 1-2 pages for individual contributor, 2-3 for executive
   - Score: 10 = optimal, 7 = slightly over/under, <5 = significantly off

8. **Skills-to-Experience Alignment** (weight: 20%)
   - Every skill listed in Skills section should appear in at least one Experience bullet
   - "Orphan skills" (listed but never demonstrated) are red flags
   - Score: 10 = all skills demonstrated, -1 per orphan skill

## HR Rubric (6 Dimensions)

Score each 1-10:

1. **Role Relevance** (weight: 25%)
   - How well does experience align with the JD's core requirements?
   - Are the most relevant roles/bullets prominently positioned?

2. **Impact Clarity** (weight: 20%)
   - Are achievements quantified with X-Y-Z formula?
   - Metrics present: revenue, %, time saved, scale, before/after

3. **Career Progression** (weight: 15%)
   - Does the trajectory show growth?
   - Are promotions and increasing scope visible?

4. **Recency Weighting** (weight: 15%)
   - Is the most relevant experience from the last 3-5 years?
   - Are recent roles given more space than older ones?

5. **Readability** (weight: 15%)
   - Bullet length (1-2 lines ideal)
   - Action verbs leading each bullet
   - Jargon-to-clarity ratio appropriate for the audience

6. **Differentiation** (weight: 10%)
   - What makes this candidate stand out?
   - Is there a unique combination of skills or experiences?

## Output Format

```
## ATS Score: XX/100
| Component | Score | Notes |
|-----------|-------|-------|
| Keyword Match | X/10 | ... |
| ... | ... | ... |

## HR Score: XX/100
| Dimension | Score | Notes |
|-----------|-------|-------|
| Role Relevance | X/10 | ... |
| ... | ... | ... |

## Top 3 Recommendations
1. ...
2. ...
3. ...

## Score Interpretation
- 85-100: Strong match — apply with confidence
- 70-84: Good match — minor optimizations recommended
- 55-69: Moderate match — significant tailoring needed
- Below 55: Weak match — consider if this role is a stretch
```

## Session Log
Save to `knowledge/sessions/score_{date}_{company-slug}_{role}.yaml`:
```yaml
date: YYYY-MM-DD
type: score
company: Company Name
slug: company-slug
role: Role Title
jd_hash: first-8-chars-of-sha256
resume_source: resume.yaml | tailored/{date}_{company-slug}_{role}/resume.yaml
scores:
  ats:
    total: XX
    keyword_match: X
    keyword_density: X
    section_completeness: X
    format_compliance: X
    contact_info: X
    date_consistency: X
    length: X
    skills_alignment: X
  hr:
    total: XX
    role_relevance: X
    impact_clarity: X
    career_progression: X
    recency: X
    readability: X
    differentiation: X
recommendations:
  - "..."
  - "..."
  - "..."
```

## Important
- Be HONEST. A perfect 100% is virtually impossible and dishonest.
- Target scores of 75-85% for well-matched roles.
- Provide actionable recommendations, not generic advice.
- Reference specific bullets and skills in your scoring notes.
