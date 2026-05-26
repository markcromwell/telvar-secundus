"""Static checks for ManaComponent + HUD GDScript (no Godot binary)."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
MANA_COMPONENT = REPO_ROOT / "scripts" / "mana_component.gd"
MANA_HUD = REPO_ROOT / "scripts" / "mana_hud_bar.gd"
GAME_HUD_SCENE = REPO_ROOT / "scenes" / "ui" / "game_hud.tscn"


def test_mana_component_script_exists() -> None:
    assert MANA_COMPONENT.is_file()


def test_mana_hud_script_exists() -> None:
    assert MANA_HUD.is_file()


def test_game_hud_scene_exists() -> None:
    assert GAME_HUD_SCENE.is_file()


def test_mana_component_contract() -> None:
    text = MANA_COMPONENT.read_text(encoding="utf-8")
    assert "class_name ManaComponent" in text
    assert "signal mana_changed" in text
    assert re.search(r"@export\s+var\s+max_mana:\s*int\s*=\s*20", text)
    assert "func use_mana" in text
    assert "regen_mana_combat_turn" in text
    assert "out_of_combat_regen_interval" in text
    assert "5.0" in text


def test_mana_hud_uses_mana_blue_and_binds_signal() -> None:
    text = MANA_HUD.read_text(encoding="utf-8")
    assert "4488ff" in text.casefold()
    assert "mana_changed" in text
    assert "ManaComponent" in text


def test_game_hud_scene_wires_mana_nodes() -> None:
    scene = GAME_HUD_SCENE.read_text(encoding="utf-8")
    assert 'path="res://scripts/mana_component.gd"' in scene
    assert 'path="res://scripts/mana_hud_bar.gd"' in scene
    assert "ManaComponent" in scene
    assert "ManaBar" in scene
    assert "HPBar" in scene
