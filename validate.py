#!/usr/bin/env python3
"""
TELVAR-RPG validation script (bootstrap stub).
Full validation is implemented in spec #1246.
During early development, this exits 0 to allow the pipeline to proceed.
"""
import re
import sys
from pathlib import Path

# Bootstrap mode: check only what is strictly required at this stage
errors = []

_REPO = Path(__file__).resolve().parent
_REQUIRED_PATHS = [
    _REPO / "scripts/resources/item.gd",
    _REPO / "scripts/inventory/inventory.gd",
    _REPO / "resources/items/wizard_band_red.tres",
    _REPO / "scripts/player/Player.gd",
    _REPO / "scenes/player/Player.tscn",
    _REPO / "assets/sprites/wizard_band_red_wrist.png",
    _REPO / "scenes/ui/obtain_card.tscn",
    _REPO / "scripts/ui/obtain_card.gd",
    _REPO / "scripts/story/award_ceremony.gd",
]
_WIZARD_BAND = _REPO / "resources/items/wizard_band_red.tres"
_PLAYER_SCENE = _REPO / "scenes/player/Player.tscn"
_PLAYER_SCRIPT = _REPO / "scripts/player/Player.gd"

_OBTAIN_SCENE = _REPO / "scenes/ui/obtain_card.tscn"
_OBTAIN_SCRIPT = _REPO / "scripts/ui/obtain_card.gd"
_AWARD_CEREMONY = _REPO / "scripts/story/award_ceremony.gd"


def _scene_node_block(scene_text, node_name):
    match = re.search(
        rf'^\[node name="{re.escape(node_name)}"(?P<header>[^\]]*)\]\n'
        r'(?P<body>.*?)(?=^\[|\Z)',
        scene_text,
        re.MULTILINE | re.DOTALL,
    )
    return match


for path in _REQUIRED_PATHS:
    if not path.is_file():
        errors.append(f"Missing required file: {path.relative_to(_REPO)}")

if _WIZARD_BAND.is_file():
    band_text = _WIZARD_BAND.read_text(encoding="utf-8")
    if '[gd_resource type="Resource"' not in band_text:
        errors.append("wizard_band_red.tres must be a Godot Resource")
    if 'path="res://scripts/resources/item.gd"' not in band_text:
        errors.append("wizard_band_red.tres must use scripts/resources/item.gd")
    if 'id = "wizard_band_red"' not in band_text:
        errors.append("wizard_band_red.tres must define id wizard_band_red")
    if 'display_name = "Red Wizard Band"' not in band_text:
        errors.append("wizard_band_red.tres must define display_name Red Wizard Band")
    if not re.search(r'tags\s*=\s*PackedStringArray\([^)]*"magical"', band_text):
        errors.append("wizard_band_red.tres must include the magical tag")

if _PLAYER_SCENE.is_file():
    player_scene = _PLAYER_SCENE.read_text(encoding="utf-8")
    wrist_band = _scene_node_block(player_scene, "WristBand")
    if not wrist_band or 'type="Sprite2D"' not in wrist_band.group("header"):
        errors.append("Player.tscn must define a WristBand Sprite2D node")
    elif 'texture = ExtResource(' not in wrist_band.group("body"):
        errors.append("Player.tscn WristBand node must assign a texture")
    if 'path="res://assets/sprites/wizard_band_red_wrist.png"' not in player_scene:
        errors.append("Player.tscn must reference assets/sprites/wizard_band_red_wrist.png")

if _PLAYER_SCRIPT.is_file():
    player_gd = _PLAYER_SCRIPT.read_text(encoding="utf-8")
    if "func set_wrist_band_visible" not in player_gd:
        errors.append("Player.gd must define set_wrist_band_visible")

if _OBTAIN_SCENE.is_file():
    obtain_scene = _OBTAIN_SCENE.read_text(encoding="utf-8")
    if "obtain_card.gd" not in obtain_scene:
        errors.append("obtain_card.tscn must attach scripts/ui/obtain_card.gd")
    if "CanvasLayer" not in obtain_scene:
        errors.append("obtain_card.tscn must use a CanvasLayer root for overlay UI")

if _OBTAIN_SCRIPT.is_file():
    obtain_gd = _OBTAIN_SCRIPT.read_text(encoding="utf-8")
    if "func show_for_item" not in obtain_gd:
        errors.append("obtain_card.gd must define show_for_item")
    if "extends CanvasLayer" not in obtain_gd:
        errors.append("obtain_card.gd must extend CanvasLayer")

if _AWARD_CEREMONY.is_file():
    ceremony_gd = _AWARD_CEREMONY.read_text(encoding="utf-8")
    if "class_name AwardCeremony" not in ceremony_gd:
        errors.append("award_ceremony.gd must define class_name AwardCeremony")
    if "func complete_award" not in ceremony_gd:
        errors.append("award_ceremony.gd must define complete_award")
    if "add_item" not in ceremony_gd:
        errors.append("award_ceremony.gd must add the item via inventory.add_item")
    if "set_wrist_band_visible" not in ceremony_gd:
        errors.append("award_ceremony.gd must call set_wrist_band_visible on the player")
    if "show_for_item" not in ceremony_gd:
        errors.append("award_ceremony.gd must call show_for_item on obtain UI")

# Only enforce critical structural checks here
# (Full validation in spec 1246)

if errors:
    for e in errors:
        print("FAIL:", e)
    sys.exit(1)

print("Bootstrap checks passed (spec 1246 will add full validation)")
sys.exit(0)
