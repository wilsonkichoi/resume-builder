from __future__ import annotations

from pathlib import Path

import yaml

from resume_builder.models.resume import ResumeIR


def parse_resume(path: str | Path) -> ResumeIR:
    path = Path(path)
    with path.open() as f:
        data = yaml.safe_load(f)
    return ResumeIR.model_validate(data)
