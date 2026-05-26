"""Text-level checks for sealed wings enter sequence (Godot GDScript)."""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
WINGS = REPO_ROOT / "scripts" / "wings_enter_sequence.gd"
PLAYER = REPO_ROOT / "player" / "Player.gd"
INVENTORY = REPO_ROOT / "scripts" / "inventory.gd"


def test_wings_script_exists() -> None:
    assert WINGS.is_file()


def test_walk_is_five_rendered_tiles() -> None:
    text = WINGS.read_text(encoding="utf-8")
    assert "WALK_TILE_COUNT: int = 5" in text
    assert "float(WALK_TILE_COUNT) * RENDERED_TILE_PX" in text


def test_enter_consumes_key_before_walk() -> None:
    text = WINGS.read_text(encoding="utf-8")
    assert "try_consume_sealed_wings_key" in text
    assert text.index("try_consume_sealed_wings_key") < text.index("_play_door_then_walk")


def test_player_disables_manual_input_not_global_freeze() -> None:
    text = PLAYER.read_text(encoding="utf-8")
    assert "manual_input_enabled" in text
    assert "set_scripted_velocity" in text


def test_inventory_exposes_wings_key_consume() -> None:
    text = INVENTORY.read_text(encoding="utf-8")
    assert "try_consume_sealed_wings_key" in text
