from pathlib import Path

from resume_builder.parser.resume_parser import parse_resume
from resume_builder.verification.provenance import (
    ClaimRegistry,
    Correction,
    Severity,
    check_bullet,
    check_corrections,
    check_technologies,
    extract_bullets_from_markdown,
    verify_generated_text,
)

FIXTURE = Path(__file__).parent / "fixtures" / "sample_resume.yaml"


def _registry() -> ClaimRegistry:
    return ClaimRegistry.from_yaml(FIXTURE)


class TestClaimRegistry:
    def test_indexes_all_claims(self):
        reg = _registry()
        # 3 summary + 1 role desc + 6 bullets + 2 project descs = 12+
        assert len(reg.claims) >= 12

    def test_includes_technologies(self):
        reg = _registry()
        assert reg.has_technology("FastAPI")
        assert reg.has_technology("Kafka")
        assert not reg.has_technology("Rust")

    def test_includes_metrics(self):
        reg = _registry()
        assert reg.has_metric("500ms to 120ms")
        assert reg.has_metric("2M events per day")

    def test_find_best_match_exact(self):
        reg = _registry()
        claim, ratio = reg.find_best_match(
            "Redesigned the REST API layer using FastAPI, reducing p99 latency "
            "from 500ms to 120ms and improving throughput by 3x."
        )
        assert claim is not None
        assert ratio > 0.95
        assert "API Redesign" in claim.location

    def test_find_best_match_rephrase(self):
        reg = _registry()
        claim, ratio = reg.find_best_match(
            "Revamped REST API with FastAPI, cutting p99 latency from 500ms to 120ms "
            "and boosting throughput 3x."
        )
        assert claim is not None
        assert ratio > 0.5

    def test_find_best_match_fabrication(self):
        reg = _registry()
        _, ratio = reg.find_best_match(
            "Built a quantum computing pipeline that reduced processing time by 99%."
        )
        assert ratio < 0.5


class TestDiffChecker:
    def test_exact_match_is_info(self):
        reg = _registry()
        finding = check_bullet(
            reg,
            "Redesigned the REST API layer using FastAPI, reducing p99 latency "
            "from 500ms to 120ms and improving throughput by 3x.",
        )
        assert finding.severity == Severity.INFO

    def test_rephrase_is_warning_or_info(self):
        reg = _registry()
        finding = check_bullet(
            reg,
            "Revamped the REST API using FastAPI, reducing p99 latency from 500ms to 120ms "
            "and improving throughput by a factor of 3.",
        )
        assert finding.severity in (Severity.INFO, Severity.WARNING)

    def test_fabrication_is_error(self):
        reg = _registry()
        finding = check_bullet(
            reg,
            "Built a quantum computing pipeline that processed 1 billion transactions per second.",
        )
        assert finding.severity == Severity.ERROR

    def test_added_metric_is_error(self):
        reg = _registry()
        finding = check_bullet(
            reg,
            "Redesigned the REST API layer using FastAPI, reducing p99 latency "
            "from 500ms to 120ms and improving throughput by 3x, saving $2M annually.",
        )
        if finding.severity == Severity.ERROR:
            assert "Metrics differ" in finding.message or "fabrication" in finding.message.lower()


class TestTechnologyCheck:
    def test_valid_technologies_pass(self):
        reg = _registry()
        findings = check_technologies(reg, ["FastAPI", "Python", "Kafka"])
        assert len(findings) == 0

    def test_fabricated_technology_flagged(self):
        reg = _registry()
        findings = check_technologies(reg, ["FastAPI", "Terraform", "Spark"])
        assert len(findings) >= 2
        assert all(f.severity == Severity.ERROR for f in findings)


class TestCorrections:
    def test_empty_corrections(self):
        findings = check_corrections([], "Some text")
        assert len(findings) == 0

    def test_catches_reintroduced_error(self):
        corrections = [
            Correction(
                date="2025-01-01",
                type="fabricated_metric",
                original="reduced costs by 90%",
                corrected="reduced costs significantly",
                context="Summary bullet",
            )
        ]
        findings = check_corrections(corrections, "reduced costs by 90%")
        assert len(findings) == 1
        assert findings[0].severity == Severity.ERROR

    def test_ignores_unrelated_text(self):
        corrections = [
            Correction(
                date="2025-01-01",
                type="fabricated_metric",
                original="reduced costs by 90%",
                corrected="reduced costs significantly",
                context="Summary bullet",
            )
        ]
        findings = check_corrections(corrections, "Built a gRPC-based push notification service")
        assert len(findings) == 0


class TestVerificationReport:
    def test_clean_source_passes(self):
        reg = _registry()
        ir = parse_resume(FIXTURE)
        bullets = []
        for company in ir.experience:
            for role in company.roles:
                for bullet in role.bullets:
                    bullets.append(f"- {bullet.text}")
        report = verify_generated_text(reg, bullets)
        assert report.passed
        assert len(report.errors) == 0

    def test_fabricated_content_fails(self):
        reg = _registry()
        bullets = [
            "- Built a quantum computing pipeline that processed 1 billion transactions.",
            "- Designed a blockchain-based authentication system for 500M users.",
        ]
        report = verify_generated_text(reg, bullets)
        assert not report.passed
        assert len(report.errors) >= 1


class TestExtractBullets:
    def test_extracts_bullets(self):
        md = """# Resume
- First bullet point here
- Second bullet about something
* Third with asterisk marker
Some paragraph text
- Fourth bullet after paragraph
"""
        bullets = extract_bullets_from_markdown(md)
        assert len(bullets) == 4

    def test_ignores_non_bullets(self):
        md = """# Heading
Some paragraph text that is long enough to matter.
## Another heading
"""
        bullets = extract_bullets_from_markdown(md)
        assert len(bullets) == 0
