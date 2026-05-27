"""Structural checks for scenes/game_over.tscn and save payload rules (phase 2711)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
GAME_OVER_SCENE = REPO_ROOT / "scenes" / "game_over.tscn"
GAME_OVER_SCRIPT = REPO_ROOT / "scripts" / "game_over.gd"


def _validate_save_payload(data: object) -> str:
    """Mirror critical checks from scripts/game_over.gd before scene change (no ResourceLoader)."""
    if not isinstance(data, dict):
        return "Save file is corrupted (invalid root)."
    if "current_scene" not in data:
        return "Save file is corrupted (missing current_scene)."
    scene_path = data["current_scene"]
    if not isinstance(scene_path, str):
        return "Save file is corrupted (invalid current_scene)."
    if not scene_path.startswith("res://"):
        return "Save file is corrupted (scene path must start with res://)."
    return ""


def test_game_over_scene_file_exists() -> None:
    assert GAME_OVER_SCENE.is_file()


def test_game_over_script_file_exists() -> None:
    assert GAME_OVER_SCRIPT.is_file()


def test_game_over_scene_references_script() -> None:
    text = GAME_OVER_SCENE.read_text(encoding="utf-8")
    assert 'path="res://scripts/game_over.gd"' in text
    assert "[ext_resource type=" in text and "Script" in text


def test_game_over_scene_has_load_button_and_signal() -> None:
    text = GAME_OVER_SCENE.read_text(encoding="utf-8")
    assert "LoadLastSaveButton" in text
    assert 'method="_on_load_last_save_pressed"' in text
    assert 'signal="pressed"' in text


def test_game_over_scene_unique_names_for_script_nodes() -> None:
    text = GAME_OVER_SCENE.read_text(encoding="utf-8")
    assert "unique_name_in_owner = true" in text
    assert "ErrorLabel" in text


def test_game_over_script_has_save_slots_and_validation() -> None:
    src = GAME_OVER_SCRIPT.read_text(encoding="utf-8")
    assert "SAVE_PATH_TMPL" in src
    assert "save_slot_" in src
    assert "JSON.new()" in src
    assert "change_scene_to_file" in src
    assert "TYPE_DICTIONARY" in src
    assert "_show_error" in src


def test_game_over_title_and_prompt_copy() -> None:
    text = GAME_OVER_SCENE.read_text(encoding="utf-8")
    assert "Game Over" in text
    assert "Load from your last save" in text
    assert "Load last save" in text


def test_validate_save_payload_accepts_minimal_valid_dict() -> None:
    assert _validate_save_payload({"current_scene": "res://scenes/game_over.tscn"}) == ""


@pytest.mark.parametrize(
    "payload,fragment",
    [
        ("not a dict", "invalid root"),
        ({}, "missing current_scene"),
        ({"current_scene": 123}, "invalid current_scene"),
        ({"current_scene": "C:/evil.tscn"}, "res://"),
    ],
)
def test_validate_save_payload_rejects_bad_payload(payload: object, fragment: str) -> None:
    err = _validate_save_payload(payload)
    assert fragment in err


def test_game_over_script_mentions_corrupt_user_feedback() -> None:
    src = GAME_OVER_SCRIPT.read_text(encoding="utf-8")
    assert "corrupted" in src.lower()


def test_example_save_json_roundtrip_matches_validation() -> None:
    sample = {
        "player_pos": {"x": 0, "y": 0},
        "quest_flags": {},
        "lore_unlocked": [],
        "inventory": [],
        "current_scene": "res://scenes/game_over.tscn",
        "play_time": 1.0,
    }
    raw = json.dumps(sample)
    data = json.loads(raw)
    assert _validate_save_payload(data) == ""
