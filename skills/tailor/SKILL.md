---
name: tailor
description: "Tailor resume for a specific job description. Use when: 'tailor resume', 'customize for job', 'apply for this role', 'optimize for JD'."
argument-hint: "[path to job description or paste JD text]"
---

# /tailor — Tailor Resume for a Job Description

## Purpose
Create a tailored version of resume.yaml optimized for a specific job description while enforcing anti-fabrication rules.

## Anti-Fabrication Rules (MANDATORY)
1. NEVER add technologies, metrics, or experiences not in resume.yaml
2. NEVER modify quantified metrics
3. You MAY reorder sections and bullets
4. You MAY emphasize or trim existing content
5. You MAY rephrase bullets to use JD keywords IF meaning is preserved
6. ALWAYS run verification after tailoring

## Process

### Step 1 — Analyze
Run /match analysis to understand fit, gaps, and recommendations.

### Step 2 — Generate Tailoring Plan
Check `knowledge/companies/` for an existing CompanyProfile for this company. If found, load it and use `CompanyProfile.pain_points` to prioritize bullets that directly address company pain points — not just JD keyword matches.

Based on match analysis (and CompanyProfile if available), create a plan:
- Which summary bullets to lead with
- Which skills categories to reorder/trim
- Which experience bullets to emphasize (move up) or trim (remove)
- Which projects to include/exclude based on skills.yaml role tags
- Which keywords from JD to inject into existing bullets
- Whether to include/exclude sabbatical

### Step 3 — Apply Tailoring
Determine the output directory: `tailored/{date}_{company-slug}_{role}/` (e.g., `tailored/2026-04-29_acme-corp_staff-engineer/`).

Create `resume.yaml` inside that directory (never modify the original `resume.yaml` in the project root):
- Reorder skills by JD relevance
- Reorder bullets within each role by relevance
- Rephrase bullets to include JD keywords (preserve meaning)
- Remove irrelevant bullets and projects
- Adjust summary paragraph for target role

### Step 4 — Verify
Run `resume-builder verify --resume tailored/{date}_{company-slug}_{role}/resume.yaml` to check:
- No fabricated claims
- All content traces to original resume.yaml
- No metrics were modified

### Step 5 — Generate Outputs
Run `resume-builder generate --resume tailored/{date}_{company-slug}_{role}/resume.yaml --output-dir tailored/{date}_{company-slug}_{role}/`

### Step 5.5 — Quick Persona Check

Before scoring, spot-check the tailored resume with two personas:

1. Read `agents/recruiter.agent.md` — does the tailored version still pass the 6-second scan?
2. Read `agents/hiring-manager.agent.md` — does the reordering create a coherent narrative for this role?
3. *(If CompanyProfile exists)* Read `agents/sales-strategist.agent.md` — is the tailored resume selling solutions to this company's pain points, or just listing features?

Output a brief check:
- **Recruiter**: PASS / FLAG (1-line explanation if flagged)
- **Hiring Manager**: PASS / FLAG (1-line explanation if flagged)
- **Sales Strategist** *(if applicable)*: PASS / FLAG (1-line explanation if flagged)

If any flags an issue, note it in the tailoring report. Do not block generation.

### Step 6 — Score
Run /score against the JD to see improvement:
- Report before/after ATS and HR scores
- Highlight which changes had the most impact

### Step 7 — Log Session
Save to `knowledge/sessions/tailor_{date}_{company}_{role}.yaml`:
```yaml
date: YYYY-MM-DD
type: tailor
company: Company Name
slug: company-slug
role: Role Title
output_dir: tailored/{date}_{company-slug}_{role}/
match_score: { required: XX, preferred: XX, overall: XX }
gaps: [missing skills]
tailoring_decisions:
  - action: emphasized
    target: specific-bullets
  - action: trimmed
    target: irrelevant-content
  - action: rephrased
    target: bullets-with-jd-keywords
scores:
  before: { ats: XX, hr: XX }
  after: { ats: XX, hr: XX }
output_files:
  - tailored/{date}_{company-slug}_{role}/resume.yaml
  - tailored/{date}_{company-slug}_{role}/resume.pdf
  - tailored/{date}_{company-slug}_{role}/resume.docx
  - tailored/{date}_{company-slug}_{role}/index.html
  - tailored/{date}_{company-slug}_{role}/resume.md
```

## Output
Present the tailored resume with a diff summary showing what changed and why.
