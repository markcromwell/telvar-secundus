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


def _read(rel: str) -> str:
    path = REPO / rel
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8")


def _require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        _fail(label)


def _require_regex(text: str, pattern: str, label: str) -> None:
    if re.search(pattern, text) is None:
        _fail(label)


def _check_spell_resource_script() -> None:
    text = _read("resources/spell.gd")
    if not text:
        return
    _require(text, "class_name Spell", "spell.gd: expected class_name Spell")
    _require(text, "extends Resource", "spell.gd: Spell must extend Resource")
    for prop in ("spell_id", "spell_name", "mana_cost", "damage", "effect"):
        _require_regex(
            text,
            rf"@export\s+var\s+{prop}\s*:",
            f"spell.gd: expected exported {prop} property",
        )


def _check_spell_book() -> None:
    text = _read("autoload/spell_book.gd")
    if not text:
        return
    _require(
        text,
        'BANISHMENT_PATH := "res://resources/spells/banishment.tres"',
        "spell_book.gd: must load the Banishment spell resource",
    )
    _require(text, "LEARNABLE_CATALOG", "spell_book.gd: missing learnable spell catalog")
    for spell_id in ("ember", "shield_light", "reveal"):
        _require(text, spell_id, f"spell_book.gd: learnable catalog missing {spell_id}")
    _require(text, "func get_learnable_display_lines", "spell_book.gd: missing learnable display helper")
    _require(text, "func regen_mana_combat_tick", "spell_book.gd: missing combat mana regen")
    _require(text, "var copper: int = 0", "spell_book.gd: must track copper")
    _require(text, "func grant_copper", "spell_book.gd: missing copper grant API")
    _require(text, "DEFEAT_RESPAWN_HP := 15", "spell_book.gd: defeat respawn HP must be 15")
    _require(text, "var player_hp", "spell_book.gd: must track player HP for respawn")
    _require(text, "func record_last_save_point", "spell_book.gd: missing last save point API")
    _require(text, "func apply_defeat_respawn_state", "spell_book.gd: missing defeat respawn API")


def _check_spell_combat() -> None:
    text = _read("scripts/combat/spell_combat.gd")
    if not text:
        return
    checks = {
        "BANISHMENT_PUSH_TILES := 3": "spell_combat.gd: Banishment must push 3 tiles",
        "BANISHMENT_STUN_TURNS := 1": "spell_combat.gd: Banishment must stun for 1 turn",
        "BANISHMENT_SHADE_DAMAGE := 15": "spell_combat.gd: Banishment must deal 15 damage to Shades",
        'kind == "thug"': "spell_combat.gd: missing Thug Banishment branch",
        'kind == "shade"': "spell_combat.gd: missing Shade Banishment branch",
        "THUG_VICTORY_COPPER_MIN := 1": "spell_combat.gd: Thug copper min must be 1",
        "THUG_VICTORY_COPPER_MAX := 3": "spell_combat.gd: Thug copper max must be 3",
        "func roll_thug_victory_copper": "spell_combat.gd: missing Thug copper loot roller",
        "randi_range": "spell_combat.gd: copper loot should roll a range",
    }
    for needle, label in checks.items():
        _require(text, needle, label)


def _check_main_defeat_overlay() -> None:
    text = _read("scenes/main.tscn")
    if not text:
        return
    if "DefeatCanvas" not in text or "DefeatFadeRect" not in text:
        _fail("main.tscn: expected DefeatCanvas / DefeatFadeRect for defeat fade")
    _require_regex(
        text,
        r'\[node\s+name="DefeatFadeRect"\s+type="ColorRect"',
        "main.tscn: DefeatFadeRect must be a ColorRect",
    )
    _require(text, "color = Color(0, 0, 0, 1)", "main.tscn: defeat fade must be black")


def _check_main_victory_wiring() -> None:
    text = _read("scenes/main.tscn")
    if not text:
        return
    for needle in ("VictoryCanvas", "VictoryLabel", "VictorySFX", "VictoryTimer"):
        _require(text, needle, f"main.tscn: missing {needle}")
    _require(text, "victory_sting.wav", "main.tscn: VictorySFX must reference victory_sting.wav")
    _require_regex(
        text,
        r'\[node\s+name="VictorySFX"\s+type="AudioStreamPlayer"',
        "main.tscn: VictorySFX must be an AudioStreamPlayer",
    )
    _require(text, 'text = "Victory!"', "main.tscn: VictoryLabel should show victory text")


def _check_main_script() -> None:
    text = _read("scenes/main.gd")
    if not text:
        return
    for needle, label in {
        "_unhandled_input": "main.gd: missing input handler",
        "toggle_cast_spell": "main.gd: missing S-key spell panel action",
        "play_thug_victory_fanfare": "main.gd: missing victory fanfare API",
        "thug_victory_fanfare": "main.gd: missing victory fanfare group",
        "SpellCombat.roll_thug_victory_copper": "main.gd: victory must roll Thug copper",
        "SpellBook.grant_copper": "main.gd: victory must grant copper",
        "_victory_sfx.play": "main.gd: victory must play SFX",
        "play_defeat_fade_and_respawn": "main.gd: missing defeat respawn API",
        "defeat_respawn_handler": "main.gd: missing defeat respawn group",
        "SpellBook.apply_defeat_respawn_state": "main.gd: defeat must apply respawn state",
    }.items():
        _require(text, needle, label)
    if "reload_current_scene" not in text and "change_scene_to_file" not in text:
        _fail("main.gd: defeat respawn must reload or change to the last save scene")


def _check_cast_spell_panel_scene() -> None:
    text = _read("scenes/ui/cast_spell_panel.tscn")
    if not text:
        return
    if "[gd_scene" not in text:
        _fail("cast_spell_panel.tscn: missing [gd_scene header")
    if "cast_spell_panel.gd" not in text:
        _fail("cast_spell_panel.tscn: must reference cast_spell_panel.gd")
    if re.search(r"\[node\s+name=\"CastSpellPanel\"", text) is None:
        _fail("cast_spell_panel.tscn: expected CastSpellPanel root node")
    for node in ("ManaLabel", "KnownList", "LearnableList"):
        _require(text, f'name="{node}"', f"cast_spell_panel.tscn: missing {node}")


def _check_cast_spell_panel_script() -> None:
    text = _read("ui/cast_spell_panel.gd")
    if not text:
        return
    for needle, label in {
        "func toggle_visible": "cast_spell_panel.gd: missing panel toggle API",
        "SpellBook.mana_current": "cast_spell_panel.gd: must display current mana",
        "SpellBook.mana_max": "cast_spell_panel.gd: must display max mana",
        "SpellBook.copper": "cast_spell_panel.gd: must display copper",
        "SpellBook.get_learnable_display_lines": "cast_spell_panel.gd: must display learnable spells",
        "known_spells": "cast_spell_panel.gd: must display known spells",
    }.items():
        _require(text, needle, label)


def _check_project_autoload() -> None:
    text = _read("project.godot")
    if not text:
        return
    if "[autoload]" not in text:
        _fail("project.godot: missing [autoload] section")
    if "SpellBook" not in text or "spell_book.gd" not in text:
        _fail("project.godot: SpellBook autoload must point to spell_book.gd")
    if "toggle_cast_spell" not in text or "83" not in text:
        _fail("project.godot: toggle_cast_spell input action must be bound to S")


def _check_banishment_tres() -> None:
    text = _read("resources/spells/banishment.tres")
    if not text:
        return
    _require(text, 'script = ExtResource("1_spell")', "banishment.tres: must use Spell script")
    _require_regex(text, r"spell_id\s*=\s*\"banishment\"", "banishment.tres: spell_id must be banishment")
    _require_regex(text, r"spell_name\s*=\s*\"Banishment\"", "banishment.tres: spell_name must be Banishment")
    _require_regex(text, r"mana_cost\s*=\s*5", "banishment.tres: mana_cost must be 5")
    _require_regex(text, r"damage\s*=\s*15", "banishment.tres: damage must be 15")
    _require_regex(text, r"effect\s*=\s*\"banishment\"", "banishment.tres: effect must be banishment")


def _check_audio_asset() -> None:
    path = REPO / "assets/audio/victory_sting.wav"
    if not path.is_file():
        return
    if path.stat().st_size <= 0:
        _fail("victory_sting.wav: file must not be empty")
    if path.stat().st_size >= 5_000_000:
        _fail("victory_sting.wav: asset must stay web-safe (<5MB)")


def main() -> int:
    _check_files()
    _check_project_autoload()
    _check_spell_resource_script()
    _check_banishment_tres()
    _check_spell_book()
    _check_spell_combat()
    _check_main_victory_wiring()
    _check_main_defeat_overlay()
    _check_main_script()
    _check_cast_spell_panel_scene()
    _check_cast_spell_panel_script()
    _check_audio_asset()
    if ERRORS:
        for e in ERRORS:
            print("FAIL:", e)
        return 1
    print("Validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
