"""Static checks for SaveSystem autoload and SaveData fields (no Godot binary)."""

from __future__ import annotations

import pytest

from tests.test_godot_config import REPO_ROOT, PROJECT_GODOT, _load_ini

SAVE_SYSTEM_GD = REPO_ROOT / "save_system.gd"


def test_save_system_script_exists() -> None:
    assert SAVE_SYSTEM_GD.is_file()


def test_save_system_autoload_registered() -> None:
    text = PROJECT_GODOT.read_text(encoding="utf-8")
    assert 'SaveSystem="*res://save_system.gd"' in text


def test_save_system_autoload_section_parseable() -> None:
    cp = _load_ini(PROJECT_GODOT)
    assert cp.has_section("autoload")
    assert cp.get("autoload", "savesystem") == '"*res://save_system.gd"'


def test_save_data_fields_documented_in_script() -> None:
    src = SAVE_SYSTEM_GD.read_text(encoding="utf-8")
    for needle in (
        '"play_time"',
        '"game_complete"',
        '"player_pos"',
        '"quest_flags"',
        '"lore_unlocked"',
        '"inventory"',
        '"current_scene"',
        '"dark_robe_unlocked"',
    ):
        assert needle in src, f"SaveData field missing from save_system.gd: {needle}"


def test_save_system_has_core_api() -> None:
    src = SAVE_SYSTEM_GD.read_text(encoding="utf-8")
    for name in (
        "func get_default_save_data",
        "func merge_with_defaults",
        "func save_to_slot",
        "func load_from_slot",
        "JSON.stringify",
        "JSON.parse_string",
    ):
        assert name in src


def test_save_system_uses_user_slot_json_pattern() -> None:
    src = SAVE_SYSTEM_GD.read_text(encoding="utf-8")
    assert "user://save_slot_" in src
