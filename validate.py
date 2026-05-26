#!/usr/bin/env python3
"""
Structural acceptance gate for Telvar Secundus (Code Forge / test_cmd_unit).

Validates JSON, GDScript tokens, .tscn structure, project.godot autoloads, and
PNG magic bytes. Exits 0 only when all checks pass; otherwise prints FAIL lines
and exits 1.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent


def _err(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)


def _require_file(path: Path, label: str) -> bool:
    if not path.is_file():
        _err(f"Missing {label}: {path.relative_to(REPO)}")
        return False
    return True


def _check_quest_json(path: Path) -> bool:
    if not _require_file(path, "quest definition"):
        return False
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        _err(f"Invalid JSON in {path.relative_to(REPO)}: {e}")
        return False
    if not isinstance(data, dict):
        _err(f"{path.relative_to(REPO)}: root must be a JSON object")
        return False
    required = ("id", "title", "giver", "status")
    ok = True
    for key in required:
        if key not in data:
            _err(f"{path.relative_to(REPO)}: missing required key {key!r}")
            ok = False
    return ok


def _check_sabatha_dialogue(path: Path) -> bool:
    if not _require_file(path, "dialogue file"):
        return False
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        _err(f"Invalid JSON in {path.relative_to(REPO)}: {e}")
        return False
    if not isinstance(data, list):
        _err(f"{path.relative_to(REPO)}: root must be a JSON array of nodes")
        return False
    for item in data:
        if isinstance(item, dict) and item.get("action") == "assign_quest":
            return True
    _err(
        f"{path.relative_to(REPO)}: no dialogue node with "
        '"action": "assign_quest" (assign_quest action node required)'
    )
    return False


def _check_gdscript_tokens(path: Path, label: str, tokens: tuple[str, ...]) -> bool:
    if not _require_file(path, label):
        return False
    text = path.read_text(encoding="utf-8")
    ok = True
    for token in tokens:
        if token not in text:
            _err(f"{path.relative_to(REPO)}: required substring not found: {token!r}")
            ok = False
    return ok


def _check_sabatha_tscn(path: Path) -> bool:
    if not _require_file(path, "Sabatha scene"):
        return False
    text = path.read_text(encoding="utf-8")
    required = (
        "StaticBody2D",
        "AnimatedSprite2D",
        "Area2D",
        'dialogue_id = "sabatha"',
    )
    ok = True
    for token in required:
        if token not in text:
            _err(f"{path.relative_to(REPO)}: required substring not found: {token!r}")
            ok = False
    return ok


def _check_project_autoloads(path: Path) -> bool:
    if not _require_file(path, "project.godot"):
        return False
    text = path.read_text(encoding="utf-8")
    ok = True
    if "QuestManager" not in text:
        _err(f"{path.relative_to(REPO)}: QuestManager autoload entry not found")
        ok = False
    if "DialogueManager" not in text:
        _err(f"{path.relative_to(REPO)}: DialogueManager autoload entry not found")
        ok = False
    return ok


def _check_png_magic(path: Path) -> bool:
    if not _require_file(path, "portrait PNG"):
        return False
    data = path.read_bytes()
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        _err(
            f"{path.relative_to(REPO)}: file does not start with PNG magic bytes "
            r"(expected \x89PNG\r\n\x1a\n)"
        )
        return False
    return True


def main() -> int:
    checks = [
        _check_quest_json(REPO / "assets/quests/merchants_delivery.json"),
        _check_sabatha_dialogue(REPO / "assets/dialogue/sabatha.json"),
        _check_gdscript_tokens(
            REPO / "scripts/QuestManager.gd",
            "QuestManager script",
            ("func assign_quest", "func get_journal"),
        ),
        _check_gdscript_tokens(
            REPO / "scripts/DialogueManager.gd",
            "DialogueManager script",
            ("func show_dialogue", "func set_flag", "func get_flag"),
        ),
        _check_sabatha_tscn(REPO / "scenes/npcs/Sabatha.tscn"),
        _check_project_autoloads(REPO / "project.godot"),
        _check_png_magic(REPO / "assets/portraits/sabatha.png"),
    ]
    if not all(checks):
        return 1
    print("validate.py: all structural checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
