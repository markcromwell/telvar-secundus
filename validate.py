#!/usr/bin/env python3
"""Static validation for the Telvar Secundus Godot project.

The automation workers do not run the Godot editor/runtime. These checks parse
project files as text and enforce the structural contracts needed by the Red-rank
starter spell implementation.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
errors: list[str] = []


def read_required(rel_path: str) -> str:
    path = ROOT / rel_path
    if not path.is_file():
        errors.append(f"missing {rel_path}")
        return ""
    return path.read_text(encoding="utf-8")


def require(text: str, needle: str, message: str) -> None:
    if needle not in text:
        errors.append(message)


def require_regex(text: str, pattern: str, message: str) -> None:
    if not re.search(pattern, text):
        errors.append(message)


def validate_project_autoloads() -> None:
    project = read_required("project.godot")
    if not project:
        return
    require(project, "SpellBook=", "project.godot must autoload SpellBook")
    require(project, "res://scripts/spell_book.gd", "SpellBook autoload must point to scripts/spell_book.gd")
    require(project, "DetectMagicPassive=", "project.godot must autoload DetectMagicPassive")
    require(
        project,
        "res://scripts/detect_magic_passive.gd",
        "DetectMagicPassive autoload must point to scripts/detect_magic_passive.gd",
    )


def validate_spell_resource_and_book() -> None:
    spell = read_required("scripts/spell.gd")
    if spell:
        require(spell, "class_name Spell", "scripts/spell.gd must define class_name Spell")
        require(spell, "extends Resource", "Spell must extend Resource")
        for field in ("spell_id", "name", "mana_cost", "damage", "effect"):
            require_regex(spell, rf"var\s+{field}\b", f"Spell resource must export/store {field}")

    book = read_required("scripts/spell_book.gd")
    if book:
        require(book, "get_known_spells", "SpellBook must expose get_known_spells()")
        for spell_id, display_name, cost in (
            ("detect_magic", "Detect Magic", 0),
            ("light_sphere", "Light Sphere", 5),
            ("banishment", "Banishment", 20),
        ):
            require(book, spell_id, f"SpellBook must register {spell_id}")
            require(book, display_name, f"SpellBook must name {display_name}")
            require_regex(
                book,
                rf'Spell\.new\("{spell_id}",\s*"{re.escape(display_name)}",\s*{cost}\b',
                f"{display_name} must have mana cost {cost}",
            )
        require(book, "15 dmg vs shades", "Banishment spell metadata must mention shade bonus damage")


def validate_mana_system() -> None:
    mana = read_required("scripts/mana_component.gd")
    if mana:
        require(mana, "class_name ManaComponent", "ManaComponent must have a class_name")
        require(mana, "signal mana_changed", "ManaComponent must emit mana_changed")
        require_regex(mana, r"@export\s+var\s+max_mana:\s*int\s*=\s*20", "ManaComponent max_mana must default to 20")
        require(mana, "func use_mana", "ManaComponent must implement use_mana")
        require(mana, "current_mana < cost", "use_mana must reject unaffordable casts")
        require(mana, "current_mana -= cost", "use_mana must deduct mana")
        require(mana, "regen_mana_combat_turn", "ManaComponent must support combat turn regen")
        require(mana, "out_of_combat_regen_interval", "ManaComponent must support timed out-of-combat regen")
        require(mana, "5.0", "Out-of-combat mana regen interval must default to 5 seconds")

    hud_script = read_required("scripts/mana_hud_bar.gd")
    if hud_script:
        require(hud_script.casefold(), "4488ff", "Mana HUD fill color must be #4488ff")
        require(hud_script, "extends ProgressBar", "Mana HUD script must extend ProgressBar")
        require(hud_script, "mana_changed", "Mana HUD must bind to mana_changed")

    hud_scene = read_required("scenes/ui/game_hud.tscn")
    if hud_scene:
        require(hud_scene, 'path="res://scripts/mana_component.gd"', "GameHUD scene must reference ManaComponent")
        require(hud_scene, 'path="res://scripts/mana_hud_bar.gd"', "GameHUD scene must reference ManaHudBar")
        require(hud_scene, '[node name="HPBar" type="ProgressBar"', "GameHUD scene must contain an HPBar")
        require(hud_scene, '[node name="ManaBar" type="ProgressBar"', "GameHUD scene must contain a ManaBar")
        require(hud_scene, "mana_component = NodePath", "ManaBar must point at a ManaComponent")


def validate_detect_magic() -> None:
    text = read_required("scripts/detect_magic_passive.gd")
    if not text:
        return
    require_regex(text, r"HIGHLIGHT_DURATION_SEC\s*:=\s*5\.0", "Detect Magic must highlight objects for 5s")
    require_regex(text, r"COOLDOWN_AFTER_HIGHLIGHT_SEC\s*:=\s*3\.0", "Detect Magic must have a 3s cooldown")
    require(text, "SpellBook.get_known_spells()", "Detect Magic must check known spells through SpellBook")
    require(text, '"detect_magic"', "Detect Magic must look up the detect_magic spell id")
    require(text, '"magical"', "Detect Magic must scan tagged magical objects")
    require(text, "modulate", "Detect Magic must visually highlight magical CanvasItems")
    require(text, "Color(1.0, 0.95, 0.65)", "Detect Magic shimmer must include a gold highlight color")
    require(text, "_clear_highlights", "Detect Magic must clear highlights after the duration")


def validate_light_sphere() -> None:
    spell = read_required("scripts/light_sphere_spell.gd")
    if spell:
        require(spell, "class_name LightSphereSpell", "Light Sphere spell must define class_name LightSphereSpell")
        require(spell, "extends RefCounted", "Light Sphere spell helper must extend RefCounted")
        require_regex(spell, r'MANA_COST\s*:=\s*5\b', "Light Sphere must cost 5 mana")
        require_regex(spell, r'DURATION_SEC\s*:=\s*30\.?0?\b', "Light Sphere must last 30 seconds")
        require_regex(spell, r'RADIUS_TILES\s*:=\s*5\b', "Light Sphere must use a 5-tile radius")
        require(spell, "use_mana(MANA_COST)", "Light Sphere must deduct mana through ManaComponent")
        require(spell, "light_sphere.tscn", "Light Sphere must instantiate its effect scene")
        require(spell, "global_position", "Light Sphere must place the light at the cast position")

    effect = read_required("scripts/light_sphere_effect.gd")
    if effect:
        require(effect, "extends Node2D", "Light Sphere effect must extend Node2D")
        require(effect, "PointLight2D", "Light Sphere effect must drive a PointLight2D")
        require_regex(effect, r'DURATION_SEC\s*:=\s*30\.?0?\b', "Light Sphere effect must last 30 seconds")
        require_regex(effect, r'RADIUS_TILES\s*:=\s*5\b', "Light Sphere effect must use a 5-tile radius")
        require_regex(effect, r'TILE_WORLD_PX\s*:=\s*16\b', "Light Sphere effect must use 16px tiles")
        require(effect, "GradientTexture2D", "Light Sphere effect must create a radial light texture")
        require(effect, "queue_free", "Light Sphere effect must remove itself after expiring")

    scene = read_required("scenes/effects/light_sphere.tscn")
    if scene:
        require(scene, '[node name="LightSphere" type="Node2D"', "Light Sphere scene root must be a Node2D")
        require(scene, 'path="res://scripts/light_sphere_effect.gd"', "Light Sphere scene must reference its effect script")
        require(scene, '[node name="PointLight2D" type="PointLight2D" parent="."]', "Light Sphere scene must contain PointLight2D")


def validate_banishment() -> None:
    text = read_required("scripts/banishment_spell.gd")
    if not text:
        return
    require(text, "class_name BanishmentSpell", "Banishment must define class_name BanishmentSpell")
    require(text, "extends RefCounted", "Banishment spell helper must extend RefCounted")
    require_regex(text, r"MANA_COST\s*:=\s*20\b", "Banishment must cost 20 mana")
    require_regex(text, r"SHADE_BONUS_DAMAGE\s*:=\s*15\b", "Banishment must deal 15 bonus damage to shades")
    require(text, "use_mana(MANA_COST)", "Banishment must deduct mana through ManaComponent")
    require(text, "PhysicsShapeQueryParameters2D", "Banishment must query a 2D physics shape")
    require(text, "intersect_shape", "Banishment must collect enemies with intersect_shape")
    require(text, '"enemies"', "Banishment must affect enemies group members")
    require(text, '"shades"', "Banishment must detect shades group members")
    require(text, "apply_stun", "Banishment must stun affected enemies")
    require(text, "take_damage", "Banishment must damage shades")
    require(text, "_apply_knockback", "Banishment must push affected enemies")
    require(text, "CharacterBody2D", "Banishment knockback must support CharacterBody2D enemies")


def validate_spell_panel() -> None:
    script = read_required("scripts/ui/spell_panel.gd")
    if script:
        require(script, "extends Control", "Spell panel script must extend Control")
        require(script, "KEY_S", "Spell panel must toggle with S")
        require(script, "SpellBook.get_known_spells()", "Spell panel must render known spells from SpellBook")
        require(script, "mana_cost", "Spell panel must show mana costs")

    scene = read_required("scenes/ui/spell_panel.tscn")
    if scene:
        require(scene, 'path="res://scripts/ui/spell_panel.gd"', "Spell panel scene must reference its script")
        require(scene, '[node name="SpellPanel" type="Control"', "Spell panel scene root must be Control")
        require(scene, '[node name="SpellList" type="VBoxContainer"', "Spell panel scene must contain SpellList")


def main() -> int:
    validate_project_autoloads()
    validate_spell_resource_and_book()
    validate_mana_system()
    validate_detect_magic()
    validate_light_sphere()
    validate_banishment()
    validate_spell_panel()

    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1

    print("Validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
