#!/usr/bin/env python3
"""Structural validation for Telvar Secundus (Godot 4.x) — text checks only, no Godot binary."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent

REQUIRED_FILES: list[str] = [
    "scripts/enemy/enemy.gd",
    "scripts/enemy/enemy_ai.gd",
    "scripts/enemy/enemy_definitions.gd",
    "scenes/enemies/rookery_thug.tscn",
    "scenes/enemies/corrupted_apprentice.tscn",
    "scenes/enemies/shade.tscn",
]

# Markers that prove the bootstrap enemy spec is present (names + mechanics).
FILE_MARKERS: dict[str, list[str]] = {
    "scripts/enemy/enemy_definitions.gd": [
        "Rookery Thug",
        "Corrupted Apprentice",
        "Shade",
        "fire_dart",
        "physical_immune",
        "ENEMY_ROOKERY_THUG",
        "ENEMY_CORRUPTED_APPRENTICE",
        "ENEMY_SHADE",
    ],
    "scripts/enemy/enemy.gd": [
        "class_name Enemy",
        "MSG_NO_EFFECT",
        "apply_incoming_damage",
        "can_cast",
    ],
    "scripts/enemy/enemy_ai.gd": [
        "class_name EnemyAI",
        "choose_action",
        "ACTION_CAST",
        "ACTION_ATTACK",
    ],
    "scenes/enemies/rookery_thug.tscn": [
        "res://scripts/enemy/enemy.gd",
        'definition_id = "rookery_thug"',
    ],
    "scenes/enemies/corrupted_apprentice.tscn": [
        "res://scripts/enemy/enemy.gd",
        'definition_id = "corrupted_apprentice"',
    ],
    "scenes/enemies/shade.tscn": [
        "res://scripts/enemy/enemy.gd",
        'definition_id = "shade"',
    ],
}


def _collect_errors() -> list[str]:
    errors: list[str] = []
    for rel in REQUIRED_FILES:
        path = REPO_ROOT / rel
        if not path.is_file():
            errors.append(f"Missing required file: {rel}")
            continue
        text = path.read_text(encoding="utf-8")
        for marker in FILE_MARKERS.get(rel, []):
            if marker not in text:
                errors.append(f"{rel}: missing marker {marker!r}")
    return errors


def main() -> int:
    errors = _collect_errors()
    if errors:
        for e in errors:
            print("FAIL:", e)
        return 1
    print("Validation OK: enemy scripts and markers present.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
