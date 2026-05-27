"""Structural checks for defeat fade-to-black and save-point respawn (phase 2683)."""

from __future__ import annotations

from pathlib import Path

from tests.test_godot_config import REPO_ROOT

SPELL_BOOK_GD = REPO_ROOT / "autoload/spell_book.gd"
MAIN_GD = REPO_ROOT / "scenes/main.gd"
MAIN_TSCN = REPO_ROOT / "scenes/main.tscn"


def test_spell_book_defeat_hp_and_save_point_api() -> None:
    src = SPELL_BOOK_GD.read_text(encoding="utf-8")
    assert "DEFEAT_RESPAWN_HP := 15" in src
    assert "var player_hp" in src
    assert "func record_last_save_point" in src
    assert "func apply_defeat_respawn_state" in src
    assert "last_save_scene_path" in src


def test_main_defeat_fanfare_api() -> None:
    src = MAIN_GD.read_text(encoding="utf-8")
    assert "play_defeat_fade_and_respawn" in src
    assert "defeat_respawn_handler" in src
    assert "DefeatFadeRect" in src
    assert "reload_current_scene" in src or "change_scene_to_file" in src


def test_main_scene_wires_defeat_fade() -> None:
    t = MAIN_TSCN.read_text(encoding="utf-8")
    assert "DefeatCanvas" in t
    assert "DefeatFadeRect" in t
    assert "ColorRect" in t
