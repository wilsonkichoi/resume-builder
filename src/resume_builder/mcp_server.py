from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from resume_builder.core import generate_outputs, verify_generated, verify_provenance

mcp = FastMCP(
    "resume-builder",
    instructions="Resume generation, verification, and anti-fabrication tools. All paths are relative to the user's project directory.",
)


@mcp.tool()
def generate(
    resume_path: str = "resume.yaml",
    formats: str = "pdf,docx,html,md",
    output_dir: str = ".",
) -> str:
    """Generate resume outputs (pdf, docx, html, md) from resume.yaml."""
    fmt_list = [f.strip() for f in formats.split(",")]
    results = generate_outputs(resume_path, fmt_list, output_dir)
    lines = [f"{r.format}: {r.path} ({r.size:,} bytes)" for r in results]
    return f"Generated {len(results)} file(s):\n" + "\n".join(lines)


@mcp.tool()
def verify(
    resume_path: str = "resume.yaml",
) -> str:
    """Verify provenance of all claims in resume.yaml. Checks that every bullet and project has verified: true."""
    result = verify_provenance(resume_path)
    if result.unverified:
        items = "\n".join(f"  - {u}" for u in result.unverified)
        return f"{len(result.unverified)} unverified claim(s):\n{items}"
    return f"All {result.total_bullets} bullets verified. {result.total_projects} projects verified."


@mcp.tool()
def verify_against_generated(
    resume_path: str = "resume.yaml",
    generated_path: str = "resume.md",
    corrections_path: str = "knowledge/corrections.yaml",
) -> str:
    """Anti-fabrication check: compare a generated/tailored resume against the source resume.yaml. Detects fabricated claims, altered metrics, and reintroduced corrections."""
    report = verify_generated(resume_path, generated_path, corrections_path)

    lines = []
    for finding in report.findings:
        prefix = finding.severity.value.ljust(5)
        line = f"{prefix} {finding.message}"
        if finding.similarity:
            line += f" (similarity: {finding.similarity:.0%})"
        lines.append(line)

    summary = f"{len(report.errors)} error(s), {len(report.warnings)} warning(s), {len(report.infos)} info(s)"
    status = "PASSED" if report.passed else "FAILED"

    return f"Anti-fabrication check: {status}\n" + "\n".join(lines) + f"\n\n{summary}"


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
