"""Phase 2605: Player reads game_complete from save and applies dark robe variant on spawn (static checks)."""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.test_godot_config import REPO_ROOT

PLAYER_SCRIPT = REPO_ROOT / "scripts" / "player.gd"


def test_player_script_exists() -> None:
	assert PLAYER_SCRIPT.is_file()


def test_player_loads_save_and_branches_on_game_complete() -> None:
	src = PLAYER_SCRIPT.read_text(encoding="utf-8")
	for needle in (
		"SaveSystem.load_from_slot",
		'"game_complete"',
		"TYPE_BOOL",
		"_set_dark_robe_variant",
		"_set_default_robe_variant",
		"ActiveSaveSlot.slot",
	):
		assert needle in src, f"player.gd missing expected fragment: {needle!r}"


def test_player_supports_default_and_dark_robe_render_paths() -> None:
	src = PLAYER_SCRIPT.read_text(encoding="utf-8")
	assert "dark_robe" in src
	assert "default" in src
	assert "AnimatedSprite2D" in src
	assert "Sprite2D" in src
