# Resume Builder

A Claude Code plugin for resume management. Parse, generate, tailor, score, and verify resumes with anti-fabrication enforcement.

## What It Does

- **Single source of truth** — `resume.yaml` with provenance tracking on every bullet
- **Generate** resume outputs in Markdown, PDF, DOCX, and HTML from one YAML file
- **Tailor** resumes for specific job descriptions while preventing fabrication
- **Score** with ATS and HR rubrics
- **Match** against job descriptions with gap analysis
- **Review** with 6 AI personas (ATS bot, recruiter, hiring manager, HR screener, technical reviewer, engineer peer)
- **Verify** every claim traces back to source — catches fabricated metrics, technologies, and embellishments
- **Ingest** project artifacts to extract verified achievements with provenance

## Prerequisites

- [uv](https://docs.astral.sh/uv/) (Python package manager)
- [Claude Code](https://claude.ai/code) and/or [Codex CLI](https://github.com/openai/codex-cli)

## Installation

### Claude Code Plugin (recommended)

```bash
# Add the marketplace
/plugin marketplace add wilsonkichoi/resume-builder

# Install the plugin — select "Install for you, in this repo only (local scope)"
/plugin install resume-builder@wilsonkichoi-resume-builder
```

When prompted for install scope, choose **"Install for you, in this repo only"** (local scope). This keeps the plugin scoped to your project rather than applying globally.

After installation:

- Skills are available as `/resume-builder:init`, `/resume-builder:generate`, `/resume-builder:tailor`, etc.
- Agents appear in `/agents` (e.g., `resume-builder:ats-bot`, `resume-builder:hiring-manager`)
- MCP tools (`generate`, `verify`, `verify_against_generated`) are exposed automatically
- Auto-updates when the repo is updated

**Updating:**

```bash
/plugin marketplace update wilsonkichoi-resume-builder
```

> **Tip:** Enable auto-updates in `/plugin` → **Marketplaces** tab → select marketplace → enable auto-update.

### Codex CLI

```bash
codex plugin install wilsonkichoi/resume-builder
```

After installation:

- Skills are available as `/init`, `/generate`, `/tailor`, `/score`, `/match`, `/review`, `/ingest`, `/verify`
- Agents appear in `/agent` (e.g., `ats-bot`, `hiring-manager`, `engineer-peer`)
- MCP tools (`generate`, `verify`, `verify_against_generated`) are exposed automatically

> **Note:** Codex CLI does not support per-project plugin scoping. Installed plugins are always global. If you need project-level control, use Claude Code's local scope install instead.

### CLI Only (limited)

The CLI provides `resume-builder generate` and `resume-builder verify` without requiring an LLM. However, the full feature set — tailoring, scoring, matching, multi-persona review, and ingestion — requires Claude Code or Codex CLI skills.

```bash
uv tool install git+https://github.com/wilsonkichoi/resume-builder
```

This installs the package into an isolated environment at `~/.local/share/uv/tools/resume-builder/` and symlinks the `resume-builder` executable into `~/.local/bin/`. No clone or virtual environment management needed.

Then from your resume project directory:

```bash
resume-builder generate --format pdf,docx,html,md
resume-builder verify --resume resume.yaml
resume-builder verify --resume resume.yaml --generated resume_tailored.md
```

**Updating:**

```bash
uv tool upgrade resume-builder
```

### Local Plugin Testing

For development and testing only:

```bash
claude --plugin-dir /path/to/resume-builder
```

## Quick Start

### 1. Initialize your resume project

Open Claude Code in your resume project directory and run:

```
/resume-builder:init
```

This scans for existing resume files (PDF, DOCX, Markdown, YAML), interviews you to fill gaps, and creates:

```
your-resume-project/
  resume.yaml              # Source of truth
  knowledge/
    corrections.yaml       # Fabrication error log
    sessions/              # Session history
```

### 2. Generate outputs

```
/resume-builder:generate
```

Generates `resume.md`, `resume.pdf`, `resume.docx`, and `index.html` from `resume.yaml`.

### 3. Add achievements from a project

```
/resume-builder:ingest ~/src/my-project
```

Analyzes source code, READMEs, infrastructure-as-code, and git history. Extracts verifiable facts, drafts resume bullets with provenance, and asks for your confirmation before updating `resume.yaml`.

### 4. Tailor for a job description

```
/resume-builder:tailor
```

Paste a job description. The skill reorders, emphasizes, and trims your resume for the target role while enforcing anti-fabrication rules.

### 5. Score your resume

```
/resume-builder:score
```

Scores against ATS (8 components) and HR (6 dimensions) rubrics with actionable improvement suggestions.

### 6. Match against a job description

```
/resume-builder:match
```

Identifies skill matches, gaps, and suggests how to position existing experience.

### 7. Multi-persona review

```
/resume-builder:review
```

Gets feedback from 6 AI personas:

| Persona | Focus |
|---------|-------|
| ATS Bot | Keyword parsing, formatting compatibility |
| Recruiter | 6-second scan impression |
| Hiring Manager | Technical depth and relevance |
| HR Screener | Red flags, compliance, gaps |
| Technical Reviewer | Accuracy of technical claims |
| Engineer Peer | Overclaim detection (most valuable for staff+ level) |

### 8. Verify anti-fabrication

```
/resume-builder:verify
```

Checks:
- All bullets have verified provenance
- Tailored output matches source claims (fuzzy matching with severity levels)
- No previously corrected errors are reintroduced
- No fabricated technologies or metrics

## MCP Tools

The MCP server exposes three tools that both Claude Code and Codex can call directly:

| Tool | Description |
|------|-------------|
| `generate` | Generate resume outputs from resume.yaml. Parameters: `resume_path`, `formats`, `output_dir` |
| `verify` | Check provenance of all claims. Parameters: `resume_path` |
| `verify_against_generated` | Anti-fabrication diff check. Parameters: `resume_path`, `generated_path`, `corrections_path` |

## Anti-Fabrication Rules

Enforced across all skills and tools:

1. Never add technologies, metrics, or experiences not in `resume.yaml`
2. Never modify quantified metrics (dates, percentages, numbers)
3. Never invent performance numbers, cost savings, or user counts
4. Never claim certifications, degrees, or titles not in the source
5. Never embellish shared work as solo accomplishments
6. May reorder, emphasize, or trim existing content
7. May rephrase bullets to use JD keywords if meaning is preserved

## resume.yaml Schema

```yaml
header:
  name: "Jane Doe"
  title: "Senior Software Engineer"
  location: "San Francisco, CA"
  email: "jane@example.com"
  linkedin: "linkedin.com/in/janedoe"
  github: "github.com/janedoe"

summary:
  paragraph: "Software engineer with 10+ years..."
  bullets:
    - label: "Track Record"
      text: "Scaled platform from 100 to 10K RPS..."
      provenance: { source: "manual", artifacts: [], verified: true }

skills:
  - category: "Languages"
    items: "Python, Go, TypeScript"
    provenance: { source: "manual", artifacts: [], verified: true }

experience:
  - company: "Acme Corp"
    location: "San Francisco, CA"
    dates: "2018 - 2024"
    roles:
      - title: "Senior Software Engineer"
        dates: "2021 - 2024"
        bullets:
          - label: "API Redesign"
            text: "Redesigned REST API layer..."
            technologies: [FastAPI, Python, Redis]
            metrics: ["500ms to 120ms", "3x throughput"]
            provenance:
              source: "ingested:2025-01-15_acme"
              artifacts: ["github:janedoe/acme-api"]
              verified: true

projects:
  - name: "OpenTracer"
    url: "https://github.com/janedoe/opentracer"
    description: "Distributed tracing library..."
    technologies: [Python, OpenTelemetry]
    provenance: { source: "manual", artifacts: ["github:janedoe/opentracer"], verified: true }

education:
  degree: "B.S. Computer Science"
  institution: "UC Berkeley"
```

## Provenance

Every bullet carries a `provenance` field:
- `source`: `"manual"` (hand-written) or `"ingested:{session-id}"` (from `/ingest`)
- `artifacts`: Source references (GitHub URLs, blog posts, docs)
- `verified`: Has the user confirmed this claim?
