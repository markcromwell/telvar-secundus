#!/usr/bin/env python3
"""Telvar Secundus structural validation (no Godot binary).

Checks required files and minimal scene wiring for CI.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent

REQUIRED_FILES = [
    "resources/spell.gd",
    "resources/spells/banishment.tres",
    "autoload/spell_book.gd",
    "scripts/combat/spell_combat.gd",
    "ui/cast_spell_panel.gd",
    "scenes/ui/cast_spell_panel.tscn",
    "scenes/main.tscn",
    "scenes/main.gd",
    "assets/audio/victory_sting.wav",
    "project.godot",
]

ERRORS: list[str] = []


def _fail(msg: str) -> None:
    ERRORS.append(msg)


def _check_files() -> None:
    for rel in REQUIRED_FILES:
        p = REPO / rel
        if not p.is_file():
            _fail(f"Missing required file: {rel}")


def _check_cast_spell_panel_scene() -> None:
    path = REPO / "scenes/ui/cast_spell_panel.tscn"
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    if "[gd_scene" not in text:
        _fail("cast_spell_panel.tscn: missing [gd_scene header")
    if "cast_spell_panel.gd" not in text:
        _fail("cast_spell_panel.tscn: must reference cast_spell_panel.gd")
    if re.search(r"\[node\s+name=\"CastSpellPanel\"", text) is None:
        _fail("cast_spell_panel.tscn: expected CastSpellPanel root node")


def _check_project_autoload() -> None:
    pg = REPO / "project.godot"
    if not pg.is_file():
        return
    text = pg.read_text(encoding="utf-8")
    if "[autoload]" not in text:
        _fail("project.godot: missing [autoload] section")
    if "SpellBook" not in text or "spell_book.gd" not in text:
        _fail("project.godot: SpellBook autoload must point to spell_book.gd")


def _check_banishment_tres() -> None:
    p = REPO / "resources/spells/banishment.tres"
    if not p.is_file():
        return
    t = p.read_text(encoding="utf-8")
    if re.search(r"spell_id\s*=\s*\"banishment\"", t) is None:
        _fail("banishment.tres: spell_id must be banishment")
    if re.search(r"damage\s*=\s*15", t) is None:
        _fail("banishment.tres: damage must be 15")


def main() -> int:
    _check_files()
    _check_project_autoload()
    _check_banishment_tres()
    _check_cast_spell_panel_scene()
    if ERRORS:
        for e in ERRORS:
            print("FAIL:", e)
        return 1
    print("Validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
