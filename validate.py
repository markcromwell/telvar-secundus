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

# Godot 4 text scene invariants shared by all enemy PackedScenes (Enemy extends Node2D).
_ENEMY_SCENE_BASE_MARKERS: list[str] = [
    "[gd_scene",
    "format=3",
    '[ext_resource type="Script" path="res://scripts/enemy/enemy.gd"',
    'type="Node2D"',
    "script = ExtResource(",
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
        "SPELL_FIRE_DART",
        '"max_hp": 28',
        '"atk": 6',
        '"max_hp": 16',
        '"atk": 3',
        '"spells": [SPELL_FIRE_DART]',
        '"max_hp": 20',
        '"atk": 5',
        '"physical_immune": true',
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
    "scenes/enemies/rookery_thug.tscn": _ENEMY_SCENE_BASE_MARKERS
    + [
        'definition_id = "rookery_thug"',
    ],
    "scenes/enemies/corrupted_apprentice.tscn": _ENEMY_SCENE_BASE_MARKERS
    + [
        'definition_id = "corrupted_apprentice"',
    ],
    "scenes/enemies/shade.tscn": _ENEMY_SCENE_BASE_MARKERS
    + [
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
    print("Validation OK: enemy scripts, stats markers, and scene structure checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
