import pytest
from pathlib import Path

from resume_builder.knowledge.achievements import Achievement, AchievementStore, PhrasingVariant


class TestAchievement:
    def test_add_variant(self):
        a = Achievement(bullet_label="Pipeline", company="TeleSign", role="MLOps")
        a.add_variant("Built CI/CD pipeline", session_id="s1", target_role="backend", score=80)
        a.add_variant("Designed ML deployment pipeline", session_id="s2", target_role="mlops", score=90)

        assert len(a.variants) == 2
        assert a.best_score == 90
        assert a.best_variant_index == 1

    def test_best_variant(self):
        a = Achievement(bullet_label="Pipeline", company="TeleSign", role="MLOps")
        a.add_variant("v1", session_id="s1", score=70)
        a.add_variant("v2", session_id="s2", score=90)
        a.add_variant("v3", session_id="s3", score=85)

        best = a.best_variant()
        assert best is not None
        assert best.text == "v2"

    def test_best_variant_empty(self):
        a = Achievement(bullet_label="Pipeline", company="TeleSign", role="MLOps")
        assert a.best_variant() is None

    def test_roundtrip(self):
        a = Achievement(bullet_label="Caching", company="TeleSign", role="Fraud Lead")
        a.add_variant("Reduced latency by 83%", session_id="s1", target_role="backend", score=85)

        data = a.to_dict()
        restored = Achievement.from_dict(data)
        assert restored.bullet_label == "Caching"
        assert len(restored.variants) == 1
        assert restored.best_score == 85


class TestAchievementStore:
    def test_create_and_save(self, tmp_path):
        path = tmp_path / "achievements.yaml"
        store = AchievementStore(path)
        store.record_variant(
            bullet_label="Pipeline",
            company="TeleSign",
            role="MLOps",
            text="Built ML pipeline",
            session_id="s1",
            target_role="mlops",
            score=85,
        )
        store.save()

        assert path.exists()

        reloaded = AchievementStore(path)
        assert len(reloaded.achievements) == 1
        assert reloaded.achievements[0].best_score == 85

    def test_get_or_create_deduplicates(self, tmp_path):
        store = AchievementStore(tmp_path / "achievements.yaml")
        a1 = store.get_or_create("Pipeline", "TeleSign", "MLOps")
        a2 = store.get_or_create("Pipeline", "TeleSign", "MLOps")
        assert a1 is a2
        assert len(store.achievements) == 1

    def test_best_variants_for_role(self, tmp_path):
        store = AchievementStore(tmp_path / "achievements.yaml")
        store.record_variant("Pipeline", "TeleSign", "MLOps", "v1 backend", "s1", "backend", 70)
        store.record_variant("Pipeline", "TeleSign", "MLOps", "v2 backend", "s2", "backend", 90)
        store.record_variant("Pipeline", "TeleSign", "MLOps", "v3 mlops", "s3", "mlops", 85)
        store.record_variant("Caching", "TeleSign", "Fraud", "v1 backend", "s1", "backend", 80)

        backend_bests = store.best_variants_for_role("backend")
        assert len(backend_bests) == 2
        texts = {v.text for _, v in backend_bests}
        assert "v2 backend" in texts
        assert "v1 backend" in texts

    def test_find_returns_none_for_missing(self, tmp_path):
        store = AchievementStore(tmp_path / "achievements.yaml")
        assert store.find("NonExistent", "Company", "Role") is None
