---
name: research
description: "Research a company and build an intelligence profile. Use when: 'research company', 'company profile', 'learn about company', 'company intelligence', 'what do I need to know about'."
argument-hint: "[company name + any links to job postings, company pages, LinkedIn posts, blog posts, etc.]"
---

# /research — Company Intelligence Gathering

## Purpose
Build a CompanyProfile from user-provided documents and supplementary web research. The profile captures what the company does, what problems they face, what they're investing in, and what kind of candidate would solve their pain — not just match their keywords.

## Anti-Fabrication Rules (MANDATORY)
1. EVERY fact must be traceable to a source URL or document
2. Inferences MUST be labeled with `is_inference: true` — they are hypotheses, not facts
3. "Unknown" is ALWAYS acceptable — NEVER fill gaps with guesses
4. If sources contradict each other, note BOTH and let the user decide
5. A single Glassdoor review is a low-confidence inference, not a fact
6. Marketing language from company websites is company-stated, NOT objective fact — label it as such
7. NEVER fabricate pain points — infer them from evidence and clearly label the reasoning

## Process

### Step 1 — Gather Source Documents
Ask the user what they have. Accept URLs and documents in priority order:

1. **Job posting** (highest signal — reveals what they need and why)
2. **Company website** (about, team, values, products)
3. **Engineering/tech blog** (reveals real technical challenges and culture)
4. **LinkedIn posts** (from hiring managers, team leads, company page)
5. **GitHub repos** (tech stack, code quality, open-source investment)
6. **Glassdoor/Blind reviews** (culture signals, handle with skepticism)
7. **Press releases / news articles** (funding, launches, pivots)
8. **Conference talks / podcasts** (deep technical and strategic signals)

Always ask: "Do you have any of these? The more sources, the sharper the profile."

Check `knowledge/companies/` for an existing profile for this company. If found, ask: "I have an existing profile from {date}. Update it with new sources, or start fresh?"

### Step 2 — Process User-Provided Documents
For each provided document or URL, fetch and extract structured facts. Tag every fact with its source URL. Separate stated facts from inferences. Note source dates — recent sources are higher confidence.

### Step 3 — Supplementary Web Research
Use WebSearch to fill gaps not covered by user-provided documents — engineering culture, funding, tech stack, recent news, hiring activity.

For each result, apply the same extraction and tagging process as Step 2.

If web tools are unavailable, work only with user-provided documents and note what could not be verified.

### Step 4 — Build CompanyProfile
Assemble all facts into the CompanyProfile structure:

- **basics**: name, slug, industry, size, stage, location, funding, website
- **mission_vision**: mission, vision, values (label as company-stated)
- **products_services**: what they sell, who they serve
- **tech_stack**: technologies with context for how they're used
- **culture_signals**: work style, values in practice (with sentiment)
- **recent_news**: funding, launches, pivots, leadership changes
- **growth_signals**: hiring velocity, new products, expansion
- **key_people**: hiring managers, team leads, notable engineers

For each field:
- Record the source
- Mark inferences with `is_inference: true`
- Set confidence: `high` (directly stated in primary source), `medium` (stated in secondary source or inferred from multiple sources), `low` (single data point or old source)
- Leave unknown fields empty — do NOT guess

### Step 5 — Pain Point Synthesis
This is the most valuable step. Infer company pain points from:

1. **JD requirements** — Why do they need this skill? What problem does it solve?
2. **Tech stack signals** — Migrating? Scaling? Legacy modernization?
3. **Glassdoor themes** — What do employees complain about? (process, tooling, tech debt)
4. **Blog post topics** — What challenges are they writing about?
5. **Hiring velocity** — Are they staffing up a specific team? Why?
6. **Growth stage** — Startup scaling problems vs. enterprise modernization vs. pivot

For each pain point:
- Write a clear description
- List all evidence (source URLs)
- Mark as `is_inference: true` (pain points are almost always inferences)
- Assess severity: `high` (multiple evidence sources, core to business), `medium` (some evidence), `low` (single data point)

Present pain points as hypotheses: "Based on {evidence}, they likely face {problem}."

### Step 6 — User Review
Present the completed profile organized by section. For each section, show the facts and their sources.

Ask: "Is anything here wrong, missing, or outdated? Anything you know from conversations, interviews, or personal research that I should add?"

Apply corrections. The user's direct knowledge overrides web research — mark user-provided corrections with `source: "user-provided"` and `confidence: "high"`.

### Step 7 — Persist and Log (MANDATORY — do not present results until this step is complete)
Save the CompanyProfile to `knowledge/companies/{slug}.yaml`.

Log session to `knowledge/sessions/`:
```yaml
date: YYYY-MM-DD
type: research
company: Company Name
slug: company-slug
sources_provided: [list of user-provided URLs]
sources_fetched: [list of web-searched URLs]
facts_extracted: N
inferences_made: N
unknowns: [list of fields with no data]
pain_points_identified: N
output_file: knowledge/companies/{slug}.yaml
```

When running multiple research sessions in sequence, log EACH run individually as you complete it. Do not batch logging or defer it until after presentation.

### Step 8 — Report
Present to the user:
- Total facts captured vs. unknowns
- Number of inferences vs. directly-sourced facts
- Sources used
- Suggested next steps: "Run `/qualify` to assess strategic fit" or "Provide more sources for a sharper profile"

## Output
The CompanyProfile YAML file in `knowledge/companies/`, plus a summary presented to the user with facts, inferences, unknowns, and recommended next steps.

## Options
- With company name: `/research Acme Corp`
- With links: `/research Acme Corp https://acme.com/careers/backend-engineer https://acme.com/blog/scaling`
- Update existing: `/research Acme Corp` (will detect existing profile and offer to update)
