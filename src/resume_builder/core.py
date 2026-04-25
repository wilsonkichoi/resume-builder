from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from resume_builder.parser.resume_parser import parse_resume
from resume_builder.verification.provenance import (
    ClaimRegistry,
    VerificationReport,
    extract_bullets_from_markdown,
    load_corrections,
    verify_generated_text,
)


@dataclass
class GenerateResult:
    format: str
    path: str
    size: int


def generate_outputs(
    resume_path: str | Path,
    formats: list[str],
    output_dir: str | Path = ".",
    template_dir: str | Path | None = None,
) -> list[GenerateResult]:
    resume_path = Path(resume_path)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    from resume_builder.templates import (
        discover_html_template,
        discover_template_dir,
        load_template_config,
    )

    resolved_dir = discover_template_dir(template_dir, resume_path)

    ir = parse_resume(resume_path)
    results: list[GenerateResult] = []

    for fmt in formats:
        if fmt == "md":
            from resume_builder.renderers.markdown_renderer import render_markdown
            out_path = output / "resume.md"
            out_path.write_text(render_markdown(ir))
        elif fmt == "pdf":
            from resume_builder.renderers.pdf_renderer import render_pdf
            out_path = output / "resume.pdf"
            config = load_template_config(resolved_dir, "pdf")
            render_pdf(ir, str(out_path), config=config)
        elif fmt == "docx":
            from resume_builder.renderers.docx_renderer import render_docx
            out_path = output / "resume.docx"
            config = load_template_config(resolved_dir, "docx")
            render_docx(ir, str(out_path), config=config)
        elif fmt == "html":
            from resume_builder.renderers.html_renderer import render_html
            out_path = output / "index.html"
            tmpl_path, css_path = discover_html_template(resolved_dir)
            out_path.write_text(render_html(ir, template_path=tmpl_path, css_path=css_path))
        else:
            continue
        results.append(GenerateResult(fmt, str(out_path), out_path.stat().st_size))

    return results


@dataclass
class ProvenanceResult:
    total_bullets: int
    total_projects: int
    unverified: list[str]
    passed: bool


def verify_provenance(resume_path: str | Path) -> ProvenanceResult:
    ir = parse_resume(resume_path)

    unverified = []
    for company in ir.experience:
        for role in company.roles:
            for bullet in role.bullets:
                if not bullet.provenance.verified:
                    unverified.append(f"{company.company} > {role.title} > {bullet.label}")

    for project in ir.projects:
        if not project.provenance.verified:
            unverified.append(f"Project: {project.name}")

    total_bullets = sum(
        len(bullet.text) > 0
        for company in ir.experience
        for role in company.roles
        for bullet in role.bullets
    )

    return ProvenanceResult(
        total_bullets=total_bullets,
        total_projects=len(ir.projects),
        unverified=unverified,
        passed=len(unverified) == 0,
    )


def verify_generated(
    resume_path: str | Path,
    generated_path: str | Path,
    corrections_path: str | Path = "knowledge/corrections.yaml",
) -> VerificationReport:
    ir = parse_resume(resume_path)
    registry = ClaimRegistry(ir)
    corrections = load_corrections(corrections_path)
    md_text = Path(generated_path).read_text()
    bullets = extract_bullets_from_markdown(md_text)
    return verify_generated_text(registry, bullets, corrections)
