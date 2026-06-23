---
name: tailor
description: "Tailor resume for a specific job description. Use when: 'tailor resume', 'customize for job', 'apply for this role', 'optimize for JD'."
argument-hint: "[path to job description or paste JD text]"
---

# /tailor — Tailor Resume for a Job Description

## Purpose
Create a tailored version of the resume YAML optimized for a specific job description while enforcing anti-fabrication rules.

## Anti-Fabrication Rules (MANDATORY)
1. NEVER add technologies, metrics, or experiences not in resume.yaml
2. NEVER modify quantified metrics
3. You MAY reorder and trim skills categories
4. You MAY adjust header.title to align with the target role
5. You MAY rewrite the summary paragraph using JD keywords IF meaning is preserved
6. You MUST NOT modify experience, projects, or education sections in any way
7. You MUST preserve the original ordering of experience entries. Do not reorder companies or roles.
8. ALWAYS run verification after tailoring

## Writing Style Rules (MANDATORY)
- NEVER use em-dash (—) or en-dash (–) in generated text. Use commas, periods, or semicolons instead.
- NEVER use hyphens (-) as separators between clauses. Hyphens are only for compound words (e.g., "full-stack").
- Prefer direct, concrete language. Avoid filler phrases.

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
- How to adjust header.title to align with target role
- Which summary paragraph adjustments to make (keywords, positioning)
- Which skills categories to reorder or trim for JD relevance

### Step 3 — Apply Tailoring
Determine the output directory: `knowledge/sessions/{company-slug}/{role-slug}/tailored/` (e.g., `knowledge/sessions/acme-corp/staff-engineer/tailored/`).

Create `resume.yaml` inside that directory (never modify the original resume YAML in the project root):
- **header.title**: Adjust to align with the target role title/level
- **header** (other fields): Copy verbatim from baseline
- **summary**: Rewrite for target role using JD keywords (preserve factual claims)
- **skills**: Reorder categories by JD relevance, trim categories with no JD overlap
- **experience**: Copy verbatim from baseline — preserve exact order of companies and roles, no reordering, rephrasing, or trimming
- **projects**: Copy verbatim from baseline — no changes
- **education**: Copy verbatim from baseline — no changes

### Step 4 — Verify
Run `resume-builder verify --resume knowledge/sessions/{company-slug}/{role-slug}/tailored/resume.yaml` to check:
- No fabricated claims
- All content traces to original resume YAML
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
