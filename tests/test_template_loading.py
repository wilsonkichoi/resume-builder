"""Tests for template discovery, loading, and resolution."""

import pytest
import yaml

from resume_builder.models.template_config import TemplateConfig
from resume_builder.templates import (
    discover_html_template,
    discover_template_dir,
    export_defaults,
    load_template_config,
    resolve_colors,
    resolve_docx_font,
    resolve_docx_page,
    resolve_docx_style,
    resolve_page_size,
    resolve_pdf_styles,
    validate_templates,
)


class TestDiscoverTemplateDir:
    def test_explicit_path(self, tmp_path):
        d = tmp_path / "my-templates"
        d.mkdir()
        result = discover_template_dir(str(d), tmp_path / "resume.yaml")
        assert result == d

    def test_auto_discover(self, tmp_path):
        (tmp_path / "templates").mkdir()
        result = discover_template_dir(None, tmp_path / "resume.yaml")
        assert result == tmp_path / "templates"

    def test_none_when_no_templates(self, tmp_path):
        result = discover_template_dir(None, tmp_path / "resume.yaml")
        assert result is None

    def test_none_for_nonexistent_explicit(self, tmp_path):
        result = discover_template_dir(str(tmp_path / "nope"), tmp_path / "resume.yaml")
        assert result is None


class TestLoadTemplateConfig:
    def test_missing_file_returns_default(self, tmp_path):
        config = load_template_config(tmp_path, "pdf")
        assert config == TemplateConfig()

    def test_none_dir_returns_default(self):
        config = load_template_config(None, "pdf")
        assert config == TemplateConfig()

    def test_loads_yaml(self, tmp_path):
        (tmp_path / "pdf_styles.yaml").write_text(yaml.dump({
            "colors": {"accent": "#FF0000"},
        }))
        config = load_template_config(tmp_path, "pdf")
        assert config.colors.accent == "#FF0000"
        assert config.colors.dark == "#1A1A2E"

    def test_empty_yaml_returns_default(self, tmp_path):
        (tmp_path / "pdf_styles.yaml").write_text("")
        config = load_template_config(tmp_path, "pdf")
        assert config == TemplateConfig()


class TestDiscoverHtmlTemplate:
    def test_none_dir(self):
        j2, css = discover_html_template(None)
        assert j2 is None and css is None

    def test_finds_both(self, tmp_path):
        (tmp_path / "resume.html.j2").write_text("<html>{{ ir.header.name }}</html>")
        (tmp_path / "style.css").write_text(":root { --accent: red; }")
        j2, css = discover_html_template(tmp_path)
        assert j2 == tmp_path / "resume.html.j2"
        assert css == tmp_path / "style.css"

    def test_missing_files(self, tmp_path):
        j2, css = discover_html_template(tmp_path)
        assert j2 is None and css is None


class TestResolveColors:
    def test_default_colors(self):
        colors = resolve_colors(TemplateConfig())
        assert colors.accent.hexval() == "0x2e5090"

    def test_custom_accent(self):
        config = TemplateConfig.model_validate({"colors": {"accent": "#FF0000"}})
        colors = resolve_colors(config)
        assert colors.accent.hexval() == "0xff0000"


class TestResolvePdfStyles:
    def test_default_styles_have_all_keys(self):
        styles = resolve_pdf_styles(TemplateConfig())
        expected = {
            "name", "title", "contact", "section", "company", "company_desc",
            "role", "role_desc", "bullet", "body", "skill_label", "skill_value",
            "project_title", "project_desc", "education",
        }
        assert set(styles.keys()) == expected

    def test_name_is_18pt_bold_centered(self):
        styles = resolve_pdf_styles(TemplateConfig())
        assert styles["name"].fontSize == 18
        assert styles["name"].fontName == "Helvetica-Bold"
        assert styles["name"].alignment == 1  # TA_CENTER

    def test_custom_font_size_overrides(self):
        config = TemplateConfig.model_validate({"styles": {"name": {"font_size": 24}}})
        styles = resolve_pdf_styles(config)
        assert styles["name"].fontSize == 24

    def test_accent_color_flows_to_title(self):
        config = TemplateConfig.model_validate({"colors": {"accent": "#FF0000"}})
        styles = resolve_pdf_styles(config)
        assert styles["title"].textColor.hexval() == "0xff0000"

    def test_text_color_override_breaks_link(self):
        config = TemplateConfig.model_validate({
            "colors": {"accent": "#FF0000"},
            "styles": {"title": {"text_color": "#00FF00"}},
        })
        styles = resolve_pdf_styles(config)
        assert styles["title"].textColor.hexval() == "0x00ff00"


class TestResolveDocx:
    def test_font_mapping(self):
        assert resolve_docx_font("Helvetica") == "Arial"
        assert resolve_docx_font("Helvetica-Bold") == "Arial"
        assert resolve_docx_font("Georgia") == "Georgia"

    def test_page_letter(self):
        page = resolve_docx_page(TemplateConfig())
        assert page.width == 12240
        assert page.height == 15840
        assert page.text_width == 12240 - 1080 - 1080

    def test_page_a4(self):
        config = TemplateConfig.model_validate({"page": {"size": "a4"}})
        page = resolve_docx_page(config)
        assert page.width == 11906

    def test_style_resolution(self):
        s = resolve_docx_style("name", TemplateConfig())
        assert s.font_name == "Arial"
        assert s.size_hp == 36  # 18pt * 2


class TestResolvePageSize:
    def test_letter(self):
        from reportlab.lib.pagesizes import letter
        assert resolve_page_size(TemplateConfig()) == letter

    def test_a4(self):
        from reportlab.lib.pagesizes import A4
        config = TemplateConfig.model_validate({"page": {"size": "a4"}})
        assert resolve_page_size(config) == A4


class TestExportDefaults:
    def test_exports_all(self, tmp_path):
        created = export_defaults(tmp_path / "out", ["pdf", "docx", "html", "css"])
        assert len(created) == 4
        assert (tmp_path / "out" / "pdf_styles.yaml").exists()
        assert (tmp_path / "out" / "docx_styles.yaml").exists()
        assert (tmp_path / "out" / "resume.html.j2").exists()
        assert (tmp_path / "out" / "style.css").exists()

    def test_exported_pdf_yaml_is_valid(self, tmp_path):
        export_defaults(tmp_path, ["pdf"])
        config = load_template_config(tmp_path, "pdf")
        assert config.colors.accent == "#2E5090"


class TestValidateTemplates:
    def test_valid_templates(self, tmp_path):
        export_defaults(tmp_path, ["pdf", "docx"])
        errors = validate_templates(tmp_path)
        assert errors == []

    def test_invalid_color(self, tmp_path):
        (tmp_path / "pdf_styles.yaml").write_text(yaml.dump({
            "colors": {"accent": "not-a-color"},
        }))
        errors = validate_templates(tmp_path)
        assert len(errors) > 0
        assert "Invalid hex color" in errors[0]

    def test_nonexistent_dir(self, tmp_path):
        errors = validate_templates(tmp_path / "nope")
        assert len(errors) == 1
        assert "does not exist" in errors[0]

    def test_empty_dir_is_valid(self, tmp_path):
        errors = validate_templates(tmp_path)
        assert errors == []
