"""Enemy module presence checks (mirrors validate.py markers for pytest CI)."""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "scripts/enemy/enemy.gd",
    "scripts/enemy/enemy_ai.gd",
    "scripts/enemy/enemy_definitions.gd",
]

FILE_MARKERS: dict[str, list[str]] = {
    "scripts/enemy/enemy_definitions.gd": [
        "Rookery Thug",
        "Corrupted Apprentice",
        "Shade",
        "fire_dart",
        "physical_immune",
    ],
    "scripts/enemy/enemy.gd": [
        "class_name Enemy",
        "No effect",
        "apply_incoming_damage",
    ],
    "scripts/enemy/enemy_ai.gd": [
        "class_name EnemyAI",
        "choose_action",
    ],
}


@pytest.mark.parametrize("rel", REQUIRED_FILES)
def test_enemy_script_exists(rel: str) -> None:
    assert (REPO_ROOT / rel).is_file()


@pytest.mark.parametrize("rel", REQUIRED_FILES)
def test_enemy_script_markers(rel: str) -> None:
    path = REPO_ROOT / rel
    text = path.read_text(encoding="utf-8")
    for marker in FILE_MARKERS[rel]:
        assert marker in text
