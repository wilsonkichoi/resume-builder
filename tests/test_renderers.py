import tempfile
from pathlib import Path

from resume_builder.models.template_config import TemplateConfig
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


# ---------------------------------------------------------------------------
# Template customization tests
# ---------------------------------------------------------------------------


def test_pdf_with_default_config():
    """Rendering with an explicit default TemplateConfig produces a valid PDF."""
    ir = parse_resume(FIXTURE)
    from resume_builder.renderers.pdf_renderer import render_pdf

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        render_pdf(ir, f.name, config=TemplateConfig())
        path = Path(f.name)
    assert path.exists()
    assert path.stat().st_size > 1000


def test_pdf_with_custom_colors():
    ir = parse_resume(FIXTURE)
    from resume_builder.renderers.pdf_renderer import render_pdf

    config = TemplateConfig.model_validate({"colors": {"accent": "#E53E3E"}})
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        render_pdf(ir, f.name, config=config)
        path = Path(f.name)
    assert path.exists()
    assert path.stat().st_size > 1000


def test_pdf_with_a4_page():
    ir = parse_resume(FIXTURE)
    from resume_builder.renderers.pdf_renderer import render_pdf

    config = TemplateConfig.model_validate({"page": {"size": "a4"}})
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        render_pdf(ir, f.name, config=config)
        path = Path(f.name)
    assert path.exists()
    assert path.stat().st_size > 1000


def test_docx_with_default_config():
    ir = parse_resume(FIXTURE)
    from resume_builder.renderers.docx_renderer import render_docx

    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
        render_docx(ir, f.name, config=TemplateConfig())
        path = Path(f.name)
    assert path.exists()
    assert path.stat().st_size > 5000


def test_docx_with_custom_colors():
    ir = parse_resume(FIXTURE)
    from resume_builder.renderers.docx_renderer import render_docx

    config = TemplateConfig.model_validate({"colors": {"accent": "#E53E3E"}})
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
        render_docx(ir, f.name, config=config)
        path = Path(f.name)
    assert path.exists()
    assert path.stat().st_size > 5000


def test_docx_with_a4_page():
    ir = parse_resume(FIXTURE)
    from resume_builder.renderers.docx_renderer import render_docx

    config = TemplateConfig.model_validate({"page": {"size": "a4"}})
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
        render_docx(ir, f.name, config=config)
        path = Path(f.name)
    assert path.exists()
    assert path.stat().st_size > 5000


def test_html_with_css_override():
    ir = parse_resume(FIXTURE)
    from resume_builder.renderers.html_renderer import render_html

    with tempfile.NamedTemporaryFile(suffix=".css", delete=False, mode="w") as f:
        f.write("[data-theme='dark'] { --accent: #E53E3E; }")
        css_path = Path(f.name)

    html = render_html(ir, css_path=css_path)
    assert "--accent: #E53E3E" in html
    assert "Jane Doe" in html


def test_html_with_custom_template(tmp_path):
    ir = parse_resume(FIXTURE)
    from resume_builder.renderers.html_renderer import render_html

    tmpl = tmp_path / "custom.html.j2"
    tmpl.write_text("<html><body>{{ ir.header.name }}</body></html>")

    html = render_html(ir, template_path=tmpl)
    assert "Jane Doe" in html
    assert "<body>" in html
