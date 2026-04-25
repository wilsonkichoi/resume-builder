from resume_builder.models.company import (
    CompanyBasics,
    CompanyProfile,
    CultureSignal,
    GrowthSignal,
    KeyPerson,
    MissionVision,
    NewsItem,
    PainPoint,
    ProductService,
    SourcedFact,
    TechStackItem,
)


class TestSourcedFact:
    def test_defaults(self):
        fact = SourcedFact(value="500 employees", source="https://example.com/about")
        assert fact.is_inference is False
        assert fact.confidence == "high"

    def test_inference_flag(self):
        fact = SourcedFact(
            value="Likely moving to microservices",
            source="https://example.com/blog",
            is_inference=True,
            confidence="medium",
        )
        assert fact.is_inference is True
        assert fact.confidence == "medium"


class TestCompanyProfile:
    def test_minimal_profile(self):
        profile = CompanyProfile(
            basics=CompanyBasics(name="Acme Corp", slug="acme-corp"),
            researched_at="2025-06-15T10:00:00Z",
        )
        assert profile.basics.name == "Acme Corp"
        assert profile.pain_points == []
        assert profile.tech_stack == []
        assert profile.sources == []

    def test_full_profile(self):
        profile = CompanyProfile(
            basics=CompanyBasics(
                name="Acme Corp",
                slug="acme-corp",
                industry="SaaS",
                size=SourcedFact(value="200-500", source="https://acme.com/about"),
                stage=SourcedFact(value="Series B", source="https://crunchbase.example/acme"),
                location=SourcedFact(value="San Francisco, CA", source="https://acme.com/about"),
                website="https://acme.com",
            ),
            mission_vision=MissionVision(
                mission=SourcedFact(value="Make widgets better", source="https://acme.com/about"),
                values=[
                    SourcedFact(value="Move fast", source="https://acme.com/values"),
                ],
            ),
            products_services=[
                ProductService(
                    name="Widget Pro",
                    description="Enterprise widget management",
                    target_customer="Fortune 500",
                    source="https://acme.com/products",
                ),
            ],
            pain_points=[
                PainPoint(
                    description="Migrating from monolith to microservices",
                    evidence=["https://acme.com/blog/migration", "https://acme.com/careers/backend"],
                    is_inference=True,
                    severity="high",
                ),
            ],
            tech_stack=[
                TechStackItem(
                    technology="Python",
                    context="Backend services",
                    source="https://acme.com/careers/backend",
                ),
            ],
            culture_signals=[
                CultureSignal(
                    signal="Remote-first",
                    sentiment="positive",
                    source="https://glassdoor.example/acme",
                ),
            ],
            recent_news=[
                NewsItem(
                    headline="Acme raises $50M Series B",
                    date="2025-03-01",
                    summary="Funding to expand engineering team",
                    source="https://techcrunch.example/acme-series-b",
                    relevance="Active hiring, well-funded",
                ),
            ],
            growth_signals=[
                GrowthSignal(
                    signal="20 open engineering roles",
                    evidence="Careers page lists 20 positions",
                    source="https://acme.com/careers",
                ),
            ],
            key_people=[
                KeyPerson(
                    name="Jane Smith",
                    title="VP Engineering",
                    relevance="Likely hiring manager for senior roles",
                    source="https://linkedin.example/janesmith",
                ),
            ],
            sources=[
                "https://acme.com/about",
                "https://acme.com/careers/backend",
                "https://glassdoor.example/acme",
            ],
            researched_at="2025-06-15T10:00:00Z",
        )
        assert profile.basics.industry == "SaaS"
        assert len(profile.pain_points) == 1
        assert profile.pain_points[0].is_inference is True
        assert len(profile.sources) == 3

    def test_serialization_roundtrip(self):
        profile = CompanyProfile(
            basics=CompanyBasics(
                name="Globex Inc",
                slug="globex-inc",
                industry="FinTech",
                size=SourcedFact(value="1000+", source="https://globex.example/about"),
            ),
            pain_points=[
                PainPoint(
                    description="Legacy Java codebase needs modernization",
                    evidence=["https://globex.example/careers"],
                    is_inference=True,
                    severity="high",
                ),
            ],
            tech_stack=[
                TechStackItem(
                    technology="Java",
                    context="Core platform",
                    source="https://globex.example/careers",
                ),
                TechStackItem(
                    technology="Kubernetes",
                    context="Infrastructure migration in progress",
                    source="https://globex.example/blog/k8s",
                    confidence="medium",
                ),
            ],
            researched_at="2025-06-15T10:00:00Z",
        )

        data = profile.model_dump()
        restored = CompanyProfile.model_validate(data)

        assert restored.basics.name == "Globex Inc"
        assert restored.basics.size.value == "1000+"
        assert len(restored.tech_stack) == 2
        assert restored.tech_stack[1].confidence == "medium"
        assert restored.pain_points[0].is_inference is True

    def test_exclude_none_serialization(self):
        profile = CompanyProfile(
            basics=CompanyBasics(name="Minimal Co", slug="minimal-co"),
            researched_at="2025-06-15T10:00:00Z",
        )
        data = profile.model_dump(exclude_none=True)
        assert "industry" not in data["basics"]
        assert "size" not in data["basics"]
        assert "last_updated" not in data
