# Resume Builder

A Claude Code plugin for resume management. Parse, generate, tailor, score, and verify resumes with anti-fabrication enforcement. Includes company research and strategic qualification to approach job search like a sales professional — understand the buyer's pain before pitching.

## What It Does

- **Single source of truth** — `resume.yaml` with provenance tracking on every bullet
- **Setup** bootstraps your project and writes plugin docs so the AI has full context every session
- **Import** existing resumes from any format (PDF, DOCX, Markdown, YAML) into `resume.yaml`
- **Generate** resume outputs in Markdown, PDF, DOCX, and HTML from one YAML file
- **Research** companies to build intelligence profiles — pain points, tech stack, culture, growth signals
- **Qualify** opportunities with dimensional scoring — assess how much they need you, not just whether you meet their bar
- **Tailor** resumes for specific job descriptions while preventing fabrication
- **Score** with ATS and HR rubrics
- **Match** against job descriptions with gap analysis
- **Review** with 7 AI personas (ATS bot, recruiter, hiring manager, HR screener, technical reviewer, engineer peer, sales strategist)
- **Verify** every claim traces back to source — catches fabricated metrics, technologies, and embellishments
- **Cover letters** — generate tailored cover letters with claim verification
- **Apply** — fire-and-forget end-to-end pipeline: research → match → qualify → tailor → score → review → cover-letter → verify in one shot. Optimized for multi-job-same-company use.
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

- Skills are available as `/resume-builder:setup`, `/resume-builder:import`, `/resume-builder:generate`, `/resume-builder:tailor`, `/resume-builder:score`, `/resume-builder:match`, `/resume-builder:review`, `/resume-builder:verify`, `/resume-builder:ingest`, `/resume-builder:research`, `/resume-builder:qualify`, `/resume-builder:cover-letter`, `/resume-builder:apply`
- Agents appear in `/agents` (e.g., `resume-builder:ats-bot`, `resume-builder:hiring-manager`, `resume-builder:cover-letter-reviewer`)
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

- Skills are available as `/setup`, `/import`, `/generate`, `/tailor`, `/score`, `/match`, `/review`, `/ingest`, `/verify`, `/research`, `/qualify`, `/cover-letter`, `/apply`
- Agents appear in `/agent` (e.g., `ats-bot`, `hiring-manager`, `engineer-peer`, `cover-letter-reviewer`)
- MCP tools (`generate`, `verify`, `verify_against_generated`) are exposed automatically

> **Note:** Codex CLI does not support per-project plugin scoping. Installed plugins are always global. If you need project-level control, use Claude Code's local scope install instead.

> **Note:** `/setup` writes plugin documentation to `CLAUDE.md`. If Codex CLI does not auto-load `CLAUDE.md`, you may need to manually copy or rename it to `AGENTS.md`.

### CLI Only (limited)

The CLI provides `resume-builder generate` and `resume-builder verify` without requiring an LLM. However, the full feature set — tailoring, scoring, matching, multi-persona review, and ingestion — requires Claude Code or Codex CLI skills.

**Install from GitHub (Latest Release):**
```bash
uv tool install git+https://github.com/wilsonkichoi/resume-builder
```

**Or, install locally in editable mode (For Development):**
```bash
uv tool install -e /path/to/resume-builder
```

This installs the package into an isolated environment at `~/.local/share/uv/tools/resume-builder/` and symlinks the `resume-builder` executable into `~/.local/bin/`. No clone or virtual environment management needed.

**Or, run directly without installing (For Testing):**
*(Note: Use `--no-cache` to ensure `uvx` picks up your latest local code edits instead of running a cached build)*
```bash
uvx --no-cache --from /path/to/resume-builder resume-builder generate
```

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

### 1. Set up your resume project

Open Claude Code in your resume project directory and run:

```
/resume-builder:setup
```

This creates the project structure and writes plugin documentation so the AI has full context in every future session:

```
your-resume-project/
  resume.yaml                        # Source of truth (scaffold)
  knowledge/
    corrections.yaml                 # Fabrication error log
    sessions/                        # Session history
    companies/                       # Company research profiles
  artifacts/                         # Place project docs here for /ingest
  CLAUDE.md                          # Plugin docs (marker-delimited section)
```

After setup completes, **restart Claude Code** so it loads the updated docs.

### 2. Import your existing resume (if migrating)

```
/resume-builder:import ../path/to/old-resume/
```

Scans for existing resume files (PDF, DOCX, Markdown, YAML), interviews you to fill gaps, and writes `resume.yaml`. Skip this step if building from scratch — edit `resume.yaml` directly.

### 3. Generate outputs

```
/resume-builder:generate
```

Generates `resume.md`, `resume.pdf`, `resume.docx`, and `index.html` from `resume.yaml`.

### 4. Add achievements from a project

```
/resume-builder:ingest ~/src/my-project
```

Analyzes source code, READMEs, infrastructure-as-code, and git history. Extracts verifiable facts, drafts resume bullets with provenance, and asks for your confirmation before updating `resume.yaml`.

### 5. Tailor for a job description

```
/resume-builder:tailor
```

Paste a job description. The skill reorders, emphasizes, and trims your resume for the target role while enforcing anti-fabrication rules. (Runs `/match`, `/verify`, and `/score` internally. For sharper results, run `/research` first.)

### 6. Score your resume

```
/resume-builder:score
```

Scores against ATS (8 components) and HR (6 dimensions) rubrics with actionable improvement suggestions.

### 7. Match against a job description

```
/resume-builder:match
```

Identifies skill matches, gaps, and suggests how to position existing experience.

### 8. Research a company

```
/resume-builder:research Acme Corp https://acme.com/careers/backend-engineer
```

Builds a CompanyProfile from user-provided links and supplementary web research. Captures company basics, products, pain points, tech stack, culture signals, growth signals, and key people — with every fact traced to its source. Profiles persist in `knowledge/companies/` for reuse across skills. (Feeds into `/tailor`, `/qualify`, `/review`, and `/cover-letter` for better results.)

### 9. Qualify an opportunity

```
/resume-builder:qualify Acme Corp
```

Flips the match lens: instead of "do I meet their bar?", assesses "how much do they need me?" (Sharper with a CompanyProfile from `/research`.) Scores across 6 dimensions:

| Dimension | Weight | Question |
|-----------|--------|----------|
| Pain-Solution Match | 25% | Do my skills address their pain points? |
| Value Density | 20% | How many needs can I *uniquely* address? |
| Growth Alignment | 15% | Am I growing where they're heading? |
| Culture Fit | 15% | Do they fit me? (bidirectional) |
| Leverage Position | 15% | Am I entering from strength or weakness? |
| ROI Potential | 10% | Can I articulate quantifiable value? |

Produces a strategic brief with positioning recommendations or reasons to pass.

### 10. Multi-persona review

```
/resume-builder:review
```

Gets feedback from up to 7 AI personas. Automatically loads all available prior context (CompanyProfile, match/qualify/tailor/score sessions) so each persona gives informed feedback — e.g., the Technical Reviewer uses tailor decisions to distinguish intentional reframes from fabrication. Reviews the tailored resume when one exists. Sales Strategist activates when a CompanyProfile exists.

| Persona | Focus |
|---------|-------|
| ATS Bot | Keyword parsing, formatting compatibility |
| Recruiter | 6-second scan impression |
| Hiring Manager | Technical depth and relevance |
| HR Screener | Red flags, compliance, gaps |
| Technical Reviewer | Accuracy of technical claims |
| Engineer Peer | Overclaim detection (most valuable for staff+ level) |
| Sales Strategist | Selling solutions vs. features (activated when CompanyProfile exists) |

### 11. Verify anti-fabrication

```
/resume-builder:verify
```

Checks:
- All bullets have verified provenance
- Tailored output matches source claims (fuzzy matching with severity levels)
- No previously corrected errors are reintroduced
- No fabricated technologies or metrics

### 12. Full application pipeline

```
/resume-builder:apply Acme Corp jd.txt https://acme.com/about
```

Fire-and-forget: runs the full pipeline (research → match → qualify → tailor → score → review → cover-letter → verify) in one shot. Produces all deliverables in `tailored/{date}_{company}_{role}/`. Reuses existing CompanyProfile when applying to multiple roles at the same company.

**Not sure which skills to run?** See [Workflows](#workflows) for scenario-based guides.

## Workflows

For a full description of each skill, see [Quick Start](#quick-start).

### Pick Your Workflow

| Scenario | When to Use | Skills | Time |
|----------|------------|--------|------|
| [First-Time Setup](#1-first-time-setup) | Just installed, no resume.yaml | setup, import, generate | 15-30 min |
| [Quick Apply](#2-quick-apply) | Have resume, need to tailor fast | tailor | 5-10 min |
| [Full Application](#3-full-application) | Complete pipeline, fire-and-forget | apply | 30-60 min |
| [Dream Job Deep-Dive](#4-dream-job-deep-dive) | High-value opportunity, full prep | research, qualify, tailor, review, cover-letter | 30-60 min |
| [Resume Maintenance](#5-resume-maintenance) | Finished a project, capture achievements | ingest, generate | 10-20 min |
| [Pre-Interview Prep](#6-pre-interview-prep) | Got an interview, need company intel | research, qualify, review | 15-30 min |
| [Opportunity Evaluation](#7-opportunity-evaluation) | Deciding whether to apply | match, qualify | 10-20 min |

### How Skills Connect

```
setup ──→ project structure + plugin docs
import ──→ resume.yaml ──→ generate (outputs)
               │
               ├──→ ingest ──→ verify (auto)
               │
               ├──→ research ──→ CompanyProfile ─┬─→ qualify
               │                                 ├─→ tailor ──→ verify (auto) ──→ score
               │                                 ├─→ review (enables sales-strategist)
               │                                 └─→ cover-letter
               │
               ├──→ match (called internally by tailor, cover-letter, qualify)
               │
               ├──→ apply (runs: research → match → qualify → tailor → score → review → cover-letter → verify)
               │
               ├──→ score
               ├──→ review
               └──→ verify

Arrows show data flow, not required ordering.
"auto" means the skill runs it internally.
Skills work without optional inputs but produce better results with them.
/apply is the full pipeline — individual skills can still be run standalone.
```

### 1. First-Time Setup

**When**: You just installed the plugin and need to create `resume.yaml`.

| Step | Command | Required? | What it does |
|------|---------|-----------|-------------|
| 1 | `/resume-builder:setup` | Yes | Creates project structure, writes plugin docs for AI context |
| 2 | Restart Claude Code | Yes | So the AI loads the updated docs |
| 3 | `/resume-builder:import` | Yes | Scans existing resume files, interviews you, writes resume.yaml |
| 4 | `/resume-builder:generate` | Yes | Creates PDF, DOCX, HTML, Markdown outputs |
| 5 | `/resume-builder:review` | Optional | Baseline feedback before any tailoring |

**You'll have**: `resume.yaml`, generated outputs in 4 formats, `knowledge/` directory, full plugin docs for AI context.

**Next**: Add achievements with `/ingest` or jump to [Quick Apply](#2-quick-apply) when you find a posting.

**After plugin updates**: Re-run `/resume-builder:setup` to refresh the docs, then restart Claude Code.

### 2. Quick Apply

**When**: You have `resume.yaml` and a job posting. Want a tailored resume fast.

| Step | Command | Required? | What it does |
|------|---------|-----------|-------------|
| 1 | `/resume-builder:tailor` | Yes | Paste JD. Internally runs match, tailors, verifies, generates, scores, and does a quick persona check. |

One command. `/tailor` handles match analysis, anti-fabrication verification, output generation, before/after scoring, and a quick check from recruiter + hiring-manager personas.

**You'll have**: `tailored/{date}_{company}_{role}/` with resume.yaml and outputs (PDF, DOCX, HTML, MD), ATS + HR scores.

| Optional add-on | Command | Why |
|-----------------|---------|-----|
| Cover letter | `/resume-builder:cover-letter` | If the posting requests one. Runs match internally. |
| Full review | `/resume-builder:review` | Deeper 6-persona feedback beyond tailor's quick check. |

### 3. Full Application

**When**: You want the complete pipeline in one shot. Fire-and-forget — no prompts, no gates. Optimal for applying to multiple roles at the same company.

| Step | Command | Required? | What it does |
|------|---------|-----------|-------------|
| 1 | `/resume-builder:apply CompanyName jd.txt [URLs]` | Yes | Runs: research → match → qualify → tailor → score → review → cover-letter → verify |

One command. Produces everything: CompanyProfile, tailored resume (4 formats), ATS/HR scores, multi-persona review, cover letter, verification report.

**Multi-job optimization**: Run `/apply` again for a different role at the same company — it reuses the existing CompanyProfile and skips research.

```
/resume-builder:apply Acme jd_backend.txt https://acme.com/about    ← first run, does research
/resume-builder:apply Acme jd_frontend.txt                          ← reuses CompanyProfile
```

**You'll have**: `tailored/{date}_{company}_{role}/` with resume.yaml, PDF, DOCX, HTML, MD, cover_letter.md, plus scores and review in session logs.

### 4. Dream Job Deep-Dive

**When**: High-value opportunity worth 30-60 minutes of preparation. Prefer this over `/apply` when you want interactive control at each step — review research before qualifying, approve tailoring plan, iterate on cover letter.

| Step | Command | Required? | What it does |
|------|---------|-----------|-------------|
| 1 | `/resume-builder:research CompanyName [URLs]` | Yes | Builds CompanyProfile — pain points, tech stack, culture, key people. Provide job posting URL, company blog, etc. |
| 2 | `/resume-builder:qualify CompanyName` | Recommended | Scores opportunity across 6 strategic dimensions. Tells you how to position — or whether to pass. |
| 3 | `/resume-builder:tailor` | Yes | Tailors resume using CompanyProfile pain points for sharper results. |
| 4 | `/resume-builder:review` | Recommended | Full 7-persona review. Sales-strategist activates because CompanyProfile exists. |
| 5 | `/resume-builder:cover-letter` | Recommended | Cover letter with company-specific hooks from pain points and recent news. |

**Decision gate after step 2**: If qualify weighted average is below 5.0 ("consider passing"), the brief explains why. Save your time or address the gaps first.

**You'll have**: CompanyProfile, strategic qualification brief, tailored resume with outputs, 7-persona review, cover letter with claim verification.

### 5. Resume Maintenance

**When**: You finished a project or hit a milestone. Capture achievements while details are fresh.

| Step | Command | Required? | What it does |
|------|---------|-----------|-------------|
| 1 | `/resume-builder:ingest ~/src/my-project` | Yes | Analyzes source code, git history, READMEs. Proposes bullets with provenance. Runs verify after. |
| 2 | `/resume-builder:generate` | Yes | Regenerate outputs with new content. |

**You'll have**: Updated `resume.yaml` with verified bullets, fresh outputs.

**Tip**: Run this after every significant project, not just when job hunting. A resume with fresh, verified achievements is always ready.

### 6. Pre-Interview Prep

**When**: You already applied and got an interview. Need to understand the company and prepare talking points.

| Step | Command | Required? | What it does |
|------|---------|-----------|-------------|
| 1 | `/resume-builder:research CompanyName [URLs]` | Yes | Deep company intelligence — pain points, tech stack, culture, key people. |
| 2 | `/resume-builder:qualify CompanyName` | Recommended | Strategic brief with positioning angle, interview talking points, and discovery questions to ask them. |
| 3 | `/resume-builder:review` | Optional | 7-persona review with sales-strategist feedback on how you're selling yourself. |

**You'll have**: CompanyProfile, strategic brief with talking points, understanding of where you're strong vs. where to compensate.

**Key output**: The qualify brief produces interview talking points and discovery questions — questions you ask *them* to demonstrate buyer understanding.

### 7. Opportunity Evaluation

**When**: You see a posting and aren't sure if it's worth applying.

| Step | Command | Required? | What it does |
|------|---------|-----------|-------------|
| 1 | `/resume-builder:match` | Yes | Quick gap analysis — match percentage, missing skills, transferable experience. |
| 2 | `/resume-builder:research CompanyName` | Optional | Builds CompanyProfile for deeper evaluation. Can be lightweight (just the JD link). |
| 3 | `/resume-builder:qualify CompanyName` | Recommended | Strategic go/no-go recommendation across 6 dimensions. |

**Decision points**:
- After step 1: Match below 50%? Probably skip unless you have a referral.
- After step 3: Qualify below 5.0 = consider passing. Above 7.0 = proceed to [Dream Job Deep-Dive](#4-dream-job-deep-dive).

**Lightweight version**: Just `/match` alone for a 2-minute skills check. No research needed.

## Template Customization

Generated outputs use a built-in design by default. You can customize colors, fonts, margins, and layout by placing template files in a `templates/` directory next to `resume.yaml`.

### Quick Start

```bash
# 1. Export default templates as a starting point
resume-builder template-export

# 2. Edit the files in templates/ (only change what you want)
# 3. Generate — templates are auto-discovered
resume-builder generate

# Or specify explicitly
resume-builder generate --template-dir templates

# Validate before generating
resume-builder template-validate
```

### Template Files

| File | Format | What it controls |
|------|--------|-----------------|
| `templates/pdf_styles.yaml` | PDF | Colors, fonts, margins, page size, element styles |
| `templates/docx_styles.yaml` | DOCX | Same schema as PDF (font names auto-mapped) |
| `templates/resume.html.j2` | HTML | Full Jinja2 template replacement |
| `templates/style.css` | HTML | CSS custom property overrides for the built-in template |

### PDF/DOCX Style Schema

Both `pdf_styles.yaml` and `docx_styles.yaml` use the same schema. Override only what you want — everything else uses built-in defaults.

```yaml
colors:
  dark: "#1A1A2E"       # Name, company, role, body text
  accent: "#2E5090"     # Title, section headings, links, rules
  muted: "#555555"      # Dates, descriptions, contact info
  light_bg: "#F0F4F8"   # Skill category background
  rule: "#2E5090"       # Horizontal rules under section headings

page:
  size: letter           # "letter" or "a4"
  margins:               # inches
    top: 0.625
    bottom: 0.625
    left: 0.75
    right: 0.75

fonts:
  primary: Helvetica              # DOCX auto-maps Helvetica → Arial
  primary_bold: Helvetica-Bold
  primary_italic: Helvetica-Oblique
  primary_bold_italic: Helvetica-BoldOblique

styles:
  name:                  # Your name at the top
    font_size: 18        # points
    alignment: center    # left, center, right
  title:                 # Job title below name
    font_size: 11
  section:               # Section headings (SKILLS, EXPERIENCE, etc.)
    font_size: 11
  bullet:                # Resume bullet points
    font_size: 10
    left_indent: 18
    bullet_indent: 6
  # Also: contact, company, company_desc, role, role_desc, body,
  #        skill_label, skill_value, project_title, project_desc, education
```

**Color cascade**: Changing `colors.accent` automatically changes all styles that reference it (title, section headings, links, rules). Override `styles.title.text_color` to break the link for a specific element.

**Style entry fields**: `font_name`, `font_size`, `leading` (line height), `alignment`, `text_color`, `space_before`, `space_after`, `left_indent`, `bullet_indent`. All optional — omit to use defaults.

### HTML Template Reference

**CSS-only overrides** (`templates/style.css`) — override CSS custom properties:

```css
[data-theme="dark"] {
  --accent: #E53E3E;
  --accent-bright: #FC8181;
}
```

**Full template replacement** (`templates/resume.html.j2`) — your template receives:

| Variable | Type | Description |
|----------|------|-------------|
| `ir` | `ResumeIR` | All resume data (header, summary, skills, experience, projects, education) |
| `current_year` | `int` | For copyright footers |
| `parse_skill_items` | `callable` | Splits skill strings into individual pills |
| `custom_css` | `str \| None` | Contents of `style.css` if present |

### Examples

**Change just the accent color** (3 lines):
```yaml
# templates/pdf_styles.yaml
colors:
  accent: "#E53E3E"
```

**Use A4 page size**:
```yaml
# templates/pdf_styles.yaml
page:
  size: a4
```

### Creating Templates with AI Assistance

Template files are structured data (YAML, CSS, Jinja2) that LLMs handle well. Start from exported defaults (`resume-builder template-export`) and ask an AI to modify them:

- [Claude Design](https://www.anthropic.com/news/claude-design-anthropic-labs) — generate and iterate on HTML template designs with visual preview
- [Google Stitch](https://stitch.withgoogle.com/) — rapid HTML/CSS prototyping for the HTML template
- Anthropic's open-source skills for Claude Code:
  - [frontend-design](https://github.com/anthropics/skills/tree/main/skills/frontend-design) — HTML/CSS generation for `resume.html.j2`
  - [pdf](https://github.com/anthropics/skills/tree/main/skills/pdf) — ReportLab PDF layout for `pdf_styles.yaml` tuning
  - [docx](https://github.com/anthropics/skills/tree/main/skills/docx) — python-docx generation for `docx_styles.yaml` tuning

The schema validates your changes before rendering — no blind box.

## MCP Tools

The MCP server exposes tools that both Claude Code and Codex can call directly:

| Tool | Description |
|------|-------------|
| `generate` | Generate resume outputs from resume.yaml. Parameters: `resume_path`, `formats`, `output_dir`, `template_dir` |
| `verify` | Check provenance of all claims. Parameters: `resume_path` |
| `verify_against_generated` | Anti-fabrication diff check. Parameters: `resume_path`, `generated_path`, `corrections_path` |
| `export_templates` | Export default template files. Parameters: `output_dir`, `formats` |
| `validate_templates` | Validate template configuration. Parameters: `template_dir` |

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
  phone: "(555) 123-4567"  # optional
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
