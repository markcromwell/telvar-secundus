"""Structural checks for dialogue / UI click SFX (no Godot runtime)."""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
DIALOGUE_MANAGER_GD = REPO_ROOT / "DialogueManager.gd"
DIALOGUE_BOX_GD = REPO_ROOT / "DialogueBox.gd"
UI_CLICK_WAV = REPO_ROOT / "assets" / "audio" / "ui_click.wav"


def test_dialogue_manager_script_exists() -> None:
    assert DIALOGUE_MANAGER_GD.is_file()


def test_dialogue_box_script_exists() -> None:
    assert DIALOGUE_BOX_GD.is_file()


def test_ui_click_wav_exists() -> None:
    assert UI_CLICK_WAV.is_file()


def test_dialogue_manager_routes_sfx_bus_and_single_player() -> None:
    text = DIALOGUE_MANAGER_GD.read_text(encoding="utf-8")
    assert 'bus = BUS_SFX' in text
    assert 'const BUS_SFX := "SFX"' in text
    assert "AudioStreamPlayer.new()" in text
    assert "max_polyphony = 1" in text
    assert "func play_ui_click" in text
    assert "_ui_click_player.stop()" in text
    assert "wire_buttons_under" in text


def test_dialogue_manager_uses_sfx_manager_not() -> None:
    """Phase 2738: UI clicks use a dedicated player on the SFX bus (not SFXManager.gd edits)."""
    text = DIALOGUE_MANAGER_GD.read_text(encoding="utf-8")
    assert "SFXManager" not in text


def test_dialogue_box_calls_manager_on_advance() -> None:
    text = DIALOGUE_BOX_GD.read_text(encoding="utf-8")
    assert "func advance_dialogue" in text
    assert "DialogueManager.singleton" in text
    assert "play_ui_click" in text
    assert "_play_advance_click_sfx" in text
