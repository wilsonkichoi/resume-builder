"""Template discovery, loading, resolution, export, and validation."""

from __future__ import annotations

import shutil
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import yaml
from pydantic import ValidationError
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import ParagraphStyle

from resume_builder.models.template_config import TemplateConfig

# Which ColorConfig role each style uses by default.
_DEFAULT_COLOR_ROLES: dict[str, str] = {
    "name": "dark",
    "title": "accent",
    "contact": "muted",
    "section": "accent",
    "company": "dark",
    "company_desc": "muted",
    "role": "dark",
    "role_desc": "muted",
    "bullet": "dark",
    "body": "dark",
    "skill_label": "dark",
    "skill_value": "dark",
    "project_title": "dark",
    "project_desc": "dark",
    "education": "dark",
}

# Built-in defaults per style (font, size, leading, alignment, spacing, indents).
# These match the current hardcoded values in pdf_renderer.py.
_BUILTIN_STYLES: dict[str, dict[str, Any]] = {
    "name": dict(font="bold", fontSize=18, leading=22, alignment="center", spaceAfter=2),
    "title": dict(font="primary", fontSize=11, leading=14, alignment="center", spaceAfter=4),
    "contact": dict(font="primary", fontSize=9.5, leading=12, alignment="center", spaceAfter=6),
    "section": dict(font="bold", fontSize=11, leading=14, alignment="left", spaceBefore=10, spaceAfter=2),
    "company": dict(font="bold", fontSize=11, leading=14, alignment="left", spaceBefore=8, spaceAfter=1),
    "company_desc": dict(font="italic", fontSize=9.5, leading=12, alignment="left", spaceAfter=1),
    "role": dict(font="bold_italic", fontSize=10, leading=13, alignment="left", spaceBefore=5, spaceAfter=1),
    "role_desc": dict(font="italic", fontSize=9.5, leading=12, alignment="left", spaceAfter=2),
    "bullet": dict(font="primary", fontSize=10, leading=13, alignment="left", spaceBefore=2, spaceAfter=2, leftIndent=18, bulletIndent=6),
    "body": dict(font="primary", fontSize=10, leading=13, alignment="left", spaceBefore=2, spaceAfter=2),
    "skill_label": dict(font="bold", fontSize=9.5, leading=12, alignment="left"),
    "skill_value": dict(font="primary", fontSize=9.5, leading=12, alignment="left"),
    "project_title": dict(font="bold", fontSize=10, leading=13, alignment="left", spaceBefore=4, spaceAfter=1),
    "project_desc": dict(font="primary", fontSize=10, leading=13, alignment="left", spaceAfter=4),
    "education": dict(font="primary", fontSize=10, leading=13, alignment="left", spaceBefore=2),
}

_ALIGNMENT_MAP = {"left": TA_LEFT, "center": TA_CENTER, "right": TA_RIGHT}

_FONT_KEY_MAP = {
    "primary": "primary",
    "bold": "primary_bold",
    "italic": "primary_italic",
    "bold_italic": "primary_bold_italic",
}


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------

def discover_template_dir(
    template_dir: str | Path | None,
    resume_path: str | Path,
) -> Path | None:
    """Resolve the template directory.

    Priority: explicit argument > ``templates/`` next to *resume_path* > None.
    """
    if template_dir is not None:
        p = Path(template_dir)
        return p if p.is_dir() else None
    auto = Path(resume_path).parent / "templates"
    return auto if auto.is_dir() else None


def load_template_config(template_dir: Path | None, fmt: str) -> TemplateConfig:
    """Load ``{fmt}_styles.yaml`` from *template_dir* and validate.

    Returns default ``TemplateConfig`` when the file does not exist.
    """
    if template_dir is None:
        return TemplateConfig()
    path = template_dir / f"{fmt}_styles.yaml"
    if not path.exists():
        return TemplateConfig()
    raw = yaml.safe_load(path.read_text()) or {}
    return TemplateConfig.model_validate(raw)


def discover_html_template(
    template_dir: Path | None,
) -> tuple[Path | None, Path | None]:
    """Return ``(jinja2_template_path, css_override_path)``."""
    if template_dir is None:
        return None, None
    j2 = template_dir / "resume.html.j2"
    css = template_dir / "style.css"
    return (j2 if j2.exists() else None, css if css.exists() else None)


# ---------------------------------------------------------------------------
# Resolution  — TemplateConfig → renderer-ready objects
# ---------------------------------------------------------------------------

def resolve_colors(config: TemplateConfig) -> SimpleNamespace:
    """Build a namespace of ``HexColor`` objects for PDF rendering."""
    return SimpleNamespace(
        dark=HexColor(config.colors.dark),
        accent=HexColor(config.colors.accent),
        muted=HexColor(config.colors.muted),
        light_bg=HexColor(config.colors.light_bg),
        rule=HexColor(config.colors.rule),
    )


def _resolve_font_name(font_key: str, config: TemplateConfig) -> str:
    """Map a built-in font key like ``'bold'`` to the actual font name from config."""
    attr = _FONT_KEY_MAP.get(font_key, "primary")
    return getattr(config.fonts, attr)


def resolve_pdf_styles(config: TemplateConfig) -> dict[str, ParagraphStyle]:
    """Build a dict of ReportLab ``ParagraphStyle`` objects from *config*."""
    colors = resolve_colors(config)
    styles: dict[str, ParagraphStyle] = {}

    for name, builtin in _BUILTIN_STYLES.items():
        entry = getattr(config.styles, name)

        font_name = entry.font_name or _resolve_font_name(builtin["font"], config)
        font_size = entry.font_size if entry.font_size is not None else builtin["fontSize"]
        leading = entry.leading if entry.leading is not None else builtin["leading"]
        alignment_str = entry.alignment or builtin["alignment"]
        alignment = _ALIGNMENT_MAP[alignment_str]

        if entry.text_color:
            text_color = HexColor(entry.text_color)
        else:
            color_role = _DEFAULT_COLOR_ROLES[name]
            text_color = getattr(colors, color_role)

        kwargs: dict[str, Any] = dict(
            fontName=font_name,
            fontSize=font_size,
            leading=leading,
            alignment=alignment,
            textColor=text_color,
        )

        sb = entry.space_before if entry.space_before is not None else builtin.get("spaceBefore")
        if sb is not None:
            kwargs["spaceBefore"] = sb
        sa = entry.space_after if entry.space_after is not None else builtin.get("spaceAfter")
        if sa is not None:
            kwargs["spaceAfter"] = sa
        li = entry.left_indent if entry.left_indent is not None else builtin.get("leftIndent")
        if li is not None:
            kwargs["leftIndent"] = li
        bi = entry.bullet_indent if entry.bullet_indent is not None else builtin.get("bulletIndent")
        if bi is not None:
            kwargs["bulletIndent"] = bi

        styles[name] = ParagraphStyle(name.capitalize(), **kwargs)

    return styles


def resolve_page_size(config: TemplateConfig):
    """Return a ReportLab page-size tuple."""
    return letter if config.page.size == "letter" else A4


# ---------------------------------------------------------------------------
# DOCX helpers
# ---------------------------------------------------------------------------

# PDF Helvetica family → DOCX Arial family.  User-provided names pass through.
_DOCX_FONT_MAP: dict[str, str] = {
    "Helvetica": "Arial",
    "Helvetica-Bold": "Arial",
    "Helvetica-Oblique": "Arial",
    "Helvetica-BoldOblique": "Arial",
}

_DOCX_PAGE_SIZES: dict[str, tuple[int, int]] = {
    "letter": (12240, 15840),
    "a4": (11906, 16838),
}


def resolve_docx_font(font_name: str) -> str:
    """Map a PDF font name to a DOCX font name."""
    return _DOCX_FONT_MAP.get(font_name, font_name)


def resolve_docx_page(config: TemplateConfig) -> SimpleNamespace:
    """Return page dimensions and margins in twips."""
    w, h = _DOCX_PAGE_SIZES[config.page.size]
    m = config.page.margins
    return SimpleNamespace(
        width=w,
        height=h,
        top=int(m.top * 1440),
        bottom=int(m.bottom * 1440),
        left=int(m.left * 1440),
        right=int(m.right * 1440),
        text_width=w - int(m.left * 1440) - int(m.right * 1440),
    )


def resolve_docx_style(
    style_name: str,
    config: TemplateConfig,
) -> SimpleNamespace:
    """Resolve a single style to DOCX-ready values (half-points, hex strings)."""
    builtin = _BUILTIN_STYLES[style_name]
    entry = getattr(config.styles, style_name)

    font_name = entry.font_name or _resolve_font_name(builtin["font"], config)
    font_name = resolve_docx_font(font_name)
    font_size = entry.font_size if entry.font_size is not None else builtin["fontSize"]
    size_hp = int(font_size * 2)

    if entry.text_color:
        color_hex = entry.text_color
    else:
        color_role = _DEFAULT_COLOR_ROLES[style_name]
        color_hex = getattr(config.colors, color_role)

    is_bold = "bold" in builtin["font"]
    is_italic = "italic" in builtin["font"]

    return SimpleNamespace(
        font_name=font_name,
        size_hp=size_hp,
        color_hex=color_hex,
        is_bold=is_bold,
        is_italic=is_italic,
    )


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------

_PDF_STYLES_YAML = """\
# Resume Builder — PDF Style Template
# Override only what you want to change. Delete or comment out everything else.
# All sizes are in points. Colors are hex (#RRGGBB).

colors:
  dark: "#1A1A2E"       # Name, company, role, body text
  accent: "#2E5090"     # Title, section headings, links, rules
  muted: "#555555"      # Dates, descriptions, contact info
  light_bg: "#F0F4F8"   # Skill category background
  rule: "#2E5090"       # Horizontal rules under section headings

page:
  size: letter           # "letter" (8.5x11) or "a4" (210x297mm)
  margins:
    top: 0.625           # inches
    bottom: 0.625
    left: 0.75
    right: 0.75

fonts:
  primary: Helvetica
  primary_bold: Helvetica-Bold
  primary_italic: Helvetica-Oblique
  primary_bold_italic: Helvetica-BoldOblique

# styles:
#   name:
#     font_size: 18        # Your name at the top
#     alignment: center
#   title:
#     font_size: 11        # Job title below name
#   section:
#     font_size: 11        # Section headings (SKILLS, EXPERIENCE, etc.)
#   bullet:
#     font_size: 10        # Resume bullet points
#     left_indent: 18
#     bullet_indent: 6
"""

_DOCX_STYLES_YAML = """\
# Resume Builder — DOCX Style Template
# Same schema as pdf_styles.yaml. Sizes are in points (converted automatically).
# Font names: "Helvetica" maps to "Arial" in DOCX. Use any installed font name.

colors:
  dark: "#1A1A2E"
  accent: "#2E5090"
  muted: "#555555"
  light_bg: "#F0F4F8"
  rule: "#2E5090"

page:
  size: letter
  margins:
    top: 0.625            # inches (900 twips)
    bottom: 0.625
    left: 0.75            # inches (1080 twips)
    right: 0.75

fonts:
  primary: Helvetica      # Maps to Arial in DOCX
  primary_bold: Helvetica-Bold
  primary_italic: Helvetica-Oblique
  primary_bold_italic: Helvetica-BoldOblique

# styles:
#   name:
#     font_size: 18
#     alignment: center
#   section:
#     font_size: 11
"""

_CSS_SKELETON = """\
/* Resume Builder — CSS Custom Property Overrides
   Place this file at templates/style.css to override the built-in HTML theme.
   Only include the properties you want to change. */

/* Example: change the accent color */
/*
[data-theme="dark"] {
  --accent: #E53E3E;
  --accent-bright: #FC8181;
  --accent-glow: rgba(229, 62, 62, 0.3);
}

[data-theme="light"] {
  --accent: #DC2626;
  --accent-bright: #EF4444;
}
*/

/* See README.md "Template Customization" section for all available CSS properties. */
"""


def export_defaults(output_dir: str | Path, formats: list[str]) -> list[str]:
    """Write default template files to *output_dir*.  Returns list of created paths."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    created: list[str] = []

    if "pdf" in formats:
        p = out / "pdf_styles.yaml"
        p.write_text(_PDF_STYLES_YAML)
        created.append(str(p))

    if "docx" in formats:
        p = out / "docx_styles.yaml"
        p.write_text(_DOCX_STYLES_YAML)
        created.append(str(p))

    if "html" in formats:
        src = Path(__file__).parent / "renderers" / "templates" / "resume.html.j2"
        dst = out / "resume.html.j2"
        shutil.copy2(src, dst)
        created.append(str(dst))

    if "css" in formats:
        p = out / "style.css"
        p.write_text(_CSS_SKELETON)
        created.append(str(p))

    return created


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_templates(template_dir: str | Path) -> list[str]:
    """Validate template files in *template_dir*.  Returns list of error strings."""
    d = Path(template_dir)
    errors: list[str] = []

    if not d.is_dir():
        return [f"Template directory does not exist: {d}"]

    for fmt in ("pdf", "docx"):
        path = d / f"{fmt}_styles.yaml"
        if not path.exists():
            continue
        try:
            raw = yaml.safe_load(path.read_text())
            if raw is None:
                continue
            TemplateConfig.model_validate(raw)
        except yaml.YAMLError as e:
            errors.append(f"{path.name}: invalid YAML — {e}")
        except ValidationError as e:
            for err in e.errors():
                loc = " → ".join(str(x) for x in err["loc"])
                errors.append(f"{path.name}: {loc} — {err['msg']}")

    j2_path = d / "resume.html.j2"
    if j2_path.exists():
        try:
            from jinja2 import Environment

            env = Environment()
            env.parse(j2_path.read_text())
        except Exception as e:
            errors.append(f"resume.html.j2: template syntax error — {e}")

    return errors
