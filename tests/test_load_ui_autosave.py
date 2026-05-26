"""Spec 2618: load UI lists autosave distinctly (filesystem checks, no Godot binary)."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SAVE_MANAGER = REPO_ROOT / "game" / "save_manager.gd"
LOAD_SCREEN = REPO_ROOT / "game" / "load_screen.gd"
MAIN_SCENE = REPO_ROOT / "scenes" / "main.tscn"


def test_load_screen_script_exists() -> None:
    assert LOAD_SCREEN.is_file()


def test_main_scene_uses_load_screen_script() -> None:
    text = MAIN_SCENE.read_text(encoding="utf-8")
    assert "load_screen.gd" in text
    assert "ItemList" in text


def test_load_screen_uses_display_name_and_list_helpers() -> None:
    text = LOAD_SCREEN.read_text(encoding="utf-8")
    assert "get_slot_display_name" in text
    assert "list_user_save_paths" in text
    assert "load_save_from_path" in text


def test_save_manager_lists_save_json_files() -> None:
    text = SAVE_MANAGER.read_text(encoding="utf-8")
    assert "func list_user_save_paths" in text
    assert "save_" in text and ".json" in text


def test_load_save_skips_autosave_before_scene_change() -> None:
    """Loading must not call autosave_silent (would overwrite autosave before restore)."""
    text = SAVE_MANAGER.read_text(encoding="utf-8")
    start = text.find("func load_save_from_path")
    assert start != -1
    next_fn = text.find("\nfunc ", start + 1)
    chunk = text[start:] if next_fn == -1 else text[start:next_fn]
    assert "autosave_silent" not in chunk
    assert "change_scene_to_file" in chunk


def test_load_screen_has_no_push_or_print() -> None:
    body = LOAD_SCREEN.read_text(encoding="utf-8")
    lowered = body.lower()
    assert "push_error" not in lowered
    assert "push_warning" not in lowered
    assert "print(" not in body
