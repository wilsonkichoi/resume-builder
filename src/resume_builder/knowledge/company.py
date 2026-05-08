from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import yaml

from resume_builder.models.company import CompanyProfile


SESSIONS_DIR = Path("knowledge/sessions")


def slugify(name: str) -> str:
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    name = name.lower()
    name = re.sub(r"[^a-z0-9]+", "-", name)
    return name.strip("-")


class CompanyStore:
    """Stores CompanyProfile at knowledge/sessions/{slug}/company.yaml."""

    def __init__(self, sessions_dir: str | Path = SESSIONS_DIR) -> None:
        self.sessions_dir = Path(sessions_dir)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

    def _profile_path(self, slug: str) -> Path:
        return self.sessions_dir / slug / "company.yaml"

    def save(self, profile: CompanyProfile) -> Path:
        path = self._profile_path(profile.basics.slug)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w") as f:
            yaml.dump(
                profile.model_dump(exclude_none=True),
                f,
                default_flow_style=False,
                sort_keys=False,
            )
        return path

    def load(self, slug: str) -> CompanyProfile:
        path = self._profile_path(slug)
        with path.open() as f:
            data = yaml.safe_load(f)
        return CompanyProfile.model_validate(data)

    def find_by_name(self, name: str) -> CompanyProfile | None:
        needle = name.lower()
        for path in self.sessions_dir.glob("*/company.yaml"):
            with path.open() as f:
                data = yaml.safe_load(f)
            if data and data.get("basics", {}).get("name", "").lower() == needle:
                return CompanyProfile.model_validate(data)
        return None

    def list_companies(self) -> list[CompanyProfile]:
        profiles = []
        for path in sorted(self.sessions_dir.glob("*/company.yaml")):
            with path.open() as f:
                data = yaml.safe_load(f)
            if data:
                profiles.append(CompanyProfile.model_validate(data))
        return profiles

    def exists(self, slug: str) -> bool:
        return self._profile_path(slug).exists()

    def delete(self, slug: str) -> bool:
        path = self._profile_path(slug)
        if path.exists():
            path.unlink()
            return True
        return False
