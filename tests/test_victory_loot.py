"""Structural checks for Thug victory fanfare and copper loot (phase 2682)."""

from __future__ import annotations

from pathlib import Path

from tests.test_godot_config import REPO_ROOT

SPELL_COMBAT_GD = REPO_ROOT / "scripts/combat/spell_combat.gd"
SPELL_BOOK_GD = REPO_ROOT / "autoload/spell_book.gd"
MAIN_GD = REPO_ROOT / "scenes/main.gd"
MAIN_TSCN = REPO_ROOT / "scenes/main.tscn"
VICTORY_WAV = REPO_ROOT / "assets/audio/victory_sting.wav"
CAST_PANEL_GD = REPO_ROOT / "ui/cast_spell_panel.gd"


def test_victory_sting_audio_exists() -> None:
    assert VICTORY_WAV.is_file()
    assert VICTORY_WAV.stat().st_size < 200_000


def test_spell_combat_thug_copper_constants() -> None:
    src = SPELL_COMBAT_GD.read_text(encoding="utf-8")
    assert "THUG_VICTORY_COPPER_MIN := 1" in src
    assert "THUG_VICTORY_COPPER_MAX := 3" in src
    assert "roll_thug_victory_copper" in src


def test_spell_book_tracks_copper() -> None:
    src = SPELL_BOOK_GD.read_text(encoding="utf-8")
    assert "var copper: int = 0" in src
    assert "func grant_copper" in src


def test_main_scene_wires_victory_nodes() -> None:
    t = MAIN_TSCN.read_text(encoding="utf-8")
    assert "VictoryCanvas" in t
    assert "VictoryLabel" in t
    assert "VictorySFX" in t
    assert "victory_sting.wav" in t
    assert "AudioStreamPlayer" in t


def test_main_victory_fanfare_api() -> None:
    src = MAIN_GD.read_text(encoding="utf-8")
    assert "play_thug_victory_fanfare" in src
    assert "thug_victory_fanfare" in src
    assert "SpellCombat.roll_thug_victory_copper" in src
    assert "SpellBook.grant_copper" in src


def test_cast_spell_panel_shows_copper() -> None:
    src = CAST_PANEL_GD.read_text(encoding="utf-8")
    assert "SpellBook.copper" in src
