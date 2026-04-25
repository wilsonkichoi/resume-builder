"""Render ResumeIR to a styled HTML page via Jinja2 template."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from resume_builder.models.resume import ResumeIR

_TEMPLATE_DIR = Path(__file__).parent / "templates"


def _parse_skill_items(items: str) -> list[str]:
    """Split a SkillCategory.items string into individual pill labels.

    Parsing rules:
    - Cloud providers (AWS, GCP, Azure): expand sub-items and prepend the
      provider name as a prefix.
          "AWS (SageMaker, S3)" → ["AWS SageMaker", "AWS S3"]
    - Platform namespaces whose sub-items are distinct product names: expand
      the sub-items without a prefix.
          "SageMaker (Model Registry, Inference Recommender)" →
          ["Model Registry", "Inference Recommender"]
    - Umbrella brands where the parenthesized text is merely explanatory:
      keep the parent as a single pill, drop the sub-items.
          "ELK Stack (Elasticsearch, Logstash, Kibana)" → ["ELK Stack"]
    - Flat items: pass through as-is.
          "MSSQL, Cassandra" → ["MSSQL", "Cassandra"]
    """
    pills: list[str] = []

    # Match: "prefix (sub1, sub2)" or standalone item
    pattern = re.compile(
        r"([^,(]+?)"          # prefix (non-greedy, no commas/parens)
        r"\s*\(([^)]+)\)"     # parenthesized sub-items
        r"|"                  # OR
        r"([^,]+)"            # standalone item (no commas)
    )

    # Cloud providers: expand sub-items WITH prefix
    _cloud_prefixes = {"AWS", "GCP", "Azure"}
    # Platform namespaces: expand sub-items WITHOUT prefix
    _expand_prefixes = {"SageMaker"}

    for match in pattern.finditer(items):
        if match.group(1) is not None:
            prefix = match.group(1).strip()
            sub_items = [s.strip() for s in match.group(2).split(",")]

            if prefix in _cloud_prefixes:
                for sub in sub_items:
                    if sub:
                        pills.append(f"{prefix} {sub}")
            elif prefix in _expand_prefixes:
                for sub in sub_items:
                    if sub:
                        pills.append(sub)
            else:
                # Umbrella brand — keep parent as single pill
                pills.append(prefix)
        else:
            standalone = match.group(3).strip()
            if standalone:
                pills.append(standalone)

    return pills


def render_html(ir: ResumeIR) -> str:
    """Render the resume IR to a full HTML page.

    Parameters
    ----------
    ir:
        Populated ``ResumeIR`` model containing all resume data.

    Returns
    -------
    str
        Complete HTML document as a string.
    """
    env = Environment(
        loader=FileSystemLoader(str(_TEMPLATE_DIR)),
        autoescape=True,        # Escape user data (& → &amp; etc.)
        keep_trailing_newline=True,
    )
    env.globals["parse_skill_items"] = _parse_skill_items

    template = env.get_template("resume.html.j2")
    return template.render(
        ir=ir,
        current_year=datetime.now().year,
    )
