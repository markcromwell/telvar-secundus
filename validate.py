#!/usr/bin/env python3
"""Structural validation for Telvar Secundus (Godot 4.x project).

Exits 0 on success, 1 with FAIL lines on errors. No Godot binary required.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
errors: list[str] = []


def _must_match(path: Path, pattern: str, description: str) -> None:
    if not path.is_file():
        errors.append(f"Missing file: {path.relative_to(REPO_ROOT)}")
        return
    text = path.read_text(encoding="utf-8")
    if not re.search(pattern, text, re.MULTILINE):
        errors.append(f"{path.relative_to(REPO_ROOT)}: {description}")


def _must_contain(path: Path, needle: str, description: str) -> None:
    if not path.is_file():
        errors.append(f"Missing file: {path.relative_to(REPO_ROOT)}")
        return
    if needle not in path.read_text(encoding="utf-8"):
        errors.append(f"{path.relative_to(REPO_ROOT)}: {description}")


def validate_spell_mana() -> None:
    spell_gd = REPO_ROOT / "spell" / "Spell.gd"
    book_gd = REPO_ROOT / "spell" / "SpellBook.gd"
    main_gd = REPO_ROOT / "main" / "Main.gd"
    project = REPO_ROOT / "project.godot"

    _must_match(spell_gd, r"@export\s+var\s+mana_cost\s*:\s*float", "Spell must export mana_cost (float)")
    _must_contain(spell_gd, "class_name Spell", "Spell.gd should declare class_name Spell")
    _must_contain(spell_gd, "extends Resource", "Spell should extend Resource")

    _must_contain(book_gd, "func cast_spell", "SpellBook should define cast_spell")
    _must_contain(book_gd, "spend_mana", "SpellBook should invoke spend_mana on the player")
    _must_match(
        book_gd,
        r"(current\s*<\s*cost|mana\s*<\s*cost)",
        "SpellBook should block casting when mana is below spell cost",
    )

    _must_contain(main_gd, "SpellBook.set_caster", "Main should register the player with SpellBook")

    if project.is_file():
        proj_text = project.read_text(encoding="utf-8")
        if "[autoload]" not in proj_text or "SpellBook=" not in proj_text or "spell/SpellBook.gd" not in proj_text:
            errors.append("project.godot: SpellBook autoload must point to spell/SpellBook.gd")
    else:
        errors.append("Missing file: project.godot")


def main() -> int:
    validate_spell_mana()
    if errors:
        for e in errors:
            print("FAIL:", e)
        return 1
    print("Validation passed (spell mana integration).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
