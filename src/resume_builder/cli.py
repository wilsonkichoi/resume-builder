from __future__ import annotations

import click
from rich.console import Console

from resume_builder.core import generate_outputs, verify_generated, verify_provenance
from resume_builder.verification.provenance import Severity

console = Console()


@click.group()
def main():
    """Resume Builder — single source of truth for all resume outputs."""


@main.command()
@click.option("--format", "formats", default="pdf,docx,html,md", help="Comma-separated output formats")
@click.option("--resume", "resume_path", default="resume.yaml", type=click.Path(exists=True), help="Path to resume.yaml")
@click.option("--output-dir", default=".", type=click.Path(), help="Output directory")
def generate(formats: str, resume_path: str, output_dir: str):
    """Generate resume outputs from resume.yaml."""
    console.print(f"[bold]Parsing[/bold] {resume_path}")
    fmt_list = [f.strip() for f in formats.split(",")]
    results = generate_outputs(resume_path, fmt_list, output_dir)
    for r in results:
        console.print(f"[green]✓[/green] Generated {r.path} ({r.size:,} bytes)")


@main.command()
@click.option("--resume", "resume_path", default="resume.yaml", type=click.Path(exists=True))
@click.option("--generated", "generated_path", default=None, type=click.Path(exists=True), help="Path to generated/tailored output to verify against source")
@click.option("--corrections", "corrections_path", default="knowledge/corrections.yaml", type=click.Path(), help="Path to corrections.yaml")
def verify(resume_path: str, generated_path: str | None, corrections_path: str):
    """Verify provenance of all claims in resume.yaml."""
    result = verify_provenance(resume_path)

    if result.unverified:
        console.print(f"[yellow]⚠[/yellow] {len(result.unverified)} unverified claim(s):")
        for item in result.unverified:
            console.print(f"  {item}")
    else:
        console.print(f"[green]✓[/green] All {result.total_bullets} bullets verified. {result.total_projects} projects verified.")

    if generated_path:
        report = verify_generated(resume_path, generated_path, corrections_path)

        console.print(f"\n[bold]Anti-fabrication check:[/bold] {generated_path}")
        for finding in report.findings:
            if finding.severity == Severity.ERROR:
                console.print(f"  [red]ERROR[/red] {finding.message}")
                if finding.generated_text:
                    console.print(f"    Generated: {finding.generated_text[:100]}")
                if finding.source_text:
                    console.print(f"    Source:    {finding.source_text[:100]}")
            elif finding.severity == Severity.WARNING:
                console.print(f"  [yellow]WARN [/yellow] {finding.message} (similarity: {finding.similarity:.0%})")
            else:
                console.print(f"  [dim]INFO [/dim] {finding.message} (similarity: {finding.similarity:.0%})")

        console.print(f"\n  {len(report.errors)} error(s), {len(report.warnings)} warning(s), {len(report.infos)} info(s)")

        if not report.passed:
            raise SystemExit(1)
