"""Static checks: player mana_changed signal and HUD wiring (phase 2642)."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
PLAYER_GD = REPO_ROOT / "player" / "Player.gd"
MAIN_GD = REPO_ROOT / "main" / "Main.gd"
MAIN_TSCN = REPO_ROOT / "main" / "Main.tscn"
PROJECT_GODOT = REPO_ROOT / "project.godot"


def test_player_declares_mana_changed_signal() -> None:
    text = PLAYER_GD.read_text(encoding="utf-8")
    assert re.search(r"signal\s+mana_changed\s*\(", text), "Player should declare mana_changed signal"


def test_player_emits_mana_changed_from_clamp() -> None:
    text = PLAYER_GD.read_text(encoding="utf-8")
    assert "mana_changed.emit" in text


def test_main_connects_player_mana_changed_to_hud() -> None:
    assert MAIN_GD.is_file()
    text = MAIN_GD.read_text(encoding="utf-8")
    assert "mana_changed.connect" in text
    assert "set_current_mana" in text


def test_main_scene_instances_player_and_hud() -> None:
    assert MAIN_TSCN.is_file()
    text = MAIN_TSCN.read_text(encoding="utf-8")
    assert "player/Player.gd" in text
    assert "HUD.tscn" in text


def test_project_runs_main_scene() -> None:
    text = PROJECT_GODOT.read_text(encoding="utf-8")
    assert 'run/main_scene="res://main/Main.tscn"' in text
