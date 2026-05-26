#!/usr/bin/env python3
"""Structural validation for QuestManager (stdlib only; no Godot binary).

Checks:
  1) scripts/quest_manager.gd exists and declares required signals/functions
  2) project.godot registers QuestManager as an autoload
  3) Every *.json under assets/quests/ parses as JSON with id, title, objectives (array)

Exit 0 on full pass; print descriptive errors to stderr and exit 1 on any failure.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
QUEST_MANAGER = REPO_ROOT / "scripts" / "quest_manager.gd"
PROJECT_GODOT = REPO_ROOT / "project.godot"
QUESTS_DIR = REPO_ROOT / "assets" / "quests"

# Presence checks: GDScript may add types / return annotations after these tokens.
QUEST_MANAGER_REQUIREMENTS: tuple[str, ...] = (
    "signal quest_updated",
    "signal objective_completed",
    "var quests",
    "func start_quest",
    "func complete_objective",
    "func is_complete",
)

QUEST_MANAGER_AUTOLOAD_RE = re.compile(
    r"^QuestManager\s*=\s*\"\*res://scripts/quest_manager\.gd\"\s*$",
    re.MULTILINE,
)


def _collect_errors() -> list[str]:
    errors: list[str] = []

    if not QUEST_MANAGER.is_file():
        errors.append(f"Missing required file: {QUEST_MANAGER.relative_to(REPO_ROOT)}")
    else:
        qm_text = QUEST_MANAGER.read_text(encoding="utf-8").lstrip("\ufeff")
        for needle in QUEST_MANAGER_REQUIREMENTS:
            if needle not in qm_text:
                errors.append(
                    "scripts/quest_manager.gd is missing a required declaration "
                    f"(expected a line containing {needle!r})."
                )

    if not PROJECT_GODOT.is_file():
        errors.append(f"Missing required file: {PROJECT_GODOT.relative_to(REPO_ROOT)}")
    else:
        pg_text = PROJECT_GODOT.read_text(encoding="utf-8").lstrip("\ufeff")
        if not QUEST_MANAGER_AUTOLOAD_RE.search(pg_text):
            errors.append(
                'project.godot must contain autoload line '
                'QuestManager="*res://scripts/quest_manager.gd" '
                "(Godot 4 singleton path with leading * on res://)."
            )

    if not QUESTS_DIR.is_dir():
        errors.append(
            f"Missing quests directory: {QUESTS_DIR.relative_to(REPO_ROOT)} "
            "(expected JSON quest definitions)."
        )
    else:
        json_files = sorted(QUESTS_DIR.glob("*.json"))
        for path in json_files:
            rel = path.relative_to(REPO_ROOT)
            try:
                data = json.loads(path.read_text(encoding="utf-8").lstrip("\ufeff"))
            except json.JSONDecodeError as exc:
                errors.append(f"Invalid JSON in {rel}: {exc}")
                continue
            if not isinstance(data, dict):
                errors.append(
                    f"Quest JSON root must be a JSON object in {rel}, got {type(data).__name__}."
                )
                continue
            if "id" not in data:
                errors.append(f"Quest JSON in {rel} is missing required top-level field 'id'.")
            if "title" not in data:
                errors.append(f"Quest JSON in {rel} is missing required top-level field 'title'.")
            if "objectives" not in data:
                errors.append(f"Quest JSON in {rel} is missing required top-level field 'objectives'.")
            elif not isinstance(data["objectives"], list):
                errors.append(
                    f"Quest JSON in {rel}: 'objectives' must be a JSON array, "
                    f"got {type(data['objectives']).__name__}."
                )

    return errors


def main() -> int:
    failures = _collect_errors()
    if failures:
        for msg in failures:
            print(msg, file=sys.stderr)
        return 1
    print("validate.py: all checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
