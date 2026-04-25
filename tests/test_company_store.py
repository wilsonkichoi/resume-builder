import pytest

from resume_builder.knowledge.company import CompanyStore, slugify
from resume_builder.models.company import (
    CompanyBasics,
    CompanyProfile,
    PainPoint,
    SourcedFact,
    TechStackItem,
)


@pytest.fixture()
def tmp_companies(tmp_path):
    companies_dir = tmp_path / "companies"
    companies_dir.mkdir()
    return companies_dir


def _make_profile(name: str = "Acme Corp", slug: str = "acme-corp") -> CompanyProfile:
    return CompanyProfile(
        basics=CompanyBasics(
            name=name,
            slug=slug,
            industry="SaaS",
            size=SourcedFact(value="200-500", source="https://acme.example/about"),
        ),
        pain_points=[
            PainPoint(
                description="Scaling bottleneck in data pipeline",
                evidence=["https://acme.example/careers/data-eng"],
                is_inference=True,
                severity="high",
            ),
        ],
        tech_stack=[
            TechStackItem(
                technology="Python",
                context="Backend services",
                source="https://acme.example/careers",
            ),
        ],
        sources=["https://acme.example/about", "https://acme.example/careers"],
        researched_at="2025-06-15T10:00:00Z",
    )


class TestSlugify:
    def test_basic(self):
        assert slugify("Acme Corp") == "acme-corp"

    def test_punctuation(self):
        assert slugify("Acme Corp, Inc.") == "acme-corp-inc"

    def test_unicode(self):
        assert slugify("Ünïcödé Labs") == "unicode-labs"

    def test_extra_spaces(self):
        assert slugify("  Lots   Of   Spaces  ") == "lots-of-spaces"

    def test_already_slug(self):
        assert slugify("already-a-slug") == "already-a-slug"


class TestCompanyStore:
    def test_save_and_load(self, tmp_companies):
        store = CompanyStore(tmp_companies)
        profile = _make_profile()
        path = store.save(profile)

        assert path.exists()
        assert path.name == "acme-corp.yaml"

        loaded = store.load("acme-corp")
        assert loaded.basics.name == "Acme Corp"
        assert loaded.basics.size.value == "200-500"
        assert len(loaded.pain_points) == 1
        assert loaded.pain_points[0].is_inference is True

    def test_find_by_name(self, tmp_companies):
        store = CompanyStore(tmp_companies)
        store.save(_make_profile())

        found = store.find_by_name("Acme Corp")
        assert found is not None
        assert found.basics.slug == "acme-corp"

        found_lower = store.find_by_name("acme corp")
        assert found_lower is not None

        not_found = store.find_by_name("Nonexistent")
        assert not_found is None

    def test_list_companies(self, tmp_companies):
        store = CompanyStore(tmp_companies)
        store.save(_make_profile("Acme Corp", "acme-corp"))
        store.save(_make_profile("Globex Inc", "globex-inc"))

        companies = store.list_companies()
        assert len(companies) == 2
        names = {c.basics.name for c in companies}
        assert names == {"Acme Corp", "Globex Inc"}

    def test_exists(self, tmp_companies):
        store = CompanyStore(tmp_companies)
        store.save(_make_profile())

        assert store.exists("acme-corp") is True
        assert store.exists("nonexistent") is False

    def test_delete(self, tmp_companies):
        store = CompanyStore(tmp_companies)
        store.save(_make_profile())

        assert store.delete("acme-corp") is True
        assert store.exists("acme-corp") is False
        assert store.delete("acme-corp") is False

    def test_mkdir_on_init(self, tmp_path):
        companies_dir = tmp_path / "new" / "nested" / "companies"
        store = CompanyStore(companies_dir)
        assert companies_dir.exists()

    def test_overwrite_on_save(self, tmp_companies):
        store = CompanyStore(tmp_companies)
        profile = _make_profile()
        store.save(profile)

        profile.pain_points.append(
            PainPoint(
                description="New pain point",
                evidence=["https://acme.example/blog"],
                severity="medium",
            )
        )
        store.save(profile)

        loaded = store.load("acme-corp")
        assert len(loaded.pain_points) == 2
