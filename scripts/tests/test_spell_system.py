"""Tests for Spell System and UI."""
from __future__ import annotations

import re
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SPELL_GD = REPO_ROOT / "scripts" / "spell.gd"
SPELL_BOOK_GD = REPO_ROOT / "scripts" / "spell_book.gd"
SPELL_PANEL_GD = REPO_ROOT / "scripts" / "ui" / "spell_panel.gd"
SPELL_PANEL_SCENE = REPO_ROOT / "scenes" / "ui" / "spell_panel.tscn"
PROJECT_GODOT = REPO_ROOT / "project.godot"

def test_spell_gd_exists() -> None:
    assert SPELL_GD.is_file()

def test_spell_book_gd_exists() -> None:
    assert SPELL_BOOK_GD.is_file()

def test_spell_panel_files_exist() -> None:
    assert SPELL_PANEL_GD.is_file()
    assert SPELL_PANEL_SCENE.is_file()

def test_spell_gd_contract() -> None:
    text = SPELL_GD.read_text(encoding="utf-8")
    assert "class_name Spell" in text
    assert "extends Resource" in text
    assert "var spell_id" in text
    assert "var name" in text
    assert "var mana_cost" in text
    assert "var damage" in text
    assert "var effect" in text

def test_spell_book_contract() -> None:
    text = SPELL_BOOK_GD.read_text(encoding="utf-8")
    assert "var known_spells" in text
    
def test_project_godot_registers_spell_book() -> None:
    text = PROJECT_GODOT.read_text(encoding="utf-8")
    assert "SpellBook=" in text
    assert "res://scripts/spell_book.gd" in text

def test_spell_panel_contract() -> None:
    gd_text = SPELL_PANEL_GD.read_text(encoding="utf-8")
    assert "extends Control" in gd_text
    assert "KEY_S" in gd_text
    assert "visible" in gd_text
    assert "SpellBook.get_known_spells()" in gd_text
    
    scene_text = SPELL_PANEL_SCENE.read_text(encoding="utf-8")
    assert "res://scripts/ui/spell_panel.gd" in scene_text
