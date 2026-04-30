from __future__ import annotations

from types import SimpleNamespace

from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)

from resume_builder.models.resume import Bullet, ResumeIR
from resume_builder.models.template_config import TemplateConfig
from resume_builder.templates import (
    resolve_colors,
    resolve_page_size,
    resolve_pdf_styles,
)


# ── Internal paragraph helpers ────────────────────────────────────────

def _link(text: str, accent_hex: str) -> str:
    """Colored link text (visually distinct, not clickable)."""
    return f'<font color="{accent_hex}">{text}</font>'


def _b(text: str) -> str:
    return f"<b>{text}</b>"


def _section_heading(text: str, styles: dict, colors: SimpleNamespace) -> list:
    return [
        Spacer(1, 4),
        Paragraph(text.upper(), styles["section"]),
        HRFlowable(
            width="100%",
            thickness=1.5,
            color=colors.rule,
            spaceBefore=0,
            spaceAfter=4,
        ),
    ]


def _company_header(
    name: str,
    location: str,
    styles: dict,
    muted_hex: str,
    description: str | None = None,
    dates: str | None = None,
) -> list:
    elements: list = []
    left = Paragraph(f"<b>{name}</b>  |  {location}", styles["company"])
    date_style = ParagraphStyle(
        "DateRight",
        fontName=styles["company"].fontName,
        fontSize=styles["body"].fontSize,
        leading=styles["body"].leading,
        textColor=styles["company_desc"].textColor,
        alignment=2,  # TA_RIGHT
    )
    right = (
        Paragraph(f'<font color="{muted_hex}">{dates}</font>', date_style)
        if dates
        else Paragraph("", styles["body"])
    )
    t = Table([[left, right]], colWidths=[4.5 * inch, 2.5 * inch])
    t.setStyle(_ZERO_PAD_TABLE_STYLE)
    elements.append(t)
    if description:
        elements.append(Paragraph(description, styles["company_desc"]))
    return elements


def _role_header(
    title: str,
    styles: dict,
    dates: str | None = None,
) -> list:
    role_date_style = ParagraphStyle(
        "RoleDateRight",
        fontName=styles["role"].fontName,
        fontSize=styles["role"].fontSize,
        leading=styles["role"].leading,
        textColor=styles["role_desc"].textColor,
        alignment=2,
    )
    left = Paragraph(title, styles["role"])
    right = (
        Paragraph(dates, role_date_style)
        if dates
        else Paragraph("", styles["role"])
    )
    t = Table([[left, right]], colWidths=[5.0 * inch, 2.0 * inch])
    t.setStyle(_ZERO_PAD_TABLE_STYLE)
    return [t]


def _role_desc(text: str, styles: dict) -> list:
    return [Paragraph(text, styles["role_desc"])]


def _bullet(text: str, styles: dict) -> Paragraph:
    return Paragraph(text, styles["bullet"], bulletText="•")


def _format_bullet(bullet: Bullet) -> str:
    if bullet.label:
        return f"{_b(bullet.label + ':')} {bullet.text}"
    return bullet.text


def _skills_table(
    rows: list[tuple[str, str]],
    styles: dict,
    colors: SimpleNamespace,
) -> Table:
    table_data = []
    for label, value in rows:
        table_data.append([
            Paragraph(label, styles["skill_label"]),
            Paragraph(value, styles["skill_value"]),
        ])
    col_widths = [1.55 * inch, 5.45 * inch]
    t = Table(table_data, colWidths=col_widths)
    style_cmds = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (0, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]
    for i in range(len(table_data)):
        style_cmds.append(("BACKGROUND", (0, i), (0, i), colors.light_bg))
    t.setStyle(TableStyle(style_cmds))
    return t


_ZERO_PAD_TABLE_STYLE = TableStyle([
    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
    ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ("TOPPADDING", (0, 0), (-1, -1), 0),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
])


# ── Public API ────────────────────────────────────────────────────────


def render_pdf(
    ir: ResumeIR,
    output_path: str,
    config: TemplateConfig | None = None,
) -> None:
    """Render a ResumeIR model to a styled PDF at *output_path*."""
    config = config or TemplateConfig()
    colors = resolve_colors(config)
    styles = resolve_pdf_styles(config)
    accent_hex = config.colors.accent
    muted_hex = config.colors.muted
    page_size = resolve_page_size(config)
    margins = config.page.margins

    doc = SimpleDocTemplate(
        output_path,
        pagesize=page_size,
        leftMargin=margins.left * inch,
        rightMargin=margins.right * inch,
        topMargin=margins.top * inch,
        bottomMargin=margins.bottom * inch,
    )

    story: list = []

    # ── Header ────────────────────────────────────────────────────────
    story.append(Paragraph(ir.header.name, styles["name"]))
    story.append(Paragraph(ir.header.title, styles["title"]))
    contact_parts = [ir.header.location]
    if ir.header.phone:
        contact_parts.append(ir.header.phone)
    contact_parts.append(ir.header.email)
    contact_text = " &nbsp;|&nbsp; ".join(contact_parts)
    contact_text += (
        f" &nbsp;|&nbsp; {_link(ir.header.linkedin, accent_hex)}"
        f" &nbsp;|&nbsp; {_link(ir.header.github, accent_hex)}"
    )
    story.append(Paragraph(contact_text, styles["contact"]))

    # ── Professional Summary ──────────────────────────────────────────
    story.extend(_section_heading("Professional Summary", styles, colors))
    story.append(Paragraph(ir.summary.paragraph, styles["body"]))
    for sb in ir.summary.bullets:
        story.append(_bullet(f"{_b(sb.label + ':')} {sb.text}", styles))

    # ── Skills ────────────────────────────────────────────────────────
    story.extend(_section_heading("Skills", styles, colors))
    story.append(_skills_table(
        [(skill.category, skill.items) for skill in ir.skills],
        styles,
        colors,
    ))

    # ── Professional Experience ───────────────────────────────────────
    story.extend(_section_heading("Professional Experience", styles, colors))
    for company in ir.experience:
        story.extend(_company_header(
            name=company.company,
            location=company.location,
            styles=styles,
            muted_hex=muted_hex,
            description=company.description,
            dates=company.dates,
        ))
        for role in company.roles:
            story.extend(_role_header(role.title, styles, role.dates))
            if role.description:
                story.extend(_role_desc(role.description, styles))
            for bul in role.bullets:
                story.append(_bullet(_format_bullet(bul), styles))

    # ── Personal Projects ─────────────────────────────────────────────
    story.extend(_section_heading("Personal Projects", styles, colors))
    for project in ir.projects:
        url_display = project.url.removeprefix("https://")
        story.append(Paragraph(
            f"{_b(project.name)} — {_link(url_display, accent_hex)}",
            styles["project_title"],
        ))
        story.append(Paragraph(project.description, styles["project_desc"]))

    # ── Education ─────────────────────────────────────────────────────
    story.extend(_section_heading("Education", styles, colors))
    story.append(Paragraph(
        f"{_b(ir.education.degree)} | {ir.education.institution}",
        styles["education"],
    ))

    doc.build(story)
