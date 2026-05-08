"""Migrate flat session files and tailored output to hierarchical structure.

Reorganizes:
  knowledge/sessions/{skill}_{date}_{company}_{role}.yaml
    → knowledge/sessions/{company}/{role}/{date}_{skill}.yaml

  knowledge/sessions/research_{date}_{company}.yaml
    → knowledge/sessions/{company}/{date}_research.yaml

  knowledge/companies/{slug}.yaml
    → knowledge/sessions/{slug}/company.yaml

  tailored/{date}_{company}_{role}/
    → knowledge/sessions/{company}/{role}/tailored/

Usage:
  uv run python scripts/migrate_sessions.py --project-dir ../wchoi-resume
  uv run python scripts/migrate_sessions.py --project-dir ../wchoi-resume --dry-run
"""

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path

KNOWN_SKILLS = frozenset(
    [
        "match",
        "qualify",
        "tailor",
        "score",
        "review",
        "cover-letter",
        "apply",
        "ingest",
    ]
)

ROLE_SKILL_PATTERN = re.compile(
    r"^(?P<skill>"
    + "|".join(sorted(KNOWN_SKILLS, key=len, reverse=True))
    + r")_(?P<date>\d{4}-\d{2}-\d{2})_(?P<company>[^_]+)_(?P<role>.+)\.yaml$"
)

# Alternate format: {date}_{skill}_{company}_{role}.yaml
DATE_FIRST_PATTERN = re.compile(
    r"^(?P<date>\d{4}-\d{2}-\d{2})_(?P<skill>"
    + "|".join(sorted(KNOWN_SKILLS, key=len, reverse=True))
    + r")_(?P<company>[^_]+)_(?P<role>.+)\.yaml$"
)

RESEARCH_PATTERN = re.compile(
    r"^(?:research_|\d{4}-\d{2}-\d{2}_research_)(?P<date>\d{4}-\d{2}-\d{2})?_?(?P<company>.+)\.yaml$"
)

RESEARCH_ALT_PATTERN = re.compile(
    r"^(?P<date>\d{4}-\d{2}-\d{2})_research_(?P<company>.+)\.yaml$"
)

RESEARCH_STD_PATTERN = re.compile(
    r"^research_(?P<date>\d{4}-\d{2}-\d{2})_(?P<company>.+)\.yaml$"
)

TAILORED_DIR_PATTERN = re.compile(
    r"^(?P<date>\d{4}-\d{2}-\d{2})_(?P<company>[^_]+)_(?P<role>.+)$"
)


def parse_session_filename(name: str) -> dict | None:
    m = ROLE_SKILL_PATTERN.match(name)
    if m:
        return {
            "type": "role_session",
            "skill": m.group("skill"),
            "date": m.group("date"),
            "company": m.group("company"),
            "role": m.group("role"),
        }

    m = DATE_FIRST_PATTERN.match(name)
    if m:
        return {
            "type": "role_session",
            "skill": m.group("skill"),
            "date": m.group("date"),
            "company": m.group("company"),
            "role": m.group("role"),
        }

    m = RESEARCH_STD_PATTERN.match(name)
    if m:
        return {
            "type": "research",
            "skill": "research",
            "date": m.group("date"),
            "company": m.group("company"),
        }

    m = RESEARCH_ALT_PATTERN.match(name)
    if m:
        return {
            "type": "research",
            "skill": "research",
            "date": m.group("date"),
            "company": m.group("company"),
        }

    return None


def migrate(project_dir: Path, *, dry_run: bool = False) -> list[tuple[Path, Path]]:
    moves: list[tuple[Path, Path]] = []
    sessions_dir = project_dir / "knowledge" / "sessions"
    companies_dir = project_dir / "knowledge" / "companies"
    tailored_dir = project_dir / "tailored"

    # 1. Migrate flat session files
    if sessions_dir.is_dir():
        for f in sorted(sessions_dir.glob("*.yaml")):
            if f.name == ".gitkeep":
                continue
            parsed = parse_session_filename(f.name)
            if not parsed:
                print(f"  SKIP (unrecognized): {f.name}")
                continue

            if parsed["type"] == "research":
                dest = sessions_dir / parsed["company"] / f"{parsed['date']}_research.yaml"
            else:
                dest = (
                    sessions_dir
                    / parsed["company"]
                    / parsed["role"]
                    / f"{parsed['date']}_{parsed['skill']}.yaml"
                )

            moves.append((f, dest))

    # 2. Migrate company profiles
    if companies_dir.is_dir():
        for f in sorted(companies_dir.glob("*.yaml")):
            slug = f.stem
            dest = sessions_dir / slug / "company.yaml"
            moves.append((f, dest))

    # 3. Migrate tailored directories
    if tailored_dir.is_dir():
        for d in sorted(tailored_dir.iterdir()):
            if not d.is_dir():
                continue
            m = TAILORED_DIR_PATTERN.match(d.name)
            if not m:
                print(f"  SKIP (unrecognized tailored dir): {d.name}")
                continue
            company = m.group("company")
            role = m.group("role")
            dest_dir = sessions_dir / company / role / "tailored"

            for f in sorted(d.rglob("*")):
                if f.is_file():
                    rel = f.relative_to(d)
                    moves.append((f, dest_dir / rel))

    # Execute moves
    print(f"\n{'DRY RUN — ' if dry_run else ''}Migration plan ({len(moves)} files):\n")
    for src, dest in moves:
        src_rel = src.relative_to(project_dir)
        dest_rel = dest.relative_to(project_dir)
        print(f"  {src_rel}\n    → {dest_rel}\n")
        if not dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dest))

    if not dry_run:
        # Clean up empty directories
        if tailored_dir.is_dir():
            for d in sorted(tailored_dir.rglob("*"), reverse=True):
                if d.is_dir() and not any(d.iterdir()):
                    d.rmdir()
            if not any(tailored_dir.iterdir()):
                tailored_dir.rmdir()
                print(f"\n  Removed empty directory: tailored/")

        if companies_dir.is_dir():
            if not any(companies_dir.iterdir()):
                companies_dir.rmdir()
                print(f"  Removed empty directory: knowledge/companies/")

    print(f"\n{'Would move' if dry_run else 'Moved'} {len(moves)} files.")
    return moves


def main() -> None:
    parser = argparse.ArgumentParser(description="Migrate sessions to hierarchical structure")
    parser.add_argument(
        "--project-dir",
        type=Path,
        default=Path("."),
        help="Path to the resume project (default: current directory)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be moved without making changes",
    )
    args = parser.parse_args()

    project_dir = args.project_dir.resolve()
    if not (project_dir / "knowledge" / "sessions").is_dir():
        print(f"Error: {project_dir}/knowledge/sessions/ does not exist.")
        raise SystemExit(1)

    migrate(project_dir, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
