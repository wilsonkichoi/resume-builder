# Resume Builder — Developer Instructions

## What This Is
Reusable Claude Code plugin for resume management. Ships skills, agents, an MCP server, and a Python CLI (`resume-builder`). Contains no user data — all resume content lives in the target project.

## Development

### Setup
```bash
uv sync
uv run pytest tests/ -v
```

### Architecture
- `skills/` — Claude Code skills (SKILL.md files). These are the user-facing interface.
- `agents/` — Review persona definitions (.agent.md files). Invoked by `/review`.
- `src/resume_builder/` — Python package.
  - `core.py` — Shared logic used by both CLI and MCP server.
  - `cli.py` — `resume-builder generate` and `resume-builder verify` (Click CLI wrapper around core).
  - `mcp_server.py` — FastMCP server exposing tools via stdio (MCP wrapper around core).
  - `models/resume.py` — Pydantic IR with Provenance model.
  - `parser/` — YAML to ResumeIR.
  - `renderers/` — ResumeIR to md, pdf, docx, html.
  - `verification/provenance.py` — ClaimRegistry, diff checker, corrections integration.
  - `knowledge/` — SessionStore and AchievementStore (data layer, no files shipped).
- `.mcp.json` — MCP server config loaded by Claude Code when plugin is installed.
- `.claude-plugin/plugin.json` — Plugin manifest for distribution.
- `tests/` — 53 tests against `tests/fixtures/sample_resume.yaml`. Never test against real resume data.

### Key Constraints
- Anti-fabrication rules are highest priority. Skills and agents must never invent content.
- The CLI operates on CWD (the target project). All paths (`--resume`, `--corrections`, `--generated`) are relative to where the user runs it.
- `knowledge/` directory is created by `/init` in the target project, not shipped with the plugin.
- Tests use `tests/fixtures/sample_resume.yaml` — fake data only. Never commit real resume data to this repo.

### Adding a Skill
1. Create `skills/<name>/SKILL.md` with frontmatter (name, description).
2. Document the process, inputs, outputs, and anti-fabrication rules.
3. Skills are invoked as `/resume-builder:<name>` when installed as a plugin.

### Adding an Agent
1. Create `agents/<name>.agent.md`.
2. Wire it into `/review` skill if it's a review persona.

### Python Tooling
- `uv` for everything (never pip/conda).
- `uv run resume-builder generate` / `uv run resume-builder verify` to test CLI.
- `uv run resume-builder-mcp` to start MCP server (stdio).
- `uv run pytest tests/ -v` to run tests.
