"""Structural checks for Player footstep wiring (no Godot runtime)."""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
PLAYER_GD = REPO_ROOT / "Player.gd"
PLAYER_TSCN = REPO_ROOT / "Player.tscn"
STONE_WAV = REPO_ROOT / "assets" / "audio" / "footstep_stone.wav"
WOOD_WAV = REPO_ROOT / "assets" / "audio" / "footstep_wood.wav"


def test_player_script_exists() -> None:
    assert PLAYER_GD.is_file()


def test_player_scene_exists() -> None:
    assert PLAYER_TSCN.is_file()


def test_footstep_audio_assets_exist() -> None:
    assert STONE_WAV.is_file()
    assert WOOD_WAV.is_file()


def test_player_gd_footstep_distance_and_sfx_manager() -> None:
    text = PLAYER_GD.read_text(encoding="utf-8")
    assert "FOOTSTEP_DISTANCE_PX := 32.0" in text
    assert "SFXManager.play" in text
    assert "wood_floor_tiles" in text
    assert "TileMapLayer" in text
    assert "get_cell_source_id" in text


def test_player_tscn_references_script_and_streams() -> None:
    text = PLAYER_TSCN.read_text(encoding="utf-8")
    assert 'path="res://Player.gd"' in text
    assert "footstep_stone.wav" in text
    assert "footstep_wood.wav" in text
