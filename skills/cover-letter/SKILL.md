---
name: cover-letter
description: "Generate a tailored cover letter for a job description. Use when: 'write cover letter', 'cover letter', 'application letter', 'write a letter for this job'."
argument-hint: "[path to job description or paste JD text]"
---

# /cover-letter — Generate Tailored Cover Letter

## Purpose
Generate a cover letter tailored to a specific job description using resume.yaml as the source of truth. Every factual claim must trace back to resume.yaml — narrative synthesis is allowed, fabrication is not.

## Anti-Fabrication Rules (MANDATORY)
1. NEVER add technologies, metrics, or experiences not in resume.yaml
2. NEVER modify quantified metrics from resume.yaml
3. NEVER invent company knowledge the user did not provide
4. You MAY synthesize narrative connecting multiple verified resume facts
5. You MAY reference company information provided by the user or from public knowledge
6. You MAY frame gaps positively but NEVER claim skills that do not exist
7. ALWAYS run claim verification after drafting

## Process

### Step 1 — Gather Inputs
- Read `resume.yaml` from the project root.
- Accept JD as file path or pasted text. A JD is **required** — a cover letter without a target is generic and weak.
- Check `knowledge/companies/` for an existing CompanyProfile. If found, load it — this replaces the need to ask the user for company research. Use `CompanyProfile.pain_points` for problem-solver hooks, `CompanyProfile.recent_news` for specific-company-knowledge hooks, and `CompanyProfile.mission_vision` + `CompanyProfile.culture_signals` for the closing paragraph.
- Check `knowledge/sessions/` for existing `/match` sessions for this company/role. If found, read the match analysis to leverage gap data, transferable skills, and tailoring recommendations.
- Check `knowledge/sessions/` for existing `/qualify` sessions for this company/role. If found, use the strategic brief to strengthen positioning — lead with pain-solution match evidence, use leverage signals for confident tone, and reference ROI potential metrics in the qualification paragraph.
- Ask the user for optional inputs:
  - **Company research** *(skip if CompanyProfile exists)*: "Do you know anything specific about this company — mission, recent news, team culture, specific projects? This strengthens the opening hook."
  - **Talking points**: "Any specific experiences or angles you want to emphasize?"
  - **Hook preference**: "Any preference for opening style?" (list the 5 types below, or auto-select the strongest based on available context)

### Step 2 — Run /match Analysis
If no existing match session found for this company/role, run `/match` analysis against the JD. This provides:
- Required/preferred skill match scores
- Gap analysis and transferable skills
- Tailoring recommendations

### Step 3 — Plan the Cover Letter
Based on match analysis and user inputs, create a plan:

**Hook type**: Select the strongest opening based on available context — company pain points, referrals, standout achievements, or domain expertise. Leverage CompanyProfile data if available. If a `/qualify` session exists with a high pain-solution match score, prefer the problem-solver hook.

**Strongest qualification**: Identify the 1-2 resume bullets that best match the JD's top requirements. If a `/qualify` session exists, use its ROI potential evidence to select bullets with the strongest metric-to-pain-point mapping.

**Gap mitigation**: For significant gaps from `/match`, plan how to address them — frame transferable skills, pivot to strengths. If `/qualify` scored leverage_position highly, lean into what makes you uniquely qualified rather than apologizing for gaps.

**Closing strategy**: Strong match -> confident ask. Stretch role -> emphasize eagerness and adjacent experience.

Present the plan to the user for approval before drafting.

### Step 4 — Draft the Cover Letter
Write the cover letter following this structure (250-400 words total):

- **Paragraph 1 (2-3 sentences)**: Hook + position identification. Name the company and role. Open with the selected hook type.
- **Paragraph 2 (3-5 sentences)**: Strongest qualification with metrics. Pull directly from resume.yaml bullets. Use X-Y-Z formula evidence from the most relevant experience.
- **Paragraph 3 (2-4 sentences)**: Additional value + gap mitigation. Connect secondary qualifications. Address the biggest gap with a transferable skill or genuine framing.
- **Paragraph 4 (2-3 sentences)**: Closing with call-to-action. Express enthusiasm, reference a specific company value or project, and include a clear next-step ask.

### Step 5 — Claim Verification
For every factual claim in the draft, verify it traces to resume.yaml:

```
## Claim Verification
- [VERIFIED] "reduced p99 latency by 76%" <- resume.yaml > Company > Role > bullet
- [VERIFIED] "built event pipeline handling 2M events/day" <- resume.yaml > Company > Role > bullet
- [NARRATIVE] "This combination of API optimization and event-driven architecture..." <- synthesis of verified claims
- [COMPANY] "Your team's recent work on [X]..." <- user-provided research, not a resume claim
```

Flag any claim that cannot be traced. Do not proceed until all factual claims are verified or removed.

### Step 5.5 — Cover Letter Review

Read `agents/cover-letter-reviewer.agent.md` and evaluate the draft from a hiring manager's perspective.

Output a brief check:
- **Hook Effectiveness**: PASS / FLAG
- **Company Research Depth**: PASS / FLAG
- **Claim-Resume Alignment**: PASS / FLAG
- **Tone**: PASS / FLAG
- **Beyond-Resume Value**: PASS / FLAG

If a CompanyProfile exists for the target company, also read `agents/sales-strategist.agent.md` and evaluate whether the cover letter sells solutions or features:
- **Buyer Empathy**: PASS / FLAG
- **Problem-Solution Framing**: PASS / FLAG

If any item is flagged, note the issue and suggest a revision. Do not block output.

### Step 6 — Output
Save the cover letter to `cover_letter_{company-slug}_{role}.md` in the project root.

If a tailored output directory exists for this company/role (`tailored/{date}_{company-slug}_{role}/`), also save a copy there so all application materials are co-located.

Present the full cover letter to the user with:
- The verification results from Step 5
- The review results from Step 5.5
- Word count

### Step 7 — Log Session
Save to `knowledge/sessions/cover-letter_{date}_{company}_{role}.yaml`:
```yaml
date: YYYY-MM-DD
type: cover-letter
company: Company Name
slug: company-slug
role: Role Title
sources_used:
  company_profile: true | false
  match_session: session-filename or null
  qualify_session: session-filename or null
match_score: { required: XX, preferred: XX, overall: XX }
hook_type: specific-company-knowledge | mutual-connection | problem-solver | impressive-achievement | industry-insight
gaps_addressed: [list of gaps mitigated]
claims_verified: X
claims_narrative: X
claims_company: X
reviewer_flags: [list of any flagged items]
word_count: XXX
output_file: cover_letter_{company-slug}_{role}.md
tailored_dir_copy: tailored/{date}_{company-slug}_{role}/cover_letter.md | null
```

## Options
- With JD file: `/cover-letter path/to/jd.txt`
- With pasted JD: `/cover-letter` (then paste JD when prompted)
- With hook preference: specify in your message, e.g., "write a cover letter for this JD, lead with my strongest achievement"
