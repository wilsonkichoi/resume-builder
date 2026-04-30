---
name: import
description: "Import an existing resume into resume-builder format. Scans for existing resume files, interviews the user, then writes resume.yaml. Use when: 'import resume', 'migrate resume', 'convert resume'."
argument-hint: "[path to existing resume files or project documents]"
---

# /import — Import Existing Resume

## Purpose
Import an existing resume into `resume.yaml` format. Scans for existing documents, interviews the user to fill gaps, and writes the structured YAML. Assumes `/setup` has already run (project structure and CLAUDE.md docs exist).

## Process

### Phase 1 — Discovery

Scan the current directory and one level of subdirectories for existing resume artifacts. If the user provides an external path (e.g., `/import ../resume/`), scan that path as well.

**Resume files**: Scan for resume artifacts in any common format (YAML, markdown, PDF, DOCX, JSON, HTML). Prioritize `resume.yaml` if it already exists in resume-builder format.

**External documents** (when the user provides an external path):
- Read and understand any document format found (HTML exports, PDFs, markdown, text files, etc.)
- Skip asset/support directories that don't contain meaningful content
- Extract project names, technologies, architecture, metrics, and timelines

**Report findings to the user:**
```
Found in source directory:
  ✓ resume.md (8.8 KB) — markdown resume (will parse)
  ✓ projects/ (15 HTML exports) — project documentation (will parse)
  ✗ skills.yaml — NOT a plugin file (skill data goes in resume.yaml)
  ✗ generate_resume_pdf.py — NOT needed (replaced by /generate)
  ✗ index.html — NOT needed (replaced by /generate HTML output)
```

### Phase 2 — Parse Existing Resume

If an existing resume file is found:

1. **Read and parse it** — extract all structured data:
   - Header: name, title, location, email, phone (optional), LinkedIn, GitHub
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

If external documents are found:

1. **Read each document** — extract meaningful content, skipping boilerplate and asset directories.

2. **Categorize extracted content** per document:
   - Technologies and tech stack
   - Architecture patterns and design decisions
   - Scale/volume metrics
   - Timelines and delivery dates

3. **Present summary to the user:**
   ```
   Parsed from 15 project documents:
     ASR for IVR — UniMRCP, FreeSWITCH, Azure, 70-80k calls/month
     Call Recording Architecture — S3, Lambda, transcription pipeline
     SIP Trunking — Kamailio, FreeSWITCH, HA design
     ...
   
   Which of these projects should be included in your resume?
   ```

### Phase 3 — Interview

Ask clarification questions to fill gaps. Do NOT proceed until these are resolved:

**Always ask:**
- "Is any content in this resume outdated or no longer accurate?"
- "Are there any recent projects or roles not captured here?"
- "Which types of roles are you targeting?"

**Ask if missing:**
- Contact info gaps (email, phone, LinkedIn, GitHub)
- Date gaps in employment history
- Bullet points with no quantified impact — ask if metrics are available
- Projects with no URLs — ask if they're public

**Do NOT ask:**
- Questions answerable from the documents already scanned
- Obvious formatting preferences (the plugin handles this)
- Technical setup questions (the plugin handles this)
- Whether to keep legacy generation scripts (they're replaced by /generate)

### Phase 4 — Confirm Before Writing

Present the complete plan before writing:

```
Ready to import. Here's what I'll write:

  WRITE  resume.yaml  — 20 bullets, 4 projects, all provenance set to manual+verified
  
  Provenance: all bullets marked source:"manual", verified:true
  
  Proceed? [describe any changes you want first]
```

Wait for explicit user confirmation before writing.

### Phase 5 — Write and Verify

After user confirms:

1. **Write `resume.yaml`** with full provenance on every bullet:
   ```yaml
   provenance: { source: "manual", artifacts: [], verified: true }
   ```

2. **Run `resume-builder verify`** to validate the file

3. **Report results**:
   ```
   ✓ resume.yaml written — 20 bullets, 4 projects, all verified
   ✓ resume-builder verify passed
   
   Next steps:
     /generate   — generate all 4 formats (PDF, DOCX, HTML, Markdown)
                   HTML output is a portfolio-quality page with dark/light
                   theme, spotlight effects, animations, and responsive design
     /ingest     — add achievements from project artifacts in artifacts/
     /tailor     — tailor for a specific job description
   ```

## Resume.yaml Schema Reference

The generated resume.yaml must conform to this structure:

```yaml
header:
  name: str
  title: str
  location: str
  email: str
  phone: str | None  # optional
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

## Anti-Fabrication Rules (MANDATORY)
- NEVER fabricate or embellish content during import — copy what exists
- NEVER skip the interview phase — always ask the user to confirm before writing
- If the existing resume has content that looks wrong or inconsistent, flag it rather than silently copying
- Set ALL provenance to `source: "manual", verified: true` for content imported from user's existing resume
- If `resume.yaml` already has content, ask before overwriting
