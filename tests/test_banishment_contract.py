"""Static checks for Banishment spell (no Godot binary)."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SPELL_GD = REPO_ROOT / "scripts" / "banishment_spell.gd"


def test_banishment_spell_script_exists() -> None:
    assert SPELL_GD.is_file()


def test_banishment_spell_contract() -> None:
    text = SPELL_GD.read_text(encoding="utf-8")
    assert "class_name BanishmentSpell" in text
    assert "extends RefCounted" in text
    assert "ManaComponent" in text
    assert "use_mana" in text
    assert re.search(r"MANA_COST\s*:=\s*20", text)
    assert re.search(r"SHADE_BONUS_DAMAGE\s*:=\s*15", text)
    assert '"enemies"' in text or "'enemies'" in text
    assert '"shades"' in text or "'shades'" in text
    assert "apply_stun" in text
    assert "take_damage" in text
    assert "intersect_shape" in text
    assert "PhysicsShapeQueryParameters2D" in text
