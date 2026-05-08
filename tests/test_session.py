from pathlib import Path

import pytest
import yaml

from resume_builder.knowledge.session import Session, SessionStore


@pytest.fixture()
def tmp_sessions(tmp_path):
    sessions_dir = tmp_path / "sessions"
    sessions_dir.mkdir()
    yield sessions_dir


class TestSession:
    def test_create_and_serialize(self):
        session = Session(id="abc123", skill="tailor", started_at="2025-01-01T00:00:00Z")
        session.add_entry("started", target_role="backend")
        session.add_entry("completed", bullets_modified=5)
        session.end()

        data = session.to_dict()
        assert data["id"] == "abc123"
        assert data["skill"] == "tailor"
        assert len(data["entries"]) == 2
        assert data["ended_at"] is not None

    def test_roundtrip(self):
        session = Session(
            id="xyz789",
            skill="score",
            started_at="2025-01-01T00:00:00Z",
            metadata={"jd_file": "job.txt"},
        )
        session.add_entry("scored", ats_score=85, hr_score=72)

        data = session.to_dict()
        restored = Session.from_dict(data)
        assert restored.id == "xyz789"
        assert restored.skill == "score"
        assert restored.metadata["jd_file"] == "job.txt"
        assert len(restored.entries) == 1
        assert restored.entries[0].details["ats_score"] == 85


class TestSessionStore:
    def test_create_and_save(self, tmp_sessions):
        store = SessionStore(tmp_sessions)
        session = store.create("ingest", project="novascan")
        session.add_entry("started")
        path = store.save(session)

        assert path.exists()
        assert path.suffix == ".yaml"

    def test_load_roundtrip(self, tmp_sessions):
        store = SessionStore(tmp_sessions)
        session = store.create("tailor", target_role="backend")
        session.add_entry("tailored", bullets_changed=3)
        store.save(session)

        loaded = store.load(session.id)
        assert loaded.id == session.id
        assert loaded.skill == "tailor"
        assert len(loaded.entries) == 1

    def test_list_sessions(self, tmp_sessions):
        store = SessionStore(tmp_sessions)
        s1 = store.create("tailor")
        s2 = store.create("score")
        s3 = store.create("tailor")
        store.save(s1)
        store.save(s2)
        store.save(s3)

        all_sessions = store.list_sessions()
        assert len(all_sessions) == 3

        tailor_sessions = store.list_sessions(skill="tailor")
        assert len(tailor_sessions) == 2

    def test_query_with_since(self, tmp_sessions):
        store = SessionStore(tmp_sessions)
        s1 = store.create("tailor")
        s1.started_at = "2025-01-01T00:00:00Z"
        s2 = store.create("tailor")
        s2.started_at = "2025-06-01T00:00:00Z"
        store.save(s1)
        store.save(s2)

        results = store.query(since="2025-03-01T00:00:00Z")
        assert len(results) == 1
        assert results[0].id == s2.id

    def test_list_sessions_recursive(self, tmp_sessions):
        store = SessionStore(tmp_sessions)
        s1 = store.create("match")
        s2 = store.create("tailor")

        nested_dir = tmp_sessions / "acme-corp" / "staff-engineer"
        nested_dir.mkdir(parents=True)
        path1 = nested_dir / "2026-05-01_match.yaml"
        path2 = nested_dir / "2026-05-01_tailor.yaml"
        with path1.open("w") as f:
            yaml.dump(s1.to_dict(), f)
        with path2.open("w") as f:
            yaml.dump(s2.to_dict(), f)

        all_sessions = store.list_sessions()
        assert len(all_sessions) == 2

        match_only = store.list_sessions(skill="match")
        assert len(match_only) == 1

    def test_list_sessions_skips_company_yaml(self, tmp_sessions):
        store = SessionStore(tmp_sessions)
        company_dir = tmp_sessions / "acme-corp"
        company_dir.mkdir()
        company_file = company_dir / "company.yaml"
        with company_file.open("w") as f:
            yaml.dump({"basics": {"name": "Acme"}}, f)

        assert store.list_sessions() == []


class TestSessionStorePaths:
    def test_session_path_with_role(self, tmp_sessions):
        store = SessionStore(tmp_sessions)
        path = store.session_path("acme-corp", "staff-engineer", "match", "2026-05-01")
        expected = tmp_sessions / "acme-corp" / "staff-engineer" / "2026-05-01_match.yaml"
        assert path == expected

    def test_session_path_without_role(self, tmp_sessions):
        store = SessionStore(tmp_sessions)
        path = store.session_path("acme-corp", None, "research", "2026-05-01")
        expected = tmp_sessions / "acme-corp" / "2026-05-01_research.yaml"
        assert path == expected

    def test_company_profile_path(self, tmp_sessions):
        store = SessionStore(tmp_sessions)
        path = store.company_profile_path("acme-corp")
        expected = tmp_sessions / "acme-corp" / "company.yaml"
        assert path == expected

    def test_tailored_dir(self, tmp_sessions):
        store = SessionStore(tmp_sessions)
        path = store.tailored_dir("acme-corp", "staff-engineer")
        expected = tmp_sessions / "acme-corp" / "staff-engineer" / "tailored"
        assert path == expected

    def test_summary_path(self, tmp_sessions):
        store = SessionStore(tmp_sessions)
        path = store.summary_path("acme-corp", "staff-engineer")
        expected = tmp_sessions / "acme-corp" / "staff-engineer" / "summary.md"
        assert path == expected

    def test_find_latest(self, tmp_sessions):
        store = SessionStore(tmp_sessions)
        role_dir = tmp_sessions / "acme-corp" / "staff-engineer"
        role_dir.mkdir(parents=True)

        (role_dir / "2026-04-30_match.yaml").write_text("id: a\nskill: match\nstarted_at: x\n")
        (role_dir / "2026-05-07_match.yaml").write_text("id: b\nskill: match\nstarted_at: x\n")
        (role_dir / "2026-05-01_tailor.yaml").write_text("id: c\nskill: tailor\nstarted_at: x\n")

        latest = store.find_latest("acme-corp", "staff-engineer", "match")
        assert latest is not None
        assert latest.name == "2026-05-07_match.yaml"

    def test_find_latest_no_dir(self, tmp_sessions):
        store = SessionStore(tmp_sessions)
        assert store.find_latest("nonexistent", "role", "match") is None

    def test_find_latest_no_match(self, tmp_sessions):
        store = SessionStore(tmp_sessions)
        role_dir = tmp_sessions / "acme-corp" / "staff-engineer"
        role_dir.mkdir(parents=True)
        (role_dir / "2026-05-01_tailor.yaml").write_text("id: a\nskill: tailor\nstarted_at: x\n")

        assert store.find_latest("acme-corp", "staff-engineer", "match") is None
