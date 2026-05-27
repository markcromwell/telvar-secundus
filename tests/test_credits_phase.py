"""Phase 2604: Credits scene, end screen play time, main menu link, CREDITS.md (static checks)."""

from __future__ import annotations

import pytest

from tests.test_godot_config import REPO_ROOT, PROJECT_GODOT, _load_ini

CREDITS_MD = REPO_ROOT / "CREDITS.md"
MAIN_MENU_SCENE = REPO_ROOT / "scenes" / "main_menu.tscn"
CREDITS_SCENE = REPO_ROOT / "scenes" / "credits.tscn"
END_SCREEN_SCENE = REPO_ROOT / "scenes" / "end_screen.tscn"
CREDITS_SCRIPT = REPO_ROOT / "scripts" / "credits.gd"
ACTIVE_SLOT_SCRIPT = REPO_ROOT / "scripts" / "active_save_slot.gd"

_EXPECTED_CREDITS = """# Credits
## Art
- LPC Base Sprites by Rhune/Sharm (CC-BY-SA 3.0) — OpenGameArt.org
- LPC Terrain by various LPC contributors (CC-BY-SA 3.0)
## Code
- Godot Engine 4.3 (MIT License) — godotengine.org
## Story
- New Paladin Order series by Mark Cromwell
"""


def test_credits_md_matches_spec_format() -> None:
    assert CREDITS_MD.is_file()
    text = CREDITS_MD.read_text(encoding="utf-8").strip("\n") + "\n"
    expected = _EXPECTED_CREDITS.strip("\n") + "\n"
    assert text == expected


def test_main_scene_is_main_menu() -> None:
    cp = _load_ini(PROJECT_GODOT)
    assert cp.get("application", "run/main_scene") == '"res://scenes/main_menu.tscn"'


def test_active_save_slot_autoload_registered() -> None:
    text = PROJECT_GODOT.read_text(encoding="utf-8")
    assert 'ActiveSaveSlot="*res://scripts/active_save_slot.gd"' in text


def test_active_save_slot_autoload_after_scene_transition() -> None:
    lines = PROJECT_GODOT.read_text(encoding="utf-8").splitlines()
    scene_idx = None
    active_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith("SceneTransition="):
            scene_idx = i
        if line.strip().startswith("ActiveSaveSlot="):
            active_idx = i
    assert scene_idx is not None and active_idx is not None
    assert scene_idx < active_idx


def test_main_menu_scene_has_credits_button_and_script() -> None:
    assert MAIN_MENU_SCENE.is_file()
    text = MAIN_MENU_SCENE.read_text(encoding="utf-8")
    assert 'path="res://scripts/main_menu.gd"' in text
    assert '[node name="Credits" type="Button"' in text
    assert "unique_name_in_owner = true" in text


def test_credits_scene_structure() -> None:
    assert CREDITS_SCENE.is_file()
    text = CREDITS_SCENE.read_text(encoding="utf-8")
    assert 'path="res://scripts/credits.gd"' in text
    assert '[node name="CreditsBody" type="RichTextLabel"' in text
    assert '[node name="PlayTime" type="Label"' in text
    assert '[node name="Finish" type="Button"' in text


def test_credits_script_persists_completion() -> None:
    src = CREDITS_SCRIPT.read_text(encoding="utf-8")
    assert '"game_complete"' in src
    assert '"dark_robe_unlocked"' in src
    assert "save_to_slot" in src


def test_end_screen_shows_play_time_and_links_to_credits() -> None:
    assert END_SCREEN_SCENE.is_file()
    text = END_SCREEN_SCENE.read_text(encoding="utf-8")
    assert 'path="res://scripts/end_screen.gd"' in text
    assert '[node name="PlayTime" type="Label"' in text
    assert '[node name="ToCredits" type="Button"' in text


def test_active_save_slot_script_exists() -> None:
    assert ACTIVE_SLOT_SCRIPT.is_file()
