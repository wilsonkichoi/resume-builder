# Resume Builder — Developer Instructions

## What This Is
Reusable Claude Code plugin for resume management. Ships skills, agents, an MCP server, and a Python CLI (`resume-builder`). Contains no user data — all resume content lives in the target project.

## Architecture
- `skills/` — Claude Code skills (SKILL.md files). User-facing interface.
- `agents/` — Review persona definitions (.agent.md files). Invoked by `/review`, `/tailor`, and `/cover-letter`.
- `src/resume_builder/` — Python package.
  - `core.py` — Shared logic used by both CLI and MCP server.
  - `cli.py` — Click CLI wrapper around core (`resume-builder generate`, `resume-builder verify`, `resume-builder template-export`, `resume-builder template-validate`).
  - `mcp_server.py` — FastMCP server exposing tools via stdio.
  - `templates.py` — Template discovery, loading, resolution, export, and validation.
  - `models/resume.py` — Pydantic IR with Provenance model.
  - `models/company.py` — CompanyProfile Pydantic model with SourcedFact traceability.
  - `models/template_config.py` — TemplateConfig Pydantic model for PDF/DOCX style customization.
  - `parser/` — YAML to ResumeIR.
  - `renderers/` — ResumeIR to md, pdf, docx, html. Accepts optional TemplateConfig for style customization.
  - `verification/provenance.py` — ClaimRegistry, diff checker, corrections integration.
  - `knowledge/` — SessionStore, AchievementStore, and CompanyStore (data layer, no files shipped).
- `.mcp.json` — MCP server config loaded by Claude Code when plugin is installed.
- `.claude-plugin/plugin.json` — Claude Code plugin manifest for distribution.
- `.claude-plugin/marketplace.json` — Claude Code marketplace manifest for plugin discovery.
- `.codex-plugin/plugin.json` — Codex CLI plugin manifest.
- `.codex-plugin/mcp.json` — Codex CLI MCP server config.
- `tests/` — Tests against `tests/fixtures/sample_resume.yaml`. Never test against real resume data.

## Setup
```bash
uv sync
uv run pytest tests/ -v
```

## Development Rules

### Anti-Fabrication Is Highest Priority
Every skill and agent must enforce anti-fabrication. This is not optional. If you add a skill that touches resume content, it MUST include an `## Anti-Fabrication Rules (MANDATORY)` section. If you add an agent that suggests rewrites, it MUST constrain rewrites to facts in resume.yaml.

### Version Bump Is Mandatory
Every change that adds, modifies, or removes user-facing functionality MUST include a version bump. Default to the smallest unit possible — patch unless there's a strong reason to go higher:
- **Patch** (0.1.0 → 0.1.1): The default. New skills, new agents, new models/stores, bug fixes, doc updates, refactors, test additions.
- **Minor** (0.1.1 → 0.2.0): Breaking changes to existing skill behavior, breaking changes to `knowledge/` schema that invalidate existing data, or breaking changes to CLI flags.
- **Major** (0.2.0 → 1.0.0): Breaking changes to the plugin API or CLI interface that require users to change how they invoke the tool.

Version MUST be updated in all three files and they MUST match:
1. `pyproject.toml` — `version = "X.Y.Z"`
2. `.claude-plugin/plugin.json` — `"version": "X.Y.Z"`
3. `.codex-plugin/plugin.json` — `"version": "X.Y.Z"`

### Documentation Updates Are Mandatory
When adding or modifying skills, agents, or Python modules, you MUST update ALL of the following:

1. **README.md** — Update the "What It Does" bullet list, Quick Start steps, persona tables, skill lists in installation sections, and the `knowledge/` directory listing if applicable.
2. **CLAUDE.md** (this file) — Update the Architecture section if new modules/files are added. Keep the test count accurate.
3. **plugin.json** — Update the `description` field if the change adds a new capability category.
4. **Cross-references in other skills** — If a new skill produces data consumed by other skills (e.g., `/research` produces CompanyProfile used by `/tailor`, `/cover-letter`, `/qualify`), update those consuming skills to reference the new data source.

Do not consider a feature complete until all documentation is updated.

### Skill Conventions
- File: `skills/<name>/SKILL.md`
- YAML frontmatter is required: `name`, `description` (with "Use when:" trigger phrases), `argument-hint`.
- Structure: `# /<name>` heading → `## Purpose` → `## Anti-Fabrication Rules (MANDATORY)` (if it touches resume content) → `## Process` with numbered `### Step N — Title` steps → `## Output` → `## Options`.
- Every skill that modifies or generates content from resume.yaml MUST run verification.
- Every skill that produces persistent output MUST log to `knowledge/sessions/` as the final step, with a YAML schema example in the SKILL.md.
- Skills that consume data from other skills (CompanyProfile, match sessions) should check for existing data before asking the user to provide it manually.

### Agent Conventions
- File: `agents/<name>.agent.md`
- YAML frontmatter is required: `name`, `description`.
- Structure: `# Name — Subtitle` → persona paragraph → `## Your Perspective` → `## Evaluation Criteria` (numbered, with 1-10 rubric scales) → `## Output Format` → `## Rules`.
- Every agent MUST produce: Strengths, Weaknesses, Score (1-10), and Action Items.
- Agents that suggest rewrites MUST constrain to facts in resume.yaml — they reframe truth, they don't invent it.
- When wiring a new agent into `/review`, update: the Personas list, the Step 2 agent definitions list, and the Step 3 summary table in `skills/review/SKILL.md`.

### Python Conventions
- `uv` for everything. Never pip, conda, or poetry.
- Data models in `models/` use Pydantic (`BaseModel`). Serialization via `model_dump()` / `model_validate()`.
- Knowledge stores in `knowledge/` use YAML persistence. Pattern: `__init__` creates directory, `save()` writes YAML, `load()` reads and validates.
- Tests go in `tests/` with fake data only. Use `tmp_path` fixture for file I/O tests. Never use real company names or real resume data.
- Run `uv run pytest tests/ -v` after every change. All tests must pass before a feature is considered complete.

### Test Requirements
- New Pydantic models MUST have serialization roundtrip tests.
- New knowledge stores MUST have CRUD tests (save, load, list, find, delete).
- New Python utility functions MUST have tests for edge cases (empty input, unicode, etc.).
- Skills and agents are Markdown files — they don't need Python tests, but they must follow the conventions above.

### Key Constraints
- The CLI and MCP server operate on CWD (the target project). All paths are relative to where the user runs it.
- `knowledge/` directory is created by `/init` in the target project, not shipped with the plugin.
- Skills and agents are the user-facing interface — Python code provides the deterministic pipeline (generation, verification, storage). LLM-dependent logic lives in skills, not Python.
- The generation pipeline (`core.py` → parsers → renderers) is fully deterministic. Same input = same output. No LLM in this path.

### CLI and MCP Commands
```bash
uv run resume-builder generate              # Generate outputs
uv run resume-builder generate --template-dir templates  # Generate with custom templates
uv run resume-builder verify                # Verify provenance
uv run resume-builder template-export       # Export default templates to templates/
uv run resume-builder template-validate     # Validate template files
uv run resume-builder-mcp                   # Start MCP server (stdio)
uv run pytest tests/ -v                     # Run tests
```
