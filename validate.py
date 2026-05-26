#!/usr/bin/env python3
"""
TELVAR-RPG structural validation (Godot 4.x text resources).

Parses .tscn / .tres with line-oriented checks — no Godot binary.
Prefers dedicated UI scenes under scenes/ui/ when present; otherwise
validates the same node structure inside scenes/hud.tscn (bootstrap layout).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent

# Files required for spell / mana pipeline
REQUIRED_FILES = [
    REPO_ROOT / "scripts" / "spell.gd",
    REPO_ROOT / "scripts" / "spell_book.gd",
    REPO_ROOT / "scripts" / "mana_component.gd",
    REPO_ROOT / "resources" / "spells" / "ember.tres",
    REPO_ROOT / "resources" / "spells" / "shield_light.tres",
    REPO_ROOT / "resources" / "spells" / "reveal.tres",
]

SPELL_PANEL_SCENE = REPO_ROOT / "scenes" / "ui" / "spell_panel.tscn"
MANA_BAR_SCENE = REPO_ROOT / "scenes" / "ui" / "mana_bar.tscn"
HUD_SCENE = REPO_ROOT / "scenes" / "hud.tscn"

NODE_HEADER_RE = re.compile(
    r'^\[node\s+name="(?P<name>[^"]+)"\s+type="(?P<type>[^"]+)"'
    r'(?:\s+parent="(?P<parent>[^"]*)")?\s*\]\s*$'
)

SPELL_TRES_EXPECTED = {
    "ember.tres": "ember",
    "shield_light.tres": "shield_light",
    "reveal.tres": "reveal",
}


def _fail(errors: list[str], msg: str) -> None:
    errors.append(msg)


def _parse_tscn_nodes(text: str) -> list[dict[str, str]]:
    """Return dicts with keys name, type, parent (parent may be empty)."""
    nodes: list[dict[str, str]] = []
    for line in text.splitlines():
        m = NODE_HEADER_RE.match(line.strip())
        if not m:
            continue
        nodes.append(
            {
                "name": m.group("name"),
                "type": m.group("type"),
                "parent": m.group("parent") or "",
            }
        )
    return nodes


def _load_spell_panel_text(errors: list[str]) -> tuple[str, str] | None:
    if SPELL_PANEL_SCENE.is_file():
        return (str(SPELL_PANEL_SCENE.relative_to(REPO_ROOT)), SPELL_PANEL_SCENE.read_text(encoding="utf-8"))
    if HUD_SCENE.is_file():
        return (str(HUD_SCENE.relative_to(REPO_ROOT)), HUD_SCENE.read_text(encoding="utf-8"))
    _fail(
        errors,
        "Spell panel: missing scenes/ui/spell_panel.tscn and fallback scenes/hud.tscn",
    )
    return None


def _load_mana_bar_text(errors: list[str]) -> tuple[str, str] | None:
    if MANA_BAR_SCENE.is_file():
        return (str(MANA_BAR_SCENE.relative_to(REPO_ROOT)), MANA_BAR_SCENE.read_text(encoding="utf-8"))
    if HUD_SCENE.is_file():
        return (str(HUD_SCENE.relative_to(REPO_ROOT)), HUD_SCENE.read_text(encoding="utf-8"))
    _fail(errors, "Mana bar: missing scenes/ui/mana_bar.tscn and fallback scenes/hud.tscn")
    return None


def _validate_spell_panel_scene(label: str, text: str, errors: list[str]) -> None:
    nodes = _parse_tscn_nodes(text)
    types = {n["type"] for n in nodes}
    if "PanelContainer" not in types:
        _fail(errors, f"{label}: expected a PanelContainer (spell panel root)")
    if "VBoxContainer" not in types:
        _fail(errors, f"{label}: expected a VBoxContainer for spell panel layout")
    spell_slots = [n for n in nodes if n["name"] == "SpellSlots" and n["type"] == "VBoxContainer"]
    if not spell_slots:
        _fail(errors, f"{label}: missing SpellSlots VBoxContainer")
    slot_buttons = [
        n
        for n in nodes
        if n["type"] == "Button" and "SpellSlots" in n["parent"]
    ]
    if len(slot_buttons) < 3:
        _fail(
            errors,
            f"{label}: expected at least 3 Button children under SpellSlots (found {len(slot_buttons)})",
        )


def _validate_mana_bar_scene(label: str, text: str, errors: list[str]) -> None:
    nodes = _parse_tscn_nodes(text)
    mana_nodes = [n for n in nodes if n["name"] == "ManaBar" and n["type"] == "ProgressBar"]
    if not mana_nodes:
        _fail(errors, f"{label}: missing ManaBar ProgressBar node")
    # HUD mana tint #4488ff → Color(0.266667, 0.533333, 1, …) in StyleBoxFlat
    if "0.266667" not in text or "0.533333" not in text:
        _fail(
            errors,
            f"{label}: mana fill color should approximate #4488ff "
            "(expected 0.266667 / 0.533333 in Color or StyleBoxFlat)",
        )


def _validate_spell_tres(path: Path, errors: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    rel = path.relative_to(REPO_ROOT)
    if 'path="res://scripts/spell.gd"' not in text:
        _fail(errors, f"{rel}: must reference res://scripts/spell.gd")
    fname = path.name
    expected_id = SPELL_TRES_EXPECTED.get(fname)
    if expected_id and f'spell_id = "{expected_id}"' not in text:
        _fail(errors, f"{rel}: expected spell_id = \"{expected_id}\"")


def main() -> int:
    errors: list[str] = []

    for path in REQUIRED_FILES:
        if not path.is_file():
            errors.append(f"Missing required file: {path.relative_to(REPO_ROOT)}")

    project_godot = REPO_ROOT / "project.godot"
    if project_godot.is_file():
        pg_text = project_godot.read_text(encoding="utf-8")
        if "SpellBook=" not in pg_text or "scripts/spell_book.gd" not in pg_text:
            errors.append("project.godot must register SpellBook autoload to scripts/spell_book.gd")
    else:
        errors.append("Missing required file: project.godot")

    loaded_spell = _load_spell_panel_text(errors)
    if loaded_spell:
        _validate_spell_panel_scene(loaded_spell[0], loaded_spell[1], errors)

    loaded_mana = _load_mana_bar_text(errors)
    if loaded_mana:
        _validate_mana_bar_scene(loaded_mana[0], loaded_mana[1], errors)

    for path in (
        REPO_ROOT / "resources" / "spells" / "ember.tres",
        REPO_ROOT / "resources" / "spells" / "shield_light.tres",
        REPO_ROOT / "resources" / "spells" / "reveal.tres",
    ):
        if path.is_file():
            _validate_spell_tres(path, errors)

    if errors:
        for e in errors:
            print("FAIL:", e)
        return 1

    print("Validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
