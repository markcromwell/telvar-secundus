"""Structural checks for Banishment spell resources and combat constants (phase 2680)."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from tests.test_godot_config import REPO_ROOT, _load_ini

BANISHMENT_TRES = REPO_ROOT / "resources/spells/banishment.tres"
SPELL_GD = REPO_ROOT / "resources/spell.gd"
SPELL_COMBAT_GD = REPO_ROOT / "scripts/combat/spell_combat.gd"
SPELL_BOOK_GD = REPO_ROOT / "autoload/spell_book.gd"
CAST_PANEL_TSCN = REPO_ROOT / "scenes/ui/cast_spell_panel.tscn"
CAST_PANEL_GD = REPO_ROOT / "ui/cast_spell_panel.gd"
PROJECT_GODOT = REPO_ROOT / "project.godot"


def test_banishment_tres_exists() -> None:
    assert BANISHMENT_TRES.is_file()


def test_banishment_tres_spell_id_and_damage() -> None:
    text = BANISHMENT_TRES.read_text(encoding="utf-8")
    assert 'spell_id = "banishment"' in text
    assert re.search(r"damage\s*=\s*15", text)


def test_spell_resource_script_exports() -> None:
    src = SPELL_GD.read_text(encoding="utf-8")
    assert "class_name Spell" in src
    for needle in ("spell_id", "spell_name", "mana_cost", "damage", "effect"):
        assert needle in src


def test_spell_combat_banishment_constants() -> None:
    src = SPELL_COMBAT_GD.read_text(encoding="utf-8")
    assert "BANISHMENT_PUSH_TILES := 3" in src
    assert "BANISHMENT_STUN_TURNS := 1" in src
    assert "BANISHMENT_SHADE_DAMAGE := 15" in src
    assert 'kind == "thug"' in src
    assert 'kind == "shade"' in src


def test_spell_book_loads_banishment_path() -> None:
    src = SPELL_BOOK_GD.read_text(encoding="utf-8")
    assert "res://resources/spells/banishment.tres" in src


def test_cast_spell_panel_scene_wires_script() -> None:
    assert CAST_PANEL_TSCN.is_file()
    tscn = CAST_PANEL_TSCN.read_text(encoding="utf-8")
    assert "cast_spell_panel.gd" in tscn
    panel = CAST_PANEL_GD.read_text(encoding="utf-8")
    assert "SpellBook" in panel


def test_main_scene_handles_spell_panel_toggle() -> None:
    main_gd = REPO_ROOT / "scenes/main.gd"
    assert main_gd.is_file()
    src = main_gd.read_text(encoding="utf-8")
    assert "_unhandled_input" in src
    assert "toggle_cast_spell" in src


def test_cast_spell_panel_uses_spellbook_lists() -> None:
    panel = CAST_PANEL_GD.read_text(encoding="utf-8")
    assert "SpellBook.get_learnable_display_lines" in panel
    assert "SpellBook.mana_current" in panel


def test_spell_book_learnable_catalog_and_helper() -> None:
    src = SPELL_BOOK_GD.read_text(encoding="utf-8")
    assert "LEARNABLE_CATALOG" in src
    assert "get_learnable_display_lines" in src


def test_project_input_toggle_cast_spell_s_key() -> None:
    text = PROJECT_GODOT.read_text(encoding="utf-8")
    assert "toggle_cast_spell" in text
    assert "keycode" in text and "83" in text


def test_main_scene_loads_cast_spell_panel() -> None:
    main = REPO_ROOT / "scenes/main.tscn"
    assert main.is_file()
    mt = main.read_text(encoding="utf-8")
    assert "cast_spell_panel.tscn" in mt
    assert "main.gd" in mt


def test_project_main_scene_set() -> None:
    text = PROJECT_GODOT.read_text(encoding="utf-8")
    assert 'run/main_scene="res://scenes/main.tscn"' in text


def test_project_autoload_spellbook() -> None:
    cp = _load_ini(PROJECT_GODOT)
    assert cp.has_section("autoload")
    spellbook = cp.get("autoload", "SpellBook", fallback="")
    assert "spell_book.gd" in spellbook
