from __future__ import annotations

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)

from resume_builder.models.resume import Bullet, ResumeIR

# ── Colors ────────────────────────────────────────────────────────────
DARK = HexColor("#1A1A2E")
ACCENT = HexColor("#2E5090")
MUTED = HexColor("#555555")
LIGHT_BG = HexColor("#F0F4F8")
RULE_COLOR = HexColor("#2E5090")

# ── Styles ────────────────────────────────────────────────────────────
STYLES = {
    "name": ParagraphStyle(
        "Name",
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        alignment=TA_CENTER,
        textColor=DARK,
        spaceAfter=2,
    ),
    "title": ParagraphStyle(
        "Title",
        fontName="Helvetica",
        fontSize=11,
        leading=14,
        alignment=TA_CENTER,
        textColor=ACCENT,
        spaceAfter=4,
    ),
    "contact": ParagraphStyle(
        "Contact",
        fontName="Helvetica",
        fontSize=9.5,
        leading=12,
        alignment=TA_CENTER,
        textColor=MUTED,
        spaceAfter=6,
    ),
    "section": ParagraphStyle(
        "Section",
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=ACCENT,
        spaceBefore=10,
        spaceAfter=2,
    ),
    "company": ParagraphStyle(
        "Company",
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=DARK,
        spaceBefore=8,
        spaceAfter=1,
    ),
    "company_desc": ParagraphStyle(
        "CompanyDesc",
        fontName="Helvetica-Oblique",
        fontSize=9.5,
        leading=12,
        textColor=MUTED,
        spaceAfter=1,
    ),
    "role": ParagraphStyle(
        "Role",
        fontName="Helvetica-BoldOblique",
        fontSize=10,
        leading=13,
        textColor=DARK,
        spaceBefore=5,
        spaceAfter=1,
    ),
    "role_desc": ParagraphStyle(
        "RoleDesc",
        fontName="Helvetica-Oblique",
        fontSize=9.5,
        leading=12,
        textColor=MUTED,
        spaceAfter=2,
    ),
    "bullet": ParagraphStyle(
        "Bullet",
        fontName="Helvetica",
        fontSize=10,
        leading=13,
        textColor=DARK,
        leftIndent=18,
        bulletIndent=6,
        spaceBefore=2,
        spaceAfter=2,
    ),
    "body": ParagraphStyle(
        "Body",
        fontName="Helvetica",
        fontSize=10,
        leading=13,
        textColor=DARK,
        spaceBefore=2,
        spaceAfter=2,
    ),
    "skill_label": ParagraphStyle(
        "SkillLabel",
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=12,
        textColor=DARK,
    ),
    "skill_value": ParagraphStyle(
        "SkillValue",
        fontName="Helvetica",
        fontSize=9.5,
        leading=12,
        textColor=DARK,
    ),
    "project_title": ParagraphStyle(
        "ProjectTitle",
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=DARK,
        spaceBefore=4,
        spaceAfter=1,
    ),
    "project_desc": ParagraphStyle(
        "ProjectDesc",
        fontName="Helvetica",
        fontSize=10,
        leading=13,
        textColor=DARK,
        spaceAfter=4,
    ),
    "education": ParagraphStyle(
        "Education",
        fontName="Helvetica",
        fontSize=10,
        leading=13,
        textColor=DARK,
        spaceBefore=2,
    ),
}

# ── Internal paragraph helpers ────────────────────────────────────────

_DATE_RIGHT = ParagraphStyle(
    "DateRight",
    fontName="Helvetica",
    fontSize=10,
    leading=13,
    textColor=MUTED,
    alignment=2,  # TA_RIGHT
)

_ROLE_DATE_RIGHT = ParagraphStyle(
    "RoleDateRight",
    fontName="Helvetica-Oblique",
    fontSize=10,
    leading=13,
    textColor=MUTED,
    alignment=2,
)

_ZERO_PAD_TABLE_STYLE = TableStyle([
    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
    ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ("TOPPADDING", (0, 0), (-1, -1), 0),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
])


def _link(text: str) -> str:
    """Colored link text (visually distinct, not clickable)."""
    return f'<font color="#2E5090">{text}</font>'


def _b(text: str) -> str:
    return f"<b>{text}</b>"


def _section_heading(text: str) -> list:
    return [
        Spacer(1, 4),
        Paragraph(text.upper(), STYLES["section"]),
        HRFlowable(
            width="100%",
            thickness=1.5,
            color=RULE_COLOR,
            spaceBefore=0,
            spaceAfter=4,
        ),
    ]


def _company_header(
    name: str,
    location: str,
    description: str | None = None,
    dates: str | None = None,
) -> list:
    elements: list = []
    left = Paragraph(f"<b>{name}</b>  |  {location}", STYLES["company"])
    right = (
        Paragraph(f"<font color='#555555'>{dates}</font>", _DATE_RIGHT)
        if dates
        else Paragraph("", STYLES["body"])
    )
    t = Table([[left, right]], colWidths=[4.5 * inch, 2.5 * inch])
    t.setStyle(_ZERO_PAD_TABLE_STYLE)
    elements.append(t)
    if description:
        elements.append(Paragraph(description, STYLES["company_desc"]))
    return elements


def _role_header(title: str, dates: str | None = None) -> list:
    left = Paragraph(title, STYLES["role"])
    right = (
        Paragraph(dates, _ROLE_DATE_RIGHT)
        if dates
        else Paragraph("", STYLES["role"])
    )
    t = Table([[left, right]], colWidths=[5.0 * inch, 2.0 * inch])
    t.setStyle(_ZERO_PAD_TABLE_STYLE)
    return [t]


def _role_desc(text: str) -> list:
    return [Paragraph(text, STYLES["role_desc"])]


def _bullet(text: str) -> Paragraph:
    return Paragraph(text, STYLES["bullet"], bulletText="•")


def _format_bullet(bullet: Bullet) -> str:
    """Build the rich-text string for a single bullet from the IR model."""
    if bullet.label:
        return f"{_b(bullet.label + ':')} {bullet.text}"
    return bullet.text


def _skills_table(rows: list[tuple[str, str]]) -> Table:
    table_data = []
    for label, value in rows:
        table_data.append([
            Paragraph(label, STYLES["skill_label"]),
            Paragraph(value, STYLES["skill_value"]),
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
        style_cmds.append(("BACKGROUND", (0, i), (0, i), LIGHT_BG))
    t.setStyle(TableStyle(style_cmds))
    return t


# ── Public API ────────────────────────────────────────────────────────


def render_pdf(ir: ResumeIR, output_path: str) -> None:
    """Render a ResumeIR model to a styled PDF at *output_path*."""
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
    )

    story: list = []

    # ── Header ────────────────────────────────────────────────────────
    story.append(Paragraph(ir.header.name, STYLES["name"]))
    story.append(Paragraph(ir.header.title, STYLES["title"]))
    story.append(Paragraph(
        f"{ir.header.location} &nbsp;|&nbsp; {ir.header.email} &nbsp;|&nbsp; "
        f"{_link(ir.header.linkedin)} &nbsp;|&nbsp; "
        f"{_link(ir.header.github)}",
        STYLES["contact"],
    ))

    # ── Professional Summary ──────────────────────────────────────────
    story.extend(_section_heading("Professional Summary"))
    story.append(Paragraph(ir.summary.paragraph, STYLES["body"]))
    for sb in ir.summary.bullets:
        story.append(_bullet(f"{_b(sb.label + ':')} {sb.text}"))

    # ── Skills ────────────────────────────────────────────────────────
    story.extend(_section_heading("Skills"))
    story.append(_skills_table([
        (skill.category, skill.items) for skill in ir.skills
    ]))

    # ── Professional Experience ───────────────────────────────────────
    story.extend(_section_heading("Professional Experience"))
    for company in ir.experience:
        story.extend(_company_header(
            name=company.company,
            location=company.location,
            description=company.description,
            dates=company.dates,
        ))
        for role in company.roles:
            story.extend(_role_header(role.title, role.dates))
            if role.description:
                story.extend(_role_desc(role.description))
            for bullet in role.bullets:
                story.append(_bullet(_format_bullet(bullet)))

    # ── Personal Projects ─────────────────────────────────────────────
    story.extend(_section_heading("Personal Projects"))
    for project in ir.projects:
        url_display = project.url.removeprefix("https://")
        story.append(Paragraph(
            f"{_b(project.name)} — {_link(url_display)}",
            STYLES["project_title"],
        ))
        story.append(Paragraph(project.description, STYLES["project_desc"]))

    # ── Education ─────────────────────────────────────────────────────
    story.extend(_section_heading("Education"))
    story.append(Paragraph(
        f"{_b(ir.education.degree)} | {ir.education.institution}",
        STYLES["education"],
    ))

    doc.build(story)
