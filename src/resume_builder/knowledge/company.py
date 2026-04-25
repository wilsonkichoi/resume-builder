from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import yaml

from resume_builder.models.company import CompanyProfile


COMPANIES_DIR = Path("knowledge/companies")


def slugify(name: str) -> str:
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    name = name.lower()
    name = re.sub(r"[^a-z0-9]+", "-", name)
    return name.strip("-")


class CompanyStore:
    def __init__(self, companies_dir: str | Path = COMPANIES_DIR) -> None:
        self.companies_dir = Path(companies_dir)
        self.companies_dir.mkdir(parents=True, exist_ok=True)

    def save(self, profile: CompanyProfile) -> Path:
        path = self.companies_dir / f"{profile.basics.slug}.yaml"
        with path.open("w") as f:
            yaml.dump(
                profile.model_dump(exclude_none=True),
                f,
                default_flow_style=False,
                sort_keys=False,
            )
        return path

    def load(self, slug: str) -> CompanyProfile:
        path = self.companies_dir / f"{slug}.yaml"
        with path.open() as f:
            data = yaml.safe_load(f)
        return CompanyProfile.model_validate(data)

    def find_by_name(self, name: str) -> CompanyProfile | None:
        needle = name.lower()
        for path in self.companies_dir.glob("*.yaml"):
            with path.open() as f:
                data = yaml.safe_load(f)
            if data and data.get("basics", {}).get("name", "").lower() == needle:
                return CompanyProfile.model_validate(data)
        return None

    def list_companies(self) -> list[CompanyProfile]:
        profiles = []
        for path in sorted(self.companies_dir.glob("*.yaml")):
            with path.open() as f:
                data = yaml.safe_load(f)
            if data:
                profiles.append(CompanyProfile.model_validate(data))
        return profiles

    def exists(self, slug: str) -> bool:
        return (self.companies_dir / f"{slug}.yaml").exists()

    def delete(self, slug: str) -> bool:
        path = self.companies_dir / f"{slug}.yaml"
        if path.exists():
            path.unlink()
            return True
        return False
