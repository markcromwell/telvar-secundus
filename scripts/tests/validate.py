#!/usr/bin/env python3
"""
Structural acceptance checks for the Telvar Secundus Godot project (Phase 2564).

Text-parses the repo — no Godot runtime. Run from repository root:

    python3 scripts/tests/validate.py

Exits 0 when all checks pass; exits 1 with a descriptive message on first failure.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def _repo_root() -> Path:
    """This file lives at scripts/tests/validate.py relative to repo root."""
    return Path(__file__).resolve().parents[2]


def _fail(message: str) -> None:
    print(f"validate.py: FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def _read_text(path: Path, label: str) -> str:
    if not path.is_file():
        _fail(f"Missing required file ({label}): {path}")
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        _fail(f"Could not read {path}: {exc}")


def main() -> None:
    root = _repo_root()

    quest_json = root / "assets" / "quests" / "merchants_delivery.json"
    raw_quest = _read_text(quest_json, "quest data")
    try:
        quest_data = json.loads(raw_quest)
    except json.JSONDecodeError as exc:
        _fail(f"{quest_json} is not valid JSON: {exc}")
    if not isinstance(quest_data, dict):
        _fail(f"{quest_json} root must be a JSON object, got {type(quest_data).__name__}")
    for key in ("id", "title", "objectives"):
        if key not in quest_data:
            _fail(f"{quest_json} missing required top-level key: {key!r}")
    if not isinstance(quest_data["objectives"], list):
        _fail(f'{quest_json}: "objectives" must be a JSON array')

    project = root / "project.godot"
    raw_project = _read_text(project, "project.godot")
    for needle in ("QuestManager", "LoreManager", "open_journal"):
        if needle not in raw_project:
            _fail(f"{project} must contain the substring {needle!r}")

    journal = root / "scenes" / "journal_ui.tscn"
    raw_journal = _read_text(journal, "journal scene")
    for needle in ("TabContainer", '"Active"', '"Done"', '"Lore"'):
        if needle not in raw_journal:
            _fail(f"{journal} must contain the substring {needle!r}")

    hud = root / "scenes" / "hud.tscn"
    raw_hud = _read_text(hud, "HUD scene")
    for needle in ("CanvasLayer", "Timer"):
        if needle not in raw_hud:
            _fail(f"{hud} must contain the substring {needle!r}")

    print("validate.py: all structural checks passed.")
    sys.exit(0)


if __name__ == "__main__":
    main()
