"""Phase 2603: SaveMenu scene (3 slots) and SceneTransition autosave hook (static checks)."""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.test_godot_config import REPO_ROOT, PROJECT_GODOT, _load_ini

SAVE_MENU_SCENE = REPO_ROOT / "scenes" / "save_menu.tscn"
SAVE_MENU_SCRIPT = REPO_ROOT / "scripts" / "save_menu.gd"
SCENE_TRANSITION_SCRIPT = REPO_ROOT / "scripts" / "scene_transition.gd"


def test_save_menu_scene_exists() -> None:
    assert SAVE_MENU_SCENE.is_file()


def test_save_menu_has_three_slot_buttons() -> None:
    text = SAVE_MENU_SCENE.read_text(encoding="utf-8")
    assert text.count('type="Button"') == 3
    assert '[node name="Slot1" type="Button"' in text
    assert '[node name="Slot2" type="Button"' in text
    assert '[node name="Slot3" type="Button"' in text
    assert text.count("unique_name_in_owner = true") == 3


def test_save_menu_scene_wires_script() -> None:
    text = SAVE_MENU_SCENE.read_text(encoding="utf-8")
    assert 'path="res://scripts/save_menu.gd"' in text


def test_save_menu_script_uses_slot_paths_and_time() -> None:
    src = SAVE_MENU_SCRIPT.read_text(encoding="utf-8")
    assert "user://save_slot_%d.json" in src
    assert "FileAccess.get_modified_time" in src
    assert "Time.get_datetime_dict_from_unix_time" in src


def test_scene_transition_script_exists() -> None:
    assert SCENE_TRANSITION_SCRIPT.is_file()


def test_scene_transition_emits_scene_changed_and_autosaves_slot_zero() -> None:
    src = SCENE_TRANSITION_SCRIPT.read_text(encoding="utf-8")
    assert "signal scene_changed" in src
    assert "scene_changed.emit" in src
    assert "save_to_slot" in src
    assert "AUTOSAVE_SLOT" in src


def test_scene_transition_autoload_registered() -> None:
    text = PROJECT_GODOT.read_text(encoding="utf-8")
    assert 'SceneTransition="*res://scripts/scene_transition.gd"' in text


def test_scene_transition_autoload_after_save_system() -> None:
    """SaveSystem must load first so SceneTransition can call it in _ready."""
    lines = PROJECT_GODOT.read_text(encoding="utf-8").splitlines()
    save_idx = None
    scene_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith("SaveSystem="):
            save_idx = i
        if line.strip().startswith("SceneTransition="):
            scene_idx = i
    assert save_idx is not None and scene_idx is not None
    assert save_idx < scene_idx


def test_scene_transition_autoload_section_parseable() -> None:
    cp = _load_ini(PROJECT_GODOT)
    assert cp.has_section("autoload")
    assert cp.get("autoload", "scenetransition") == '"*res://scripts/scene_transition.gd"'
