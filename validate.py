#!/usr/bin/env python3
"""Text-only structural validation for the Godot project (no Godot runtime).

Exits 0 on success; prints descriptive errors and exits non-zero on failure.
Uses only the Python standard library.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent

# GDScript sources required for the quest system (paths relative to repo root).
REQUIRED_GDSCRIPT_FILES: tuple[str, ...] = (
    "scripts/quest_manager.gd",
    "scripts/quest_journal.gd",
)

QUEST_MANAGER_RELATIVE = "scripts/quest_manager.gd"
QUEST_MANAGER_TOKENS: tuple[str, ...] = (
    "start_quest",
    "complete_objective",
    "is_complete",
    "quest_updated",
    "objective_completed",
    "get_progress",
)

QUEST_JSON_FILES: tuple[str, ...] = (
    "assets/quests/merchants_delivery.json",
    "assets/quests/test_of_fire.json",
)

PROJECT_GODOT = "project.godot"
QUEST_JOURNAL_SCENE = "scenes/quest_journal.tscn"


def _fail(message: str) -> None:
    print(message, file=sys.stderr)
    sys.exit(1)


def _check_required_gdscripts() -> None:
    for rel in REQUIRED_GDSCRIPT_FILES:
        path = REPO_ROOT / rel
        if not path.is_file():
            _fail(f"Missing required file: {rel}")


def _check_quest_manager_tokens() -> None:
    path = REPO_ROOT / QUEST_MANAGER_RELATIVE
    text = path.read_text(encoding="utf-8")
    missing = [tok for tok in QUEST_MANAGER_TOKENS if tok not in text]
    if missing:
        _fail(
            f"{QUEST_MANAGER_RELATIVE}: missing required tokens: {', '.join(missing)}"
        )


def _validate_quest_json(rel_path: str) -> None:
    path = REPO_ROOT / rel_path
    if not path.is_file():
        _fail(f"Missing required file: {rel_path}")
    raw = path.read_text(encoding="utf-8")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        _fail(f"Invalid JSON in {rel_path}: {exc}")
    if not isinstance(data, dict):
        _fail(f"JSON structure error in {rel_path}: root must be a JSON object")
    for key in ("id", "title", "objectives"):
        if key not in data:
            _fail(
                f"JSON structure error in {rel_path}: missing required key {key!r}"
            )
    objectives = data["objectives"]
    if not isinstance(objectives, list):
        _fail(
            f"JSON structure error in {rel_path}: "
            f"key 'objectives' must be a JSON array, got {type(objectives).__name__}"
        )
    if len(objectives) == 0:
        _fail(
            f"JSON structure error in {rel_path}: "
            "key 'objectives' must be a non-empty array"
        )


def _check_project_autoload() -> None:
    path = REPO_ROOT / PROJECT_GODOT
    if not path.is_file():
        _fail(f"Missing required file: {PROJECT_GODOT}")
    text = path.read_text(encoding="utf-8")
    in_autoload = False
    found = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            in_autoload = stripped.lower() == "[autoload]"
            continue
        if not in_autoload or not stripped or stripped.startswith(";"):
            continue
        if "QuestManager" in line:
            found = True
            break
    if not found:
        _fail(
            f"{PROJECT_GODOT}: no autoload line containing 'QuestManager' "
            "under [autoload]"
        )


def _check_quest_journal_scene() -> None:
    rel = QUEST_JOURNAL_SCENE
    path = REPO_ROOT / rel
    if not path.is_file():
        _fail(f"Missing required file: {rel}")
    text = path.read_text(encoding="utf-8")
    if "TabContainer" not in text:
        _fail(f"{rel}: expected scene text to contain 'TabContainer'")


def main() -> None:
    _check_required_gdscripts()
    _check_quest_manager_tokens()
    for rel in QUEST_JSON_FILES:
        _validate_quest_json(rel)
    _check_project_autoload()
    _check_quest_journal_scene()
    print("All checks passed.")
    sys.exit(0)


if __name__ == "__main__":
    main()
