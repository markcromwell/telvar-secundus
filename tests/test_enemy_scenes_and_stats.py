"""Per-enemy PackedScene files and definition stat strings (text-level acceptance)."""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

ENEMY_SCENES: dict[str, list[str]] = {
    "scenes/enemies/rookery_thug.tscn": ['definition_id = "rookery_thug"'],
    "scenes/enemies/corrupted_apprentice.tscn": ['definition_id = "corrupted_apprentice"'],
    "scenes/enemies/shade.tscn": ['definition_id = "shade"'],
}

DEFINITIONS_PATH = REPO_ROOT / "scripts/enemy/enemy_definitions.gd"


@pytest.mark.parametrize("rel,markers", ENEMY_SCENES.items())
def test_enemy_scene_exists_with_definition(rel: str, markers: list[str]) -> None:
    path = REPO_ROOT / rel
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    assert "res://scripts/enemy/enemy.gd" in text
    for m in markers:
        assert m in text


def test_rookery_thug_stats_in_definitions() -> None:
    text = DEFINITIONS_PATH.read_text(encoding="utf-8")
    assert "ENEMY_ROOKERY_THUG" in text
    assert '"max_hp": 28' in text
    assert '"atk": 6' in text


def test_corrupted_apprentice_fire_dart_and_stats() -> None:
    text = DEFINITIONS_PATH.read_text(encoding="utf-8")
    assert "ENEMY_CORRUPTED_APPRENTICE" in text
    assert '"max_hp": 16' in text
    assert '"atk": 3' in text
    assert "SPELL_FIRE_DART" in text
    assert '"spells": [SPELL_FIRE_DART]' in text


def test_shade_physical_immunity_and_stats() -> None:
    text = DEFINITIONS_PATH.read_text(encoding="utf-8")
    assert "ENEMY_SHADE" in text
    assert '"max_hp": 20' in text
    assert '"atk": 5' in text
    assert '"physical_immune": true' in text
