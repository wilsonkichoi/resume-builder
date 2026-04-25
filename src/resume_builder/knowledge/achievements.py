from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml


ACHIEVEMENTS_PATH = Path("knowledge/achievements.yaml")


@dataclass
class PhrasingVariant:
    text: str
    session_id: str
    target_role: str = ""
    score: float | None = None


@dataclass
class Achievement:
    bullet_label: str
    company: str
    role: str
    variants: list[PhrasingVariant] = field(default_factory=list)
    best_score: float | None = None
    best_variant_index: int | None = None

    def add_variant(
        self, text: str, session_id: str, target_role: str = "", score: float | None = None
    ) -> None:
        self.variants.append(
            PhrasingVariant(text=text, session_id=session_id, target_role=target_role, score=score)
        )
        if score is not None and (self.best_score is None or score > self.best_score):
            self.best_score = score
            self.best_variant_index = len(self.variants) - 1

    def best_variant(self) -> PhrasingVariant | None:
        if self.best_variant_index is not None and self.best_variant_index < len(self.variants):
            return self.variants[self.best_variant_index]
        return self.variants[-1] if self.variants else None

    def to_dict(self) -> dict:
        return {
            "bullet_label": self.bullet_label,
            "company": self.company,
            "role": self.role,
            "best_score": self.best_score,
            "best_variant_index": self.best_variant_index,
            "variants": [
                {
                    "text": v.text,
                    "session_id": v.session_id,
                    "target_role": v.target_role,
                    "score": v.score,
                }
                for v in self.variants
            ],
        }

    @classmethod
    def from_dict(cls, data: dict) -> Achievement:
        variants = [PhrasingVariant(**v) for v in data.get("variants", [])]
        return cls(
            bullet_label=data["bullet_label"],
            company=data["company"],
            role=data["role"],
            best_score=data.get("best_score"),
            best_variant_index=data.get("best_variant_index"),
            variants=variants,
        )


class AchievementStore:
    def __init__(self, path: str | Path = ACHIEVEMENTS_PATH) -> None:
        self.path = Path(path)
        self.achievements: list[Achievement] = []
        if self.path.exists():
            self._load()

    def _load(self) -> None:
        with self.path.open() as f:
            data = yaml.safe_load(f)
        if not data or not data.get("achievements"):
            return
        self.achievements = [Achievement.from_dict(a) for a in data["achievements"]]

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w") as f:
            yaml.dump(
                {"achievements": [a.to_dict() for a in self.achievements]},
                f,
                default_flow_style=False,
                sort_keys=False,
            )

    def find(self, bullet_label: str, company: str, role: str) -> Achievement | None:
        for a in self.achievements:
            if a.bullet_label == bullet_label and a.company == company and a.role == role:
                return a
        return None

    def get_or_create(self, bullet_label: str, company: str, role: str) -> Achievement:
        existing = self.find(bullet_label, company, role)
        if existing:
            return existing
        achievement = Achievement(bullet_label=bullet_label, company=company, role=role)
        self.achievements.append(achievement)
        return achievement

    def record_variant(
        self,
        bullet_label: str,
        company: str,
        role: str,
        text: str,
        session_id: str,
        target_role: str = "",
        score: float | None = None,
    ) -> Achievement:
        achievement = self.get_or_create(bullet_label, company, role)
        achievement.add_variant(text, session_id, target_role, score)
        return achievement

    def best_variants_for_role(self, target_role: str) -> list[tuple[Achievement, PhrasingVariant]]:
        results = []
        for a in self.achievements:
            role_variants = [v for v in a.variants if v.target_role == target_role and v.score is not None]
            if role_variants:
                best = max(role_variants, key=lambda v: v.score or 0)
                results.append((a, best))
        return results
