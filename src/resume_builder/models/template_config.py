"""Pydantic schema for template customization.

Users place a ``pdf_styles.yaml`` or ``docx_styles.yaml`` in their project's
``templates/`` directory.  Every field has a default matching the current
hardcoded renderer output, so an empty file produces identical results.
"""

from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, field_validator


class ColorConfig(BaseModel):
    """Five color roles used across PDF and DOCX renderers."""

    dark: str = "#1A1A2E"
    accent: str = "#2E5090"
    muted: str = "#555555"
    light_bg: str = "#F0F4F8"
    rule: str = "#2E5090"

    @field_validator("*", mode="before")
    @classmethod
    def validate_hex_color(cls, v: str) -> str:
        if not isinstance(v, str) or not re.match(r"^#[0-9A-Fa-f]{6}$", v):
            raise ValueError(f"Invalid hex color: {v!r}. Must be #RRGGBB format.")
        return v


class MarginConfig(BaseModel):
    """Page margins in inches."""

    top: float = 0.625
    bottom: float = 0.625
    left: float = 0.75
    right: float = 0.75


class PageConfig(BaseModel):
    size: Literal["letter", "a4"] = "letter"
    margins: MarginConfig = MarginConfig()


class FontConfig(BaseModel):
    """Font family names (PDF names; DOCX renderer maps automatically)."""

    primary: str = "Helvetica"
    primary_bold: str = "Helvetica-Bold"
    primary_italic: str = "Helvetica-Oblique"
    primary_bold_italic: str = "Helvetica-BoldOblique"


class StyleEntry(BaseModel):
    """Individual style properties.  All optional — only override what you need."""

    font_name: str | None = None
    font_size: float | None = None
    leading: float | None = None
    alignment: Literal["left", "center", "right"] | None = None
    text_color: str | None = None
    space_before: float | None = None
    space_after: float | None = None
    left_indent: float | None = None
    bullet_indent: float | None = None

    @field_validator("text_color", mode="before")
    @classmethod
    def validate_text_color(cls, v: str | None) -> str | None:
        if v is not None and not re.match(r"^#[0-9A-Fa-f]{6}$", v):
            raise ValueError(f"Invalid hex color: {v!r}. Must be #RRGGBB format.")
        return v


class StylesConfig(BaseModel):
    """One entry per visual element.  Defaults are empty (inherit from built-in)."""

    name: StyleEntry = StyleEntry()
    title: StyleEntry = StyleEntry()
    contact: StyleEntry = StyleEntry()
    section: StyleEntry = StyleEntry()
    company: StyleEntry = StyleEntry()
    company_desc: StyleEntry = StyleEntry()
    role: StyleEntry = StyleEntry()
    role_desc: StyleEntry = StyleEntry()
    bullet: StyleEntry = StyleEntry()
    body: StyleEntry = StyleEntry()
    skill_label: StyleEntry = StyleEntry()
    skill_value: StyleEntry = StyleEntry()
    project_title: StyleEntry = StyleEntry()
    project_desc: StyleEntry = StyleEntry()
    education: StyleEntry = StyleEntry()


class TemplateConfig(BaseModel):
    """Top-level template configuration for PDF and DOCX renderers."""

    colors: ColorConfig = ColorConfig()
    page: PageConfig = PageConfig()
    fonts: FontConfig = FontConfig()
    styles: StylesConfig = StylesConfig()
