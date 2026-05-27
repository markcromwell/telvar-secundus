"""Static checks for passive Detect Magic GDScript (no Godot binary)."""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
DETECT_MAGIC_GD = REPO_ROOT / "scripts" / "detect_magic_passive.gd"
PROJECT_GODOT = REPO_ROOT / "project.godot"


def test_detect_magic_script_exists() -> None:
    assert DETECT_MAGIC_GD.is_file()


def test_detect_magic_passive_contract() -> None:
    text = DETECT_MAGIC_GD.read_text(encoding="utf-8")
    assert "HIGHLIGHT_DURATION_SEC" in text
    assert "5.0" in text
    assert "COOLDOWN_AFTER_HIGHLIGHT_SEC" in text
    assert "3.0" in text
    assert '"magical"' in text
    assert "get_known_spells" in text
    assert "detect_magic" in text


def test_project_godot_registers_detect_magic_autoload() -> None:
    text = PROJECT_GODOT.read_text(encoding="utf-8")
    assert "DetectMagicPassive=" in text
    assert "res://scripts/detect_magic_passive.gd" in text
