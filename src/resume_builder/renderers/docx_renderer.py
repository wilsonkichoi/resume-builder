"""DOCX renderer — produces a styled resume from a ResumeIR model.

Styling is ported from generate_resume_docx.js (docx npm library) to
python-docx equivalents: same fonts, colors, sizes, spacing, borders,
bullet formatting, and table layout.
"""

from __future__ import annotations

import re

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor, Twips
from docx.table import Table

from resume_builder.models.resume import ResumeIR

# ---------------------------------------------------------------------------
# Color palette (matches JS constants)
# ---------------------------------------------------------------------------
DARK = RGBColor(0x1A, 0x1A, 0x2E)
ACCENT = RGBColor(0x2E, 0x50, 0x90)
MUTED = RGBColor(0x55, 0x55, 0x55)
LIGHT_BG = "F0F4F8"
RULE_COLOR = "2E5090"

# JS sizes are in half-points; python-docx Pt() takes full points.
HP = 0.5  # multiply JS half-point value by HP to get Pt argument


# ---------------------------------------------------------------------------
# Low-level OxmlElement helpers
# ---------------------------------------------------------------------------

def _set_bottom_border(paragraph, color: str, size: int) -> None:
    """Add a bottom border to a paragraph via raw XML (python-docx has no
    direct paragraph-border API)."""
    pPr = paragraph._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), str(size))
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), color)
    pBdr.append(bottom)
    pPr.append(pBdr)


def _set_cell_shading(cell, fill: str) -> None:
    """Apply background shading to a table cell."""
    shading = OxmlElement("w:shd")
    shading.set(qn("w:fill"), fill)
    shading.set(qn("w:val"), "clear")
    cell._tc.get_or_add_tcPr().append(shading)


def _remove_cell_borders(cell) -> None:
    """Remove all borders from a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = OxmlElement("w:tcBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "none")
        el.set(qn("w:sz"), "0")
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), "auto")
        tcBorders.append(el)
    tcPr.append(tcBorders)


def _set_cell_margins(cell, top: int, bottom: int, left: int, right: int) -> None:
    """Set cell margins in twips via XML."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement("w:tcMar")
    for edge, val in [("top", top), ("bottom", bottom), ("start", left), ("end", right)]:
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:w"), str(val))
        el.set(qn("w:type"), "dxa")
        tcMar.append(el)
    tcPr.append(tcMar)


def _set_cell_width(cell, width: int) -> None:
    """Set explicit cell width in twips."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcW = OxmlElement("w:tcW")
    tcW.set(qn("w:w"), str(width))
    tcW.set(qn("w:type"), "dxa")
    tcPr.append(tcW)


def _add_tab_stop_right_max(paragraph) -> None:
    """Add a right-aligned tab stop at the right margin (TabStopPosition.MAX
    in docx-js = 9026 twips on letter with 1080 margins, i.e. full text
    width).  We compute: page_width - left_margin - right_margin =
    12240 - 1080 - 1080 = 10080 twips."""
    pPr = paragraph._p.get_or_add_pPr()
    tabs = OxmlElement("w:tabs")
    tab = OxmlElement("w:tab")
    tab.set(qn("w:val"), "right")
    tab.set(qn("w:pos"), "10080")
    tab.set(qn("w:leader"), "none")
    tabs.append(tab)
    pPr.append(tabs)


def _configure_bullet_numbering(doc: Document) -> str:
    """Register a bullet numbering definition in the document and return its
    abstractNumId.  python-docx does not expose numbering creation, so we
    manipulate the XML directly.

    Returns the numId (as string) to reference in paragraphs.
    """
    numbering_part = doc.part.numbering_part
    numbering_elm = numbering_part.numbering_definitions._numbering

    # Find the next available abstractNumId / numId
    existing_abstract = numbering_elm.findall(qn("w:abstractNum"))
    next_abstract_id = str(len(existing_abstract) + 100)  # offset to avoid conflicts

    existing_nums = numbering_elm.findall(qn("w:num"))
    next_num_id = str(len(existing_nums) + 100)

    # abstractNum
    abstract_num = OxmlElement("w:abstractNum")
    abstract_num.set(qn("w:abstractNumId"), next_abstract_id)
    multi = OxmlElement("w:multiLevelType")
    multi.set(qn("w:val"), "hybridMultilevel")
    abstract_num.append(multi)

    lvl = OxmlElement("w:lvl")
    lvl.set(qn("w:ilvl"), "0")
    start = OxmlElement("w:start")
    start.set(qn("w:val"), "1")
    lvl.append(start)
    numFmt = OxmlElement("w:numFmt")
    numFmt.set(qn("w:val"), "bullet")
    lvl.append(numFmt)
    lvlText = OxmlElement("w:lvlText")
    lvlText.set(qn("w:val"), "•")
    lvl.append(lvlText)
    lvlJc = OxmlElement("w:lvlJc")
    lvlJc.set(qn("w:val"), "left")
    lvl.append(lvlJc)
    # indent: left 540, hanging 270 (in twips / dxa)
    pPr = OxmlElement("w:pPr")
    ind = OxmlElement("w:ind")
    ind.set(qn("w:left"), "540")
    ind.set(qn("w:hanging"), "270")
    pPr.append(ind)
    lvl.append(pPr)
    # Bullet font
    rPr = OxmlElement("w:rPr")
    rFonts = OxmlElement("w:rFonts")
    rFonts.set(qn("w:ascii"), "Symbol")
    rFonts.set(qn("w:hAnsi"), "Symbol")
    rFonts.set(qn("w:hint"), "default")
    rPr.append(rFonts)
    lvl.append(rPr)

    abstract_num.append(lvl)
    numbering_elm.insert(0, abstract_num)

    # num referencing abstractNum
    num = OxmlElement("w:num")
    num.set(qn("w:numId"), next_num_id)
    abstractNumId_el = OxmlElement("w:abstractNumId")
    abstractNumId_el.set(qn("w:val"), next_abstract_id)
    num.append(abstractNumId_el)
    numbering_elm.append(num)

    return next_num_id


def _make_bullet_paragraph(paragraph, num_id: str) -> None:
    """Apply bullet numbering to an existing paragraph."""
    pPr = paragraph._p.get_or_add_pPr()
    numPr = OxmlElement("w:numPr")
    ilvl = OxmlElement("w:ilvl")
    ilvl.set(qn("w:val"), "0")
    numPr.append(ilvl)
    numId_el = OxmlElement("w:numId")
    numId_el.set(qn("w:val"), num_id)
    numPr.append(numId_el)
    pPr.append(numPr)


# ---------------------------------------------------------------------------
# Text-run helpers
# ---------------------------------------------------------------------------

def _plain_run(paragraph, text: str, size_hp: int = 20, color: RGBColor = None):
    """Add a plain text run. *size_hp* is in half-points (JS convention)."""
    run = paragraph.add_run(text)
    run.font.name = "Arial"
    run.font.size = Pt(size_hp * HP)
    if color:
        run.font.color.rgb = color
    return run


def _bold_run(paragraph, text: str, size_hp: int = 20, color: RGBColor = None):
    run = _plain_run(paragraph, text, size_hp, color)
    run.bold = True
    return run


def _italic_run(paragraph, text: str, size_hp: int = 20, color: RGBColor = None):
    run = _plain_run(paragraph, text, size_hp, color)
    run.italic = True
    return run


def _bold_italic_run(paragraph, text: str, size_hp: int = 20, color: RGBColor = None):
    run = _plain_run(paragraph, text, size_hp, color)
    run.bold = True
    run.italic = True
    return run


# ---------------------------------------------------------------------------
# Markdown-bold parser  (**bold** markers inside text)
# ---------------------------------------------------------------------------
_BOLD_RE = re.compile(r"(\*\*[^*]+\*\*)")


def _add_parsed_runs(paragraph, text: str, size_hp: int = 20, color: RGBColor = None):
    """Split *text* on ``**bold**`` markers and add runs accordingly."""
    parts = _BOLD_RE.split(text)
    for part in parts:
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            _bold_run(paragraph, part[2:-2], size_hp, color)
        else:
            _plain_run(paragraph, part, size_hp, color)


# ---------------------------------------------------------------------------
# Paragraph-level builders
# ---------------------------------------------------------------------------

def _set_spacing(paragraph, before: int | None = None, after: int | None = None):
    """Set paragraph spacing in twips."""
    fmt = paragraph.paragraph_format
    if before is not None:
        fmt.space_before = Twips(before)
    if after is not None:
        fmt.space_after = Twips(after)


def _add_section_heading(doc: Document, text: str) -> None:
    """SECTION HEADING — uppercased, bold, accent color, bottom border."""
    p = doc.add_paragraph()
    _set_spacing(p, before=280, after=80)
    _set_bottom_border(p, RULE_COLOR, 6)
    _bold_run(p, text.upper(), size_hp=22, color=ACCENT)


def _add_subheading(doc: Document, left: str, right: str | None = None) -> None:
    """Company / org name with optional right-aligned location."""
    p = doc.add_paragraph()
    _set_spacing(p, before=200, after=40)
    _bold_run(p, left, size_hp=22, color=DARK)
    if right:
        _add_tab_stop_right_max(p)
        _plain_run(p, f"\t{right}", size_hp=20, color=MUTED)


def _add_role_title(doc: Document, title: str, dates: str | None = None) -> None:
    """Role title — bold italic, with optional right-aligned dates."""
    p = doc.add_paragraph()
    _set_spacing(p, before=100, after=20)
    _bold_italic_run(p, title, size_hp=20, color=DARK)
    if dates:
        _add_tab_stop_right_max(p)
        r = _plain_run(p, f"\t{dates}", size_hp=20, color=MUTED)
        r.italic = True


def _add_role_description(doc: Document, text: str) -> None:
    """Italic description line below a role title."""
    p = doc.add_paragraph()
    _set_spacing(p, before=0, after=40)
    _italic_run(p, text, size_hp=19, color=MUTED)


def _add_bullet(doc: Document, text: str, num_id: str) -> None:
    """Bulleted paragraph with **bold** markers parsed from *text*."""
    p = doc.add_paragraph()
    _set_spacing(p, before=40, after=40)
    _make_bullet_paragraph(p, num_id)
    _add_parsed_runs(p, text, size_hp=20)


def _format_bullet_text(bullet) -> str:
    """Build the full bullet string from a Bullet model instance.

    If the bullet has a label, prepend it as ``**Label:** text``.
    """
    if bullet.label:
        return f"**{bullet.label}:** {bullet.text}"
    return bullet.text


# ---------------------------------------------------------------------------
# Skills table
# ---------------------------------------------------------------------------

def _add_skills_table(doc: Document, skills) -> None:
    """Two-column table: category label (shaded) | items."""
    table = doc.add_table(rows=len(skills), cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    # Column widths in twips — 2520 / 7560 (matching JS)
    for row_idx, skill in enumerate(skills):
        row = table.rows[row_idx]
        label_cell = row.cells[0]
        value_cell = row.cells[1]

        # --- Label cell ---
        _remove_cell_borders(label_cell)
        _set_cell_shading(label_cell, LIGHT_BG)
        _set_cell_margins(label_cell, top=40, bottom=40, left=80, right=80)
        _set_cell_width(label_cell, 2520)
        lp = label_cell.paragraphs[0]
        _set_spacing(lp, before=0, after=0)
        _bold_run(lp, skill.category, size_hp=19, color=DARK)

        # --- Value cell ---
        _remove_cell_borders(value_cell)
        _set_cell_margins(value_cell, top=40, bottom=40, left=80, right=80)
        _set_cell_width(value_cell, 7560)
        vp = value_cell.paragraphs[0]
        _set_spacing(vp, before=0, after=0)
        _plain_run(vp, skill.items, size_hp=19, color=DARK)

    # Set overall table width
    tbl = table._tbl
    tblPr = tbl.tblPr if tbl.tblPr is not None else OxmlElement("w:tblPr")
    tblW = OxmlElement("w:tblW")
    tblW.set(qn("w:w"), "10080")
    tblW.set(qn("w:type"), "dxa")
    # Remove any existing tblW
    for existing in tblPr.findall(qn("w:tblW")):
        tblPr.remove(existing)
    tblPr.append(tblW)

    # Remove table-level borders
    tblBorders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "none")
        el.set(qn("w:sz"), "0")
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), "auto")
        tblBorders.append(el)
    for existing in tblPr.findall(qn("w:tblBorders")):
        tblPr.remove(existing)
    tblPr.append(tblBorders)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def render_docx(ir: ResumeIR, output_path: str) -> None:
    """Render *ir* to a styled DOCX file at *output_path*."""
    doc = Document()

    # -- Default font for the document --
    style = doc.styles["Normal"]
    font = style.font
    font.name = "Arial"
    font.size = Pt(20 * HP)  # 10pt (20 half-points)

    # -- Page setup (Letter: 12240 x 15840 twips, margins 900/1080) --
    section = doc.sections[0]
    section.page_width = Twips(12240)
    section.page_height = Twips(15840)
    section.top_margin = Twips(900)
    section.bottom_margin = Twips(900)
    section.left_margin = Twips(1080)
    section.right_margin = Twips(1080)

    # -- Register bullet numbering --
    num_id = _configure_bullet_numbering(doc)

    # ===================================================================
    # HEADER — Name, Title, Contact
    # ===================================================================

    # Name (centered, bold, 18pt)
    # Remove the default empty paragraph that Document() creates
    if doc.paragraphs:
        p_name = doc.paragraphs[0]
    else:
        p_name = doc.add_paragraph()
    p_name.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _set_spacing(p_name, after=0)
    _bold_run(p_name, ir.header.name, size_hp=36, color=DARK)

    # Title (centered, accent)
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _set_spacing(p_title, before=40, after=60)
    _plain_run(p_title, ir.header.title, size_hp=22, color=ACCENT)

    # Contact line (centered, muted + accent for links)
    p_contact = doc.add_paragraph()
    p_contact.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _set_spacing(p_contact, after=100)

    contact_parts = [
        (ir.header.location, MUTED),
        ("  |  ", MUTED),
        (ir.header.email, MUTED),
        ("  |  ", MUTED),
        (ir.header.linkedin, ACCENT),
        ("  |  ", MUTED),
        (ir.header.github, ACCENT),
    ]
    for text, color in contact_parts:
        _plain_run(p_contact, text, size_hp=19, color=color)

    # ===================================================================
    # PROFESSIONAL SUMMARY
    # ===================================================================
    _add_section_heading(doc, "Professional Summary")

    # Summary paragraph — parse **bold** markers
    p_summary = doc.add_paragraph()
    _set_spacing(p_summary, before=60, after=60)
    _add_parsed_runs(p_summary, ir.summary.paragraph, size_hp=20)

    # Summary bullets
    for sb in ir.summary.bullets:
        _add_bullet(doc, f"**{sb.label}:** {sb.text}", num_id)

    # ===================================================================
    # SKILLS
    # ===================================================================
    _add_section_heading(doc, "Skills")
    _add_skills_table(doc, ir.skills)

    # ===================================================================
    # PROFESSIONAL EXPERIENCE
    # ===================================================================
    _add_section_heading(doc, "Professional Experience")

    for company in ir.experience:
        # Company subheading with location
        _add_subheading(doc, company.company, company.location)

        # Company description + dates on the same line (if description exists)
        if company.description:
            p_desc = doc.add_paragraph()
            _set_spacing(p_desc, before=0, after=20)
            _add_tab_stop_right_max(p_desc)
            r = _italic_run(p_desc, company.description, size_hp=19, color=MUTED)
            _plain_run(p_desc, f"\t{company.dates}", size_hp=19, color=MUTED).italic = True

        for role in company.roles:
            _add_role_title(doc, role.title, role.dates)
            if role.description:
                _add_role_description(doc, role.description)
            for bullet in role.bullets:
                _add_bullet(doc, _format_bullet_text(bullet), num_id)

    # ===================================================================
    # PERSONAL PROJECTS
    # ===================================================================
    _add_section_heading(doc, "Personal Projects")

    for project in ir.projects:
        # Project name — URL line
        p_proj = doc.add_paragraph()
        _set_spacing(p_proj, before=100, after=40)
        _bold_run(p_proj, project.name, size_hp=20)
        _plain_run(p_proj, " — ", size_hp=20)
        # URL displayed without https:// prefix, in accent color
        display_url = project.url.replace("https://", "").replace("http://", "")
        _plain_run(p_proj, display_url, size_hp=20, color=ACCENT)

        # Project description with **bold** parsing
        p_pdesc = doc.add_paragraph()
        _set_spacing(p_pdesc, before=0, after=80)
        _add_parsed_runs(p_pdesc, project.description, size_hp=20)

    # ===================================================================
    # EDUCATION
    # ===================================================================
    _add_section_heading(doc, "Education")

    p_edu = doc.add_paragraph()
    _set_spacing(p_edu, before=60, after=0)
    _bold_run(p_edu, ir.education.degree, size_hp=20)
    _plain_run(p_edu, f" | {ir.education.institution}", size_hp=20)

    # ===================================================================
    # Save
    # ===================================================================
    doc.save(output_path)
