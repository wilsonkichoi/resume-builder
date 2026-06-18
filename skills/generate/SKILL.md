---
name: generate
description: "Generate PDF, DOCX, HTML, and Markdown from wilson-resume.yml. Use when: 'generate resume', 'build resume', 'create pdf', 'create docx', 'update html', 'rebuild outputs'."
argument-hint: "[--format pdf|docx|html|md] [--output-dir path] [--template-dir path]"
---

# /generate — Generate Resume Outputs

## Purpose
Run the deterministic generation pipeline. No LLM content generation — pure parsing and rendering from wilson-resume.yml.

## Process

1. Verify `wilson-resume.yml` exists in the project
2. Run: `resume-builder generate --format pdf,docx,html,md --output-dir .`
3. Report which files were generated and their sizes
4. Run: `resume-builder verify` to confirm provenance integrity

## Default Output Features

- **HTML** (`wilson-resume.html`) — Portfolio-quality page with: dark/light theme toggle (localStorage), spotlight hover on cards, scroll reveal animations, hero parallax, ambient background glow, gradient text shimmer, card-based layouts with hover lift, timeline visualization, interactive skill pills, full mobile responsiveness, prefers-reduced-motion support. Built in, no configuration needed.
- **PDF** (`wilson-resume.pdf`) — Clean professional document. Customizable via `templates/pdf_styles.yaml`.
- **DOCX** (`wilson-resume.docx`) — Word document. Same style schema as PDF via `templates/docx_styles.yaml`.
- **Markdown** (`wilson-resume.md`) — GitHub-flavored markdown. No styling.

## Options
- Generate all formats: `resume-builder generate`
- Specific format: `resume-builder generate --format pdf`
- Custom output directory: `resume-builder generate --output-dir ./output`

## Template Customization

Users can customize the appearance of generated outputs by placing files in a `templates/` directory next to `wilson-resume.yml`:

- `templates/pdf_styles.yaml` — Override PDF colors, fonts, margins, and style properties
- `templates/docx_styles.yaml` — Override DOCX colors, fonts, margins, and style properties
- `templates/resume.html.j2` — Replace the entire HTML template
- `templates/style.css` — Override CSS custom properties for the HTML output

To get started: `resume-builder template-export`

When generating with templates: `resume-builder generate --template-dir templates`

Or just place a `templates/` directory next to `wilson-resume.yml` — auto-discovered.

## Notes
- This command is fully deterministic, same input always produces same output
- No LLM involvement in the rendering pipeline
- If the resume YAML has been modified by /ingest or /tailor, regenerate to update all outputs
- Output filenames are derived from the input file stem (e.g., wilson-resume.yml produces wilson-resume.pdf)
