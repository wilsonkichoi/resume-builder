from __future__ import annotations

from pydantic import BaseModel


class SourcedFact(BaseModel):
    value: str
    source: str
    is_inference: bool = False
    confidence: str = "high"


class CompanyBasics(BaseModel):
    name: str
    slug: str
    industry: str | None = None
    size: SourcedFact | None = None
    stage: SourcedFact | None = None
    location: SourcedFact | None = None
    funding: SourcedFact | None = None
    website: str | None = None


class MissionVision(BaseModel):
    mission: SourcedFact | None = None
    vision: SourcedFact | None = None
    values: list[SourcedFact] = []


class ProductService(BaseModel):
    name: str
    description: str
    target_customer: str | None = None
    source: str


class PainPoint(BaseModel):
    description: str
    evidence: list[str] = []
    is_inference: bool = False
    severity: str = "medium"


class TechStackItem(BaseModel):
    technology: str
    context: str
    source: str
    confidence: str = "high"


class CultureSignal(BaseModel):
    signal: str
    sentiment: str
    source: str
    is_inference: bool = False


class NewsItem(BaseModel):
    headline: str
    date: str | None = None
    summary: str
    source: str
    relevance: str


class GrowthSignal(BaseModel):
    signal: str
    evidence: str
    source: str


class KeyPerson(BaseModel):
    name: str
    title: str
    relevance: str
    source: str


class CompanyProfile(BaseModel):
    basics: CompanyBasics
    mission_vision: MissionVision = MissionVision()
    products_services: list[ProductService] = []
    pain_points: list[PainPoint] = []
    tech_stack: list[TechStackItem] = []
    culture_signals: list[CultureSignal] = []
    recent_news: list[NewsItem] = []
    growth_signals: list[GrowthSignal] = []
    key_people: list[KeyPerson] = []
    sources: list[str] = []
    researched_at: str
    last_updated: str | None = None
