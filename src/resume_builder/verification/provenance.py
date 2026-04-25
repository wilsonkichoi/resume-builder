from __future__ import annotations

import re
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from enum import Enum
from pathlib import Path

import yaml

from resume_builder.models.resume import ResumeIR
from resume_builder.parser.resume_parser import parse_resume


class Severity(Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass
class Claim:
    text: str
    location: str
    technologies: list[str] = field(default_factory=list)
    metrics: list[str] = field(default_factory=list)


@dataclass
class Finding:
    severity: Severity
    message: str
    source_text: str = ""
    generated_text: str = ""
    similarity: float = 0.0


class ClaimRegistry:
    """Indexes every verifiable claim from resume.yaml for comparison."""

    def __init__(self, ir: ResumeIR) -> None:
        self.claims: list[Claim] = []
        self.technologies: set[str] = set()
        self.metrics: list[str] = []
        self._index(ir)

    @classmethod
    def from_yaml(cls, path: str | Path) -> ClaimRegistry:
        return cls(parse_resume(path))

    def _index(self, ir: ResumeIR) -> None:
        for bullet in ir.summary.bullets:
            self._add_claim(bullet.text, f"Summary > {bullet.label}")

        for company in ir.experience:
            for role in company.roles:
                if role.description:
                    self._add_claim(
                        role.description,
                        f"{company.company} > {role.title} > description",
                    )
                for bullet in role.bullets:
                    self._add_claim(
                        bullet.text,
                        f"{company.company} > {role.title} > {bullet.label}",
                        technologies=bullet.technologies,
                        metrics=bullet.metrics,
                    )

        for project in ir.projects:
            self._add_claim(
                project.description,
                f"Project: {project.name}",
                technologies=project.technologies,
            )

    def _add_claim(
        self,
        text: str,
        location: str,
        technologies: list[str] | None = None,
        metrics: list[str] | None = None,
    ) -> None:
        techs = technologies or []
        mets = metrics or []
        self.claims.append(Claim(text=text, location=location, technologies=techs, metrics=mets))
        self.technologies.update(techs)
        self.metrics.extend(mets)

    def find_best_match(self, text: str) -> tuple[Claim | None, float]:
        best_claim: Claim | None = None
        best_ratio = 0.0
        normalized = _normalize(text)
        for claim in self.claims:
            ratio = SequenceMatcher(None, _normalize(claim.text), normalized).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_claim = claim
        return best_claim, best_ratio

    def has_technology(self, tech: str) -> bool:
        tech_lower = tech.lower()
        return any(t.lower() == tech_lower for t in self.technologies)

    def has_metric(self, metric: str) -> bool:
        metric_lower = metric.lower()
        return any(metric_lower in m.lower() for m in self.metrics)


# --- Diff Checker ---

REPHRASE_THRESHOLD = 0.70
MINOR_REWORD_THRESHOLD = 0.90


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _extract_numbers(text: str) -> list[str]:
    raw = re.findall(r"\d+[\d,.]*[%x]?", text)
    return [re.sub(r"[.x]+$", "", n) for n in raw]


def check_bullet(registry: ClaimRegistry, generated_text: str) -> Finding:
    claim, similarity = registry.find_best_match(generated_text)

    if similarity >= MINOR_REWORD_THRESHOLD:
        return Finding(
            severity=Severity.INFO,
            message="Minor rewording of source claim",
            source_text=claim.text if claim else "",
            generated_text=generated_text,
            similarity=similarity,
        )

    if similarity >= REPHRASE_THRESHOLD:
        source_nums = set(_extract_numbers(claim.text)) if claim else set()
        gen_nums = set(_extract_numbers(generated_text))
        new_nums = gen_nums - source_nums
        if new_nums:
            return Finding(
                severity=Severity.ERROR,
                message=f"Metrics differ from source: added {new_nums}",
                source_text=claim.text if claim else "",
                generated_text=generated_text,
                similarity=similarity,
            )
        return Finding(
            severity=Severity.WARNING,
            message="Rephrased — meaning may have changed",
            source_text=claim.text if claim else "",
            generated_text=generated_text,
            similarity=similarity,
        )

    return Finding(
        severity=Severity.ERROR,
        message="No matching source claim found — possible fabrication",
        source_text=claim.text if claim else "",
        generated_text=generated_text,
        similarity=similarity,
    )


def check_technologies(registry: ClaimRegistry, technologies: list[str]) -> list[Finding]:
    findings: list[Finding] = []
    for tech in technologies:
        if not registry.has_technology(tech):
            findings.append(
                Finding(
                    severity=Severity.ERROR,
                    message=f"Technology '{tech}' not found in source resume",
                    generated_text=tech,
                )
            )
    return findings


# --- Corrections ---

@dataclass
class Correction:
    date: str
    type: str
    original: str
    corrected: str
    context: str


def load_corrections(path: str | Path) -> list[Correction]:
    path = Path(path)
    if not path.exists():
        return []
    with path.open() as f:
        data = yaml.safe_load(f)
    if not data or not data.get("corrections"):
        return []
    return [Correction(**c) for c in data["corrections"]]


def check_corrections(corrections: list[Correction], text: str) -> list[Finding]:
    findings: list[Finding] = []
    normalized = _normalize(text)
    for correction in corrections:
        orig_normalized = _normalize(correction.original)
        if SequenceMatcher(None, orig_normalized, normalized).ratio() >= REPHRASE_THRESHOLD:
            findings.append(
                Finding(
                    severity=Severity.ERROR,
                    message=f"Reintroduced previously corrected error ({correction.type}): '{correction.original}' → '{correction.corrected}'",
                    source_text=correction.corrected,
                    generated_text=text,
                )
            )
    return findings


# --- Full Verification ---

@dataclass
class VerificationReport:
    findings: list[Finding] = field(default_factory=list)

    @property
    def errors(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == Severity.ERROR]

    @property
    def warnings(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == Severity.WARNING]

    @property
    def infos(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == Severity.INFO]

    @property
    def passed(self) -> bool:
        return len(self.errors) == 0


def verify_generated_text(
    registry: ClaimRegistry,
    generated_lines: list[str],
    corrections: list[Correction] | None = None,
) -> VerificationReport:
    report = VerificationReport()
    corrections = corrections or []

    for line in generated_lines:
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("---"):
            continue

        bullet_text = re.sub(r"^[-•*]\s*", "", line)
        bullet_text = re.sub(r"\*\*([^*]+)\*\*", r"\1", bullet_text)
        if not bullet_text or len(bullet_text) < 20:
            continue

        report.findings.append(check_bullet(registry, bullet_text))
        report.findings.extend(check_corrections(corrections, bullet_text))

    return report


def extract_bullets_from_markdown(md_text: str) -> list[str]:
    lines = []
    for line in md_text.splitlines():
        stripped = line.strip()
        if stripped.startswith(("- ", "* ", "• ")):
            lines.append(stripped)
    return lines
