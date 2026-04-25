from pathlib import Path

from resume_builder.models.resume import ResumeIR
from resume_builder.parser.resume_parser import parse_resume

FIXTURE = Path(__file__).parent / "fixtures" / "sample_resume.yaml"


def test_parse_resume_returns_resume_ir():
    ir = parse_resume(FIXTURE)
    assert isinstance(ir, ResumeIR)


def test_header_fields():
    ir = parse_resume(FIXTURE)
    assert ir.header.name == "Jane Doe"
    assert "Senior Software Engineer" in ir.header.title
    assert ir.header.email == "jane@example.com"
    assert ir.header.linkedin == "linkedin.com/in/janedoe"
    assert ir.header.github == "github.com/janedoe"


def test_summary_has_bullets():
    ir = parse_resume(FIXTURE)
    assert len(ir.summary.bullets) == 3
    labels = [b.label for b in ir.summary.bullets]
    assert "Track Record" in labels
    assert "Leadership" in labels
    assert "Core Strengths" in labels


def test_skills_categories():
    ir = parse_resume(FIXTURE)
    assert len(ir.skills) == 3
    categories = [s.category for s in ir.skills]
    assert "Languages" in categories
    assert "Cloud" in categories
    assert "Databases" in categories


def test_experience_companies():
    ir = parse_resume(FIXTURE)
    assert len(ir.experience) == 2
    companies = [c.company for c in ir.experience]
    assert "Acme Corp" in companies
    assert "StartupXYZ" in companies


def test_acme_roles():
    ir = parse_resume(FIXTURE)
    acme = next(c for c in ir.experience if c.company == "Acme Corp")
    assert len(acme.roles) == 2
    titles = [r.title for r in acme.roles]
    assert "Senior Software Engineer" in titles
    assert "Software Engineer" in titles


def test_bullets_have_provenance():
    ir = parse_resume(FIXTURE)
    for company in ir.experience:
        for role in company.roles:
            for bullet in role.bullets:
                assert bullet.provenance is not None
                assert bullet.provenance.verified is True


def test_projects():
    ir = parse_resume(FIXTURE)
    assert len(ir.projects) == 2
    names = [p.name for p in ir.projects]
    assert "OpenTracer" in names
    assert "KVStore" in names


def test_projects_have_provenance():
    ir = parse_resume(FIXTURE)
    for project in ir.projects:
        assert project.provenance is not None
        assert project.provenance.verified is True


def test_education():
    ir = parse_resume(FIXTURE)
    assert "Computer Science" in ir.education.degree
    assert "Berkeley" in ir.education.institution


def test_total_bullet_count():
    ir = parse_resume(FIXTURE)
    total = sum(len(r.bullets) for c in ir.experience for r in c.roles)
    assert total == 6
