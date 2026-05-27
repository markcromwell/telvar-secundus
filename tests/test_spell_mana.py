"""Static checks for Spell mana_cost and SpellBook casting integration."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SPELL_GD = REPO_ROOT / "spell" / "Spell.gd"
SPELLBOOK_GD = REPO_ROOT / "spell" / "SpellBook.gd"
MAIN_GD = REPO_ROOT / "main" / "Main.gd"
PROJECT_GODOT = REPO_ROOT / "project.godot"


def test_spell_script_exists() -> None:
    assert SPELL_GD.is_file(), f"Expected Spell at {SPELL_GD}"


def test_spell_exports_mana_cost() -> None:
    text = SPELL_GD.read_text(encoding="utf-8")
    assert "class_name Spell" in text
    assert "extends Resource" in text
    assert re.search(r"@export\s+var\s+mana_cost\s*:\s*float", text), "Spell must @export mana_cost as float"


def test_spellbook_exists_and_checks_mana_before_spend() -> None:
    text = SPELLBOOK_GD.read_text(encoding="utf-8")
    assert SPELLBOOK_GD.is_file()
    assert "func cast_spell" in text
    assert "mana_cost" in text
    assert re.search(r"get\s*\(\s*[\"']mana[\"']\s*\)", text), "SpellBook should read current mana via get(\"mana\")"
    assert "spend_mana" in text
    assert re.search(r"current\s*<\s*cost|mana\s*<\s*cost", text), "SpellBook should compare current mana to cost before casting"


def test_spellbook_cast_returns_bool_from_spend_mana() -> None:
    text = SPELLBOOK_GD.read_text(encoding="utf-8")
    assert "call(\"spend_mana\"" in text or "call('spend_mana'" in text or "spend_mana(" in text


def test_main_registers_caster_with_spellbook() -> None:
    text = MAIN_GD.read_text(encoding="utf-8")
    assert "SpellBook.set_caster" in text


def test_project_autoloads_spellbook() -> None:
    text = PROJECT_GODOT.read_text(encoding="utf-8")
    assert "[autoload]" in text
    assert "SpellBook=" in text
    assert "spell/SpellBook.gd" in text
