"""Static checks for Light Sphere spell + effect scene (no Godot binary)."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SPELL_GD = REPO_ROOT / "scripts" / "light_sphere_spell.gd"
EFFECT_GD = REPO_ROOT / "scripts" / "light_sphere_effect.gd"
EFFECT_SCENE = REPO_ROOT / "scenes" / "effects" / "light_sphere.tscn"


def test_light_sphere_spell_script_exists() -> None:
    assert SPELL_GD.is_file()


def test_light_sphere_effect_script_exists() -> None:
    assert EFFECT_GD.is_file()


def test_light_sphere_scene_exists() -> None:
    assert EFFECT_SCENE.is_file()


def test_light_sphere_spell_contract() -> None:
    text = SPELL_GD.read_text(encoding="utf-8")
    assert "class_name LightSphereSpell" in text
    assert "extends RefCounted" in text
    assert "ManaComponent" in text
    assert "use_mana" in text
    assert re.search(r"MANA_COST\s*:=\s*5", text)
    assert re.search(r"DURATION_SEC\s*:=\s*30", text)
    assert re.search(r"RADIUS_TILES\s*:=\s*5", text)
    assert "light_sphere.tscn" in text


def test_light_sphere_effect_contract() -> None:
    text = EFFECT_GD.read_text(encoding="utf-8")
    assert "PointLight2D" in text
    assert re.search(r"DURATION_SEC\s*:=\s*30", text)
    assert re.search(r"RADIUS_TILES\s*:=\s*5", text)
    assert re.search(r"TILE_WORLD_PX\s*:=\s*16", text)
    assert "GradientTexture2D" in text
    assert "queue_free" in text


def test_light_sphere_scene_wires_effect() -> None:
    scene = EFFECT_SCENE.read_text(encoding="utf-8")
    assert "res://scripts/light_sphere_effect.gd" in scene
    assert "PointLight2D" in scene
