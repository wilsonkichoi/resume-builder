from pathlib import Path

import yaml

from resume_builder.core import generate_outputs
from resume_builder.models.resume import ResumeIR
from resume_builder.parser.resume_parser import parse_resume

FIXTURE = Path(__file__).parent / "fixtures" / "sample_resume.yaml"


def _names(results):
    return {Path(r.path).name for r in results}


def test_output_name_defaults_to_resume(tmp_path):
    results = generate_outputs(FIXTURE, ["md"], output_dir=tmp_path)
    assert _names(results) == {"resume.md"}
    assert (tmp_path / "resume.md").exists()


def test_output_name_arg_sets_basename(tmp_path):
    results = generate_outputs(FIXTURE, ["md"], output_dir=tmp_path, output_name="wilson_resume")
    assert _names(results) == {"wilson_resume.md"}
    assert (tmp_path / "wilson_resume.md").exists()


def test_output_name_from_yaml(tmp_path):
    data = yaml.safe_load(FIXTURE.read_text())
    data["output_name"] = "jane_resume"
    src = tmp_path / "resume.yaml"
    src.write_text(yaml.safe_dump(data))
    results = generate_outputs(src, ["md"], output_dir=tmp_path)
    assert (tmp_path / "jane_resume.md").exists()
    assert _names(results) == {"jane_resume.md"}


def test_output_name_arg_overrides_yaml(tmp_path):
    data = yaml.safe_load(FIXTURE.read_text())
    data["output_name"] = "from_yaml"
    src = tmp_path / "resume.yaml"
    src.write_text(yaml.safe_dump(data))
    results = generate_outputs(src, ["md"], output_dir=tmp_path, output_name="from_arg")
    assert (tmp_path / "from_arg.md").exists()
    assert _names(results) == {"from_arg.md"}


def test_html_always_index_regardless_of_output_name(tmp_path):
    results = generate_outputs(FIXTURE, ["html"], output_dir=tmp_path, output_name="wilson_resume")
    assert _names(results) == {"index.html"}
    assert (tmp_path / "index.html").exists()


def test_output_name_optional_field_roundtrips():
    ir = parse_resume(FIXTURE)
    assert ir.output_name is None
    restored = ResumeIR.model_validate(ir.model_dump())
    assert restored.output_name is None
    with_name = ResumeIR.model_validate({**ir.model_dump(), "output_name": "x"})
    assert with_name.output_name == "x"
