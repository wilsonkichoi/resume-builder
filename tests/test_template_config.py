"""Tests for TemplateConfig Pydantic schema."""

import pytest
from pydantic import ValidationError

from resume_builder.models.template_config import (
    ColorConfig,
    FontConfig,
    MarginConfig,
    PageConfig,
    StyleEntry,
    StylesConfig,
    TemplateConfig,
)


class TestColorConfig:
    def test_defaults(self):
        c = ColorConfig()
        assert c.dark == "#1A1A2E"
        assert c.accent == "#2E5090"
        assert c.muted == "#555555"
        assert c.light_bg == "#F0F4F8"
        assert c.rule == "#2E5090"

    def test_override(self):
        c = ColorConfig(accent="#E53E3E")
        assert c.accent == "#E53E3E"
        assert c.dark == "#1A1A2E"

    def test_invalid_hex_rejected(self):
        with pytest.raises(ValidationError, match="Invalid hex color"):
            ColorConfig(accent="not-a-color")

    def test_short_hex_rejected(self):
        with pytest.raises(ValidationError, match="Invalid hex color"):
            ColorConfig(accent="#FFF")

    def test_rgb_without_hash_rejected(self):
        with pytest.raises(ValidationError, match="Invalid hex color"):
            ColorConfig(accent="2E5090")


class TestStyleEntry:
    def test_all_none_by_default(self):
        s = StyleEntry()
        assert s.font_name is None
        assert s.font_size is None
        assert s.leading is None
        assert s.alignment is None
        assert s.text_color is None

    def test_partial_override(self):
        s = StyleEntry(font_size=14)
        assert s.font_size == 14
        assert s.font_name is None

    def test_invalid_text_color_rejected(self):
        with pytest.raises(ValidationError, match="Invalid hex color"):
            StyleEntry(text_color="red")

    def test_valid_text_color(self):
        s = StyleEntry(text_color="#FF0000")
        assert s.text_color == "#FF0000"


class TestTemplateConfig:
    def test_full_defaults(self):
        config = TemplateConfig()
        assert config.colors.accent == "#2E5090"
        assert config.page.size == "letter"
        assert config.page.margins.top == 0.625
        assert config.fonts.primary == "Helvetica"
        assert config.styles.name.font_size is None

    def test_roundtrip_serialization(self):
        config = TemplateConfig()
        data = config.model_dump()
        restored = TemplateConfig.model_validate(data)
        assert restored == config

    def test_partial_override_preserves_defaults(self):
        config = TemplateConfig.model_validate({
            "colors": {"accent": "#E53E3E"},
            "styles": {"name": {"font_size": 24}},
        })
        assert config.colors.accent == "#E53E3E"
        assert config.colors.dark == "#1A1A2E"
        assert config.styles.name.font_size == 24
        assert config.styles.title.font_size is None

    def test_empty_dict_produces_defaults(self):
        config = TemplateConfig.model_validate({})
        assert config == TemplateConfig()

    def test_a4_page_size(self):
        config = TemplateConfig.model_validate({"page": {"size": "a4"}})
        assert config.page.size == "a4"

    def test_invalid_page_size_rejected(self):
        with pytest.raises(ValidationError):
            TemplateConfig.model_validate({"page": {"size": "tabloid"}})
