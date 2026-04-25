from __future__ import annotations

from pydantic import BaseModel


class Provenance(BaseModel):
    source: str = "manual"
    artifacts: list[str] = []
    verified: bool = True


class Header(BaseModel):
    name: str
    title: str
    location: str
    email: str
    linkedin: str
    github: str


class SummaryBullet(BaseModel):
    label: str
    text: str
    provenance: Provenance = Provenance()


class Summary(BaseModel):
    paragraph: str
    bullets: list[SummaryBullet] = []
    provenance: Provenance = Provenance()


class SkillCategory(BaseModel):
    category: str
    items: str
    provenance: Provenance = Provenance()


class Bullet(BaseModel):
    label: str | None = None
    text: str
    technologies: list[str] = []
    metrics: list[str] = []
    provenance: Provenance = Provenance()


class Role(BaseModel):
    title: str
    dates: str
    description: str | None = None
    bullets: list[Bullet] = []


class Company(BaseModel):
    company: str
    location: str
    description: str | None = None
    dates: str
    roles: list[Role] = []


class Project(BaseModel):
    name: str
    url: str
    description: str
    technologies: list[str] = []
    provenance: Provenance = Provenance()


class Education(BaseModel):
    degree: str
    institution: str


class ResumeIR(BaseModel):
    header: Header
    summary: Summary
    skills: list[SkillCategory] = []
    experience: list[Company] = []
    projects: list[Project] = []
    education: Education
