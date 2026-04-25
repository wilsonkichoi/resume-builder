---
name: ingest
description: "Analyze project artifacts and propose verified resume updates. Use when: 'ingest project', 'add project to resume', 'update resume with', 'I finished a project', or user provides source code/GitHub/blog/demo links."
argument-hint: "[path to project, GitHub URL, blog post, or demo link]"
---

# /ingest — Ingest Project Artifacts into Resume

## Purpose
Analyze real project artifacts (source code, GitHub repos, blog posts, demos) and propose verified resume updates. Every claim must trace back to a source artifact.

## Anti-Fabrication Rules (MANDATORY)
- NEVER invent metrics (performance numbers, cost savings, user counts) unless provided by the user
- NEVER claim technologies that appear only as transitive dependencies
- NEVER embellish scope beyond what the code demonstrates
- When you INFER something (e.g., scale from load test config), explicitly ASK the user to confirm
- Provenance is REQUIRED on every proposed bullet

## Process

### Step 1 — Gather Artifacts
Ask the user what they have:
- Source code path (local directory)
- GitHub repository URL
- Blog post or write-up
- YouTube talk/demo link
- Architecture diagrams
- Any metrics they can provide (users, requests/sec, cost savings, etc.)

### Step 2 — Analyze Artifacts
For source code:
- Read `pyproject.toml`, `package.json`, `requirements.txt`, `Cargo.toml` for tech stack
- Read infrastructure-as-code (CDK, Terraform, CloudFormation) for architecture
- Read tests for scale and coverage metrics
- Read README for project description and purpose
- Check git log for contribution scope and timeline

For GitHub repos:
- Check repo description, topics, and README
- Review languages and dependency files
- Look at CI/CD workflows for deployment patterns

For blog posts / demos:
- Extract claims and check if they're supported by code
- Note any metrics mentioned with their context

### Step 3 — Extract Verifiable Facts
Categorize findings:
- **Technologies**: Only include if meaningfully used (imported AND used in core logic, not just transitive)
- **Architecture**: Patterns visible in the code (event-driven, serverless, microservices, etc.)
- **Scale metrics**: ONLY what's provable from artifacts. Flag anything inferred.
- **Test coverage**: Number of tests, types of tests
- **Unique aspects**: What makes this project notable?

### Step 4 — Draft Resume Bullets
Generate 3-5 bullet options per project using the X-Y-Z formula:
> "Accomplished [X] as measured by [Y] by doing [Z]"

Each bullet must include:
```yaml
- label: "Descriptive Label"
  text: "The bullet text"
  technologies: [list, of, verified, tech]
  metrics: ["only verified metrics"]
  provenance:
    source: "ingested:{date}_{project-name}"
    artifacts: ["github:user/repo", "blog:post-name.md"]
    verified: false  # Set to false until user confirms
```

### Step 5 — Propose Updates
Present to the user:
1. **Proposed resume.yaml additions** — new project entry and/or new role bullets
2. **Proposed skills.yaml additions** — new technologies with role tags
3. **Flags** — anything that needs user confirmation (inferred metrics, scope claims)
4. **Questions** — ask about metrics you couldn't find in artifacts

Wait for user review and approval before making any changes.

### Step 6 — Apply and Verify
After user approval:
1. Update resume.yaml with approved content (set `verified: true` on confirmed items)
2. Update skills.yaml if new technologies were approved
3. Run `rb verify --resume resume.yaml` to confirm provenance integrity
4. Log the session to `knowledge/sessions/ingest_{date}_{project}.yaml`

## Session Log Format
```yaml
date: YYYY-MM-DD
type: ingest
project: project-name
artifacts_analyzed:
  - type: source_code
    path: /path/to/project
  - type: github
    url: https://github.com/user/repo
facts_extracted:
  technologies: [list]
  architecture: [patterns]
  metrics: [verified metrics]
bullets_proposed: 5
bullets_accepted: 3
bullets_rejected: 2
skills_added: [new skills]
```

## Output Requirements
- Present findings in a clear, structured format
- Clearly separate VERIFIED facts from INFERRED claims
- Always ask before modifying resume.yaml
- Bold key technologies and metrics in proposed bullets
