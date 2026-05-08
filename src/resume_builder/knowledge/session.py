from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import yaml

from resume_builder.knowledge.company import slugify


SESSIONS_DIR = Path("knowledge/sessions")


@dataclass
class SessionEntry:
    timestamp: str
    action: str
    details: dict = field(default_factory=dict)


@dataclass
class Session:
    id: str
    skill: str
    started_at: str
    entries: list[SessionEntry] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    ended_at: str | None = None

    def add_entry(self, action: str, **details: object) -> None:
        self.entries.append(
            SessionEntry(
                timestamp=datetime.now(timezone.utc).isoformat(),
                action=action,
                details=dict(details),
            )
        )

    def end(self) -> None:
        self.ended_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "skill": self.skill,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "metadata": self.metadata,
            "entries": [
                {"timestamp": e.timestamp, "action": e.action, "details": e.details}
                for e in self.entries
            ],
        }

    @classmethod
    def from_dict(cls, data: dict) -> Session:
        entries = [SessionEntry(**e) for e in data.get("entries", [])]
        return cls(
            id=data["id"],
            skill=data["skill"],
            started_at=data["started_at"],
            ended_at=data.get("ended_at"),
            metadata=data.get("metadata", {}),
            entries=entries,
        )


class SessionStore:
    def __init__(self, sessions_dir: str | Path = SESSIONS_DIR) -> None:
        self.sessions_dir = Path(sessions_dir)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

    def create(self, skill: str, **metadata: object) -> Session:
        session = Session(
            id=uuid.uuid4().hex[:12],
            skill=skill,
            started_at=datetime.now(timezone.utc).isoformat(),
            metadata=dict(metadata),
        )
        return session

    def save(self, session: Session) -> Path:
        path = self.sessions_dir / f"{session.id}.yaml"
        with path.open("w") as f:
            yaml.dump(session.to_dict(), f, default_flow_style=False, sort_keys=False)
        return path

    def load(self, session_id: str) -> Session:
        path = self.sessions_dir / f"{session_id}.yaml"
        with path.open() as f:
            data = yaml.safe_load(f)
        return Session.from_dict(data)

    def list_sessions(self, skill: str | None = None) -> list[Session]:
        sessions = []
        for path in sorted(self.sessions_dir.rglob("*.yaml")):
            if path.name == "company.yaml":
                continue
            with path.open() as f:
                data = yaml.safe_load(f)
            if data is None:
                continue
            if "id" not in data or "skill" not in data:
                continue
            session = Session.from_dict(data)
            if skill is None or session.skill == skill:
                sessions.append(session)
        return sessions

    def query(self, skill: str | None = None, since: str | None = None) -> list[Session]:
        sessions = self.list_sessions(skill=skill)
        if since:
            sessions = [s for s in sessions if s.started_at >= since]
        return sessions

    def session_path(
        self, company_slug: str, role_slug: str | None, skill: str, date: str
    ) -> Path:
        if role_slug:
            return self.sessions_dir / company_slug / role_slug / f"{date}_{skill}.yaml"
        return self.sessions_dir / company_slug / f"{date}_{skill}.yaml"

    def company_profile_path(self, company_slug: str) -> Path:
        return self.sessions_dir / company_slug / "company.yaml"

    def tailored_dir(self, company_slug: str, role_slug: str) -> Path:
        return self.sessions_dir / company_slug / role_slug / "tailored"

    def summary_path(self, company_slug: str, role_slug: str) -> Path:
        return self.sessions_dir / company_slug / role_slug / "summary.md"

    def find_latest(
        self, company_slug: str, role_slug: str, skill: str
    ) -> Path | None:
        dir_path = self.sessions_dir / company_slug / role_slug
        if not dir_path.is_dir():
            return None
        matches = sorted(dir_path.glob(f"*_{skill}.yaml"), reverse=True)
        return matches[0] if matches else None
