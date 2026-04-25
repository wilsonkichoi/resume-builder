---
name: init
description: "Initialize resume-builder in a project. Scans for existing resume files and project documents, interviews the user, then creates resume.yaml and project structure. Use when: 'init', 'set up resume', 'initialize', 'migrate resume', 'import resume'."
---

# /init — Initialize Resume Builder

## Purpose
Bootstrap resume-builder in the current project directory. Handles both fresh starts and migration from existing resume projects. Scans for existing documents, interviews the user to fill gaps, and only writes files once confident in the data.

## Process

### Phase 1 — Discovery

Scan the current directory and one level of subdirectories for existing resume artifacts:

**Resume files** (prioritize in this order):
- `resume.yaml` — already in resume-builder format, validate and adopt
- `resume.md`, `resume.txt` — markdown/text resume to parse
- `resume.pdf` — extract text content
- `resume.docx`, `resume.doc` — extract text content
- `*.json` with resume-like keys (header, experience, education)

**Supporting documents:**
- `skills.yaml` — existing skill inventory
- `projects/` directory — project artifacts, architecture docs
- `*.html` — portfolio/resume HTML pages
- `generate_resume_*.py`, `generate_resume_*.js` — existing generation scripts
- `CLAUDE.md`, `AGENTS.md`, `GEMINI.md` — existing AI instructions
- `.github/workflows/` — existing CI/CD

**Report findings to the user:**
```
Found in current directory:
  ✓ resume.md (8.8 KB) — markdown resume
  ✓ skills.yaml (6.8 KB) — skill inventory
  ✓ projects/ (32 files) — project documentation
  ✓ generate_resume_pdf.py — existing PDF generator
  ✓ index.html (59 KB) — portfolio page
  ✗ resume.yaml — not found (will create)
  ✗ knowledge/ — not found (will create)
```

### Phase 2 — Parse Existing Resume

If an existing resume file is found:

1. **Read and parse it** — extract all structured data:
   - Header: name, title, location, email, LinkedIn, GitHub
   - Summary paragraph and highlight bullets
   - Skills by category
   - Experience: companies, roles, dates, bullet points
   - Projects: name, URL, description, technologies
   - Education

2. **Extract technologies and metrics** from each bullet:
   - Technologies: tools, frameworks, languages, services mentioned
   - Metrics: percentages, counts, scale figures, latency numbers

3. **Present the parsed structure** to the user for review:
   ```
   Parsed from resume.md:
     Header: Wilson K. Choi | Senior Software Engineer | ...
     Summary: 3 bullets
     Skills: 6 categories
     Experience: 3 companies, 6 roles, 20 bullets
     Projects: 4 entries
     Education: B.S. Computer Science, Cal Poly Pomona
   
   Does this look complete? Anything missing or incorrect?
   ```

### Phase 3 — Interview

Ask clarification questions to fill gaps. Do NOT proceed until these are resolved:

**Always ask:**
- "Is any content in this resume outdated or no longer accurate?"
- "Are there any recent projects or roles not captured here?"
- "Which types of roles are you targeting?" (to set up skills.yaml role tags)

**Ask if missing:**
- Contact info gaps (email, LinkedIn, GitHub)
- Date gaps in employment history
- Bullet points with no quantified impact — ask if metrics are available
- Projects with no URLs — ask if they're public

**Ask if migrating from existing project:**
- "Should I preserve your existing generation scripts (generate_resume_pdf.py, etc.) or will you use `resume-builder generate` instead?"
- "Your existing CLAUDE.md has instructions — should I merge them with resume-builder's instructions or replace?"

**Do NOT ask:**
- Questions answerable from the documents already scanned
- Obvious formatting preferences (the plugin handles this)
- Technical setup questions (the plugin handles this)

### Phase 4 — Confirm Before Writing

Present the complete plan before creating any files:

```
Ready to initialize. Here's what I'll create:

  CREATE  resume.yaml         — 20 bullets, 4 projects, all provenance set to manual+verified
  CREATE  knowledge/corrections.yaml  — empty corrections log
  CREATE  knowledge/sessions/         — session log directory
  SKIP    skills.yaml         — already exists, no changes needed
  SKIP    resume.md           — keeping existing file

  Provenance: all bullets marked source:"manual", verified:true
  
  Proceed? [describe any changes you want first]
```

Wait for explicit user confirmation before writing ANY files.

### Phase 5 — Write Files

After user confirms:

1. **Write `resume.yaml`** with full provenance on every bullet:
   ```yaml
   provenance: { source: "manual", artifacts: [], verified: true }
   ```

2. **Create `knowledge/` directory**:
   - `knowledge/corrections.yaml` — empty corrections log
   - `knowledge/sessions/` — directory for session logs

3. **Update `.gitignore`** if it exists — add `knowledge/sessions/*.yaml` (session logs are local, not committed)

4. **Run `resume-builder verify`** to validate the new file

5. **Report results**:
   ```
   ✓ resume.yaml created — 20 bullets, 4 projects, all verified
   ✓ knowledge/ directory initialized
   ✓ resume-builder verify passed
   
   Next steps:
     resume-builder generate --format md    — generate resume.md from resume.yaml
     /ingest <project-path>     — add achievements from project artifacts
     /tailor <job-description>  — tailor for a specific role
   ```

## Resume.yaml Schema Reference

The generated resume.yaml must conform to this structure:

```yaml
header:
  name: str
  title: str
  location: str
  email: str
  linkedin: str
  github: str

summary:
  paragraph: str
  bullets:
    - label: str
      text: str
      provenance: { source: str, artifacts: [], verified: bool }

skills:
  - category: str
    items: str  # comma-separated
    provenance: { source: str, artifacts: [], verified: bool }

experience:
  - company: str
    location: str
    description: str (optional)
    dates: str
    roles:
      - title: str
        dates: str
        description: str (optional)
        bullets:
          - label: str
            text: str
            technologies: [str]
            metrics: [str]
            provenance: { source: str, artifacts: [], verified: bool }

projects:
  - name: str
    url: str
    description: str
    technologies: [str]
    provenance: { source: str, artifacts: [], verified: bool }

education:
  degree: str
  institution: str
```

## Rules
- NEVER fabricate or embellish content during migration — copy what exists
- NEVER skip the interview phase — always ask the user to confirm before writing
- If the existing resume has content that looks wrong or inconsistent, flag it rather than silently copying
- Set ALL provenance to `source: "manual", verified: true` for content migrated from user's existing resume
- If `resume.yaml` already exists and is valid, ask before overwriting
