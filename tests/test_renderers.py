import tempfile
from pathlib import Path

from resume_builder.parser.resume_parser import parse_resume
from resume_builder.renderers.markdown_renderer import render_markdown

FIXTURE = Path(__file__).parent / "fixtures" / "sample_resume.yaml"


def test_markdown_contains_name():
    ir = parse_resume(FIXTURE)
    md = render_markdown(ir)
    assert "Jane Doe" in md


def test_markdown_contains_all_sections():
    ir = parse_resume(FIXTURE)
    md = render_markdown(ir)
    assert "### Professional Summary" in md
    assert "### Skills" in md
    assert "### Professional Experience" in md
    assert "### Personal Projects" in md
    assert "### Education" in md


def test_markdown_contains_all_companies():
    ir = parse_resume(FIXTURE)
    md = render_markdown(ir)
    assert "Acme Corp" in md
    assert "StartupXYZ" in md


def test_markdown_contains_projects():
    ir = parse_resume(FIXTURE)
    md = render_markdown(ir)
    assert "OpenTracer" in md
    assert "KVStore" in md


def test_pdf_generates_file():
    ir = parse_resume(FIXTURE)
    from resume_builder.renderers.pdf_renderer import render_pdf

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        render_pdf(ir, f.name)
        path = Path(f.name)
    assert path.exists()
    assert path.stat().st_size > 1000


def test_docx_generates_file():
    ir = parse_resume(FIXTURE)
    from resume_builder.renderers.docx_renderer import render_docx

    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
        render_docx(ir, f.name)
        path = Path(f.name)
    assert path.exists()
    assert path.stat().st_size > 5000


def test_html_renders():
    ir = parse_resume(FIXTURE)
    from resume_builder.renderers.html_renderer import render_html

    html = render_html(ir)
    assert "Jane Doe" in html
    assert "data-theme" in html
    assert "tailwindcss" in html


def test_html_contains_all_sections():
    ir = parse_resume(FIXTURE)
    from resume_builder.renderers.html_renderer import render_html

    html = render_html(ir)
    assert "Professional Experience" in html
    assert "Skills" in html
    assert "Personal Projects" in html
    assert "Education" in html


def test_html_contains_experience():
    ir = parse_resume(FIXTURE)
    from resume_builder.renderers.html_renderer import render_html

    html = render_html(ir)
    assert "Acme Corp" in html
    assert "StartupXYZ" in html
    assert "OpenTracer" in html
