---
name: apply
description: "End-to-end application pipeline: research, match, qualify, tailor, score, review, cover letter, verify. Use when: 'apply to job', 'full application', 'e2e application', 'run the full pipeline', 'apply to this role'."
argument-hint: "[company name] [path to JD or paste JD text] [optional: research links]"
---

# /apply — End-to-End Application Pipeline

## Purpose
Fire-and-forget pipeline that runs the full application workflow from company research through final deliverables. Produces a tailored resume (PDF/DOCX/MD/HTML), cover letter, scores, and review — all in one shot.

Optimized for multi-job-same-company use: company research is performed once and reused across subsequent runs.

## Anti-Fabrication Rules (MANDATORY)
1. All sub-skills enforce their own anti-fabrication rules — this pipeline does not relax them
2. The final `/verify` step is the safety net — if it fails, flag the output clearly
3. No fabrication is acceptable regardless of pipeline speed or convenience

## Process

### Step 1 — Research (conditional)
Extract the company name from the JD or user input. Check `knowledge/companies/{slug}.yaml` for an existing CompanyProfile.

- **If profile exists**: Skip research. Log: "Reusing existing CompanyProfile for {company} (researched {date})."
- **If no profile exists**: Run `/research` with any links the user provided. Use non-interactive mode — do not ask for additional sources, work with what's given plus web search.

### Step 2 — Match
Run `/match` against the JD. Do not prompt the user — proceed directly with resume.yaml and the JD.

This produces: match scores, gap analysis, transferable skills, and tailoring recommendations.

### Step 3 — Qualify
Run `/qualify` using the CompanyProfile and JD. Do not prompt the user for culture preferences — score culture_fit with available signals and note confidence as low if preferences are unknown.

This produces: dimensional scores, weighted average, and strategic brief.

### Step 4 — Tailor
Run `/tailor` against the JD. This internally:
- Uses the CompanyProfile pain points for prioritization
- Uses the match session for gap awareness
- Uses the qualify session for positioning
- Produces tailored resume.yaml in `tailored/{date}_{company-slug}_{role}/`
- Generates PDF, DOCX, HTML, MD outputs
- Runs its own quick persona check

Do not prompt for tailoring preferences — use match/qualify data to make decisions.

### Step 5 — Score
Run `/score` against the JD using the tailored resume (`tailored/{date}_{company-slug}_{role}/resume.yaml`).

This produces: ATS and HR scores with component breakdowns.

### Step 6 — Review
Run `/review` with the JD as context, evaluating the tailored resume. All personas report findings.

This is report-only — findings do not feed back into tailoring.

### Step 7 — Cover Letter
Run `/cover-letter` using the JD. This internally:
- Uses the CompanyProfile for company-specific hooks
- Uses the match session for gap mitigation
- Uses the qualify session for positioning angle
- Auto-selects the strongest hook type based on available data
- Saves to `tailored/{date}_{company-slug}_{role}/cover_letter.md`

Do not prompt for hook preference or talking points — auto-select based on qualify scores:
- Pain-solution match >= 7 → problem-solver hook
- ROI potential >= 7 → impressive-achievement hook
- Otherwise → specific-company-knowledge hook (if CompanyProfile exists) or impressive-achievement hook

### Step 8 — Verify
Run `/verify` on the tailored resume (`tailored/{date}_{company-slug}_{role}/resume.yaml`).

Report status: PASS or FAIL with details. Do not block output delivery on verification — report it alongside results.

### Step 9 — Log Session (MANDATORY — do not present results until this step is complete)
Save to `knowledge/sessions/apply_{date}_{company-slug}_{role}.yaml`:
```yaml
date: YYYY-MM-DD
type: apply
company: Company Name
slug: company-slug
role: Role Title
output_dir: tailored/{date}_{company-slug}_{role}/
research_skipped: true | false
company_profile: knowledge/companies/{slug}.yaml
sub_sessions:
  research: session-filename or null
  match: session-filename
  qualify: session-filename
  tailor: session-filename
  score: session-filename
  review: session-filename
  cover_letter: session-filename
  verify: pass | fail
scores:
  match: { required: XX, preferred: XX, overall: XX }
  qualify: { weighted_average: X.X, recommendation: strong-pursue | pursue-with-caution | consider-passing }
  ats: XX
  hr: XX
verification: pass | fail
output_files:
  - tailored/{date}_{company-slug}_{role}/resume.yaml
  - tailored/{date}_{company-slug}_{role}/resume.pdf
  - tailored/{date}_{company-slug}_{role}/resume.docx
  - tailored/{date}_{company-slug}_{role}/index.html
  - tailored/{date}_{company-slug}_{role}/resume.md
  - tailored/{date}_{company-slug}_{role}/cover_letter.md
```

## Output
Present a consolidated summary only after Step 9 is complete:

```
## Application Complete: {Company} — {Role}

### Scores
| Metric | Score |
|--------|-------|
| Match (overall) | XX% |
| Qualify (weighted avg) | X.X/10 — {recommendation} |
| ATS | XX/100 |
| HR | XX/100 |

### Verification
{PASS | FAIL with details}

### Review Highlights
- Top strength: ...
- Top concern: ...
- Consensus score: X.X/10

### Deliverables
All files in `tailored/{date}_{company-slug}_{role}/`:
- resume.yaml (tailored)
- resume.pdf
- resume.docx
- index.html
- resume.md
- cover_letter.md

### Strategic Position
{One-paragraph summary from /qualify strategic brief — how to position in interviews}
```

## Options
- First run for a company: `/apply Acme Corp jd.txt https://acme.com/about https://acme.com/blog`
- Subsequent jobs at same company: `/apply Acme Corp jd_backend.txt` (reuses CompanyProfile)
- Minimal: `/apply "Company Name" path/to/jd.txt`

## Non-Interactive Mode
This skill runs all sub-skills in non-interactive mode. Sub-skills that normally prompt for user input instead use these defaults:
- `/research`: Work with provided links + web search, no source-gathering prompt
- `/cover-letter`: Auto-select hook type, no preference prompt
- `/qualify`: Score culture_fit with available signals, no preference prompt
- `/tailor`: Use match/qualify data for decisions, no tailoring preference prompt
- `/review`: Run all applicable personas without selection prompt
