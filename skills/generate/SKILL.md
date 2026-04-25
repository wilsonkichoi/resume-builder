---
name: generate
description: "Generate PDF, DOCX, HTML, and Markdown from resume.yaml. Use when: 'generate resume', 'build resume', 'create pdf', 'create docx', 'update html', 'rebuild outputs'."
---

# /generate — Generate Resume Outputs

## Purpose
Run the deterministic generation pipeline. No LLM content generation — pure parsing and rendering from resume.yaml.

## Process

1. Verify `resume.yaml` exists in the project
2. Run: `resume-builder generate --format pdf,docx,html,md --output-dir .`
3. Report which files were generated and their sizes
4. Run: `resume-builder verify` to confirm provenance integrity

## Options
- Generate all formats: `resume-builder generate`
- Specific format: `resume-builder generate --format pdf`
- Custom output directory: `resume-builder generate --output-dir ./output`

## Template Customization

Users can customize the appearance of generated outputs by placing files in a `templates/` directory next to `resume.yaml`:

- `templates/pdf_styles.yaml` — Override PDF colors, fonts, margins, and style properties
- `templates/docx_styles.yaml` — Override DOCX colors, fonts, margins, and style properties
- `templates/resume.html.j2` — Replace the entire HTML template
- `templates/style.css` — Override CSS custom properties for the HTML output

To get started: `resume-builder template-export`

When generating with templates: `resume-builder generate --template-dir templates`

Or just place a `templates/` directory next to `resume.yaml` — auto-discovered.

## Notes
- This command is fully deterministic — same input always produces same output
- No LLM involvement in the rendering pipeline
- If resume.yaml has been modified by /ingest or /tailor, regenerate to update all outputs
