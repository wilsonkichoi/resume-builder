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
Check `knowledge/sessions/{slug}/company.yaml` for an existing CompanyProfile for this company. If found, load it and use `CompanyProfile.pain_points` to prioritize bullets that directly address company pain points — not just JD keyword matches.

Check `knowledge/sessions/{slug}/{role-slug}/` for an existing `/qualify` session (`*_qualify.yaml`, latest by date). If found, use it to sharpen tailoring:
- **Pain-solution match**: Lead with bullets that map directly to their pain points
- **ROI potential**: Prioritize bullets with metrics that connect to their specific needs
- **Leverage position**: Emphasize skills/experience that make you uniquely qualified
- **Growth alignment**: If high, include career trajectory signals; if low, trim them

Based on match analysis, qualify assessment (if available), and CompanyProfile (if available), create a plan:
- Which summary bullets to lead with
- Which skills categories to reorder/trim
- Which experience bullets to emphasize (move up) or trim (remove)
- Which projects to include/exclude based on skills.yaml role tags
- Which keywords from JD to inject into existing bullets
- Whether to include/exclude sabbatical

### Step 3 — Apply Tailoring
Determine the output directory: `knowledge/sessions/{company-slug}/{role-slug}/tailored/` (e.g., `knowledge/sessions/acme-corp/staff-engineer/tailored/`).

Create `resume.yaml` inside that directory (never modify the original `resume.yaml` in the project root):
- Reorder skills by JD relevance
- Reorder bullets within each role by relevance
- Rephrase bullets to include JD keywords (preserve meaning)
- Remove irrelevant bullets and projects
- Adjust summary paragraph for target role

### Step 4 — Verify
Run `resume-builder verify --resume knowledge/sessions/{company-slug}/{role-slug}/tailored/resume.yaml` to check:
- No fabricated claims
- All content traces to original resume.yaml
- No metrics were modified

### Step 5 — Generate Outputs
Run `resume-builder generate --resume knowledge/sessions/{company-slug}/{role-slug}/tailored/resume.yaml --output-dir knowledge/sessions/{company-slug}/{role-slug}/tailored/`

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

### Step 7 — Log Session (MANDATORY — do not present results until this step is complete)
Save to `knowledge/sessions/{company-slug}/{role-slug}/{date}_tailor.yaml`:
```yaml
date: YYYY-MM-DD
type: tailor
company: Company Name
slug: company-slug
role: Role Title
role_slug: role-slug
output_dir: knowledge/sessions/{company-slug}/{role-slug}/tailored/
sources_used:
  company_profile: true | false
  match_session: session-filename or null
  qualify_session: session-filename or null
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
  - knowledge/sessions/{company-slug}/{role-slug}/tailored/resume.yaml
  - knowledge/sessions/{company-slug}/{role-slug}/tailored/resume.pdf
  - knowledge/sessions/{company-slug}/{role-slug}/tailored/resume.docx
  - knowledge/sessions/{company-slug}/{role-slug}/tailored/index.html
  - knowledge/sessions/{company-slug}/{role-slug}/tailored/resume.md
```

Append to `knowledge/sessions/{company-slug}/{role-slug}/summary.md` (create with `# {Company Name} — {Role Title}` header if it doesn't exist):
```markdown
---

## {date} tailor

**Strategy**: {1-2 sentence summary of tailoring approach and rationale}
**Key changes from base resume**:
- {change category}: {what changed and why}
- {change category}: {what changed and why}
- {change category}: {what changed and why}
**Content removed**: {what was trimmed and why it's noise for this buyer}
**Scores**: ATS {before}→{after}, HR {before}→{after}
**Gaps remaining**: {what tailoring couldn't fix — cover letter territory}
**Output**: knowledge/sessions/{company-slug}/{role-slug}/tailored/
```

When running multiple tailoring passes in sequence, log EACH run individually as you complete it. Do not batch logging or defer it until after presentation.

## Output
Present the tailored resume with a diff summary showing what changed and why — only after Step 7 (Log Session) is complete.
