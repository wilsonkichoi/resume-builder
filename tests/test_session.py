from pathlib import Path

import pytest

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
