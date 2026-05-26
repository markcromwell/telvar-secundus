#!/usr/bin/env python3
"""
TELVAR-RPG validation script (bootstrap stub).
Full validation is implemented in spec #1246.
During early development, this exits 0 to allow the pipeline to proceed.
"""
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
]
_WIZARD_BAND = _REPO / "resources/items/wizard_band_red.tres"
_PLAYER_SCENE = _REPO / "scenes/player/Player.tscn"
_PLAYER_SCRIPT = _REPO / "scripts/player/Player.gd"

_OBTAIN_SCENE = _REPO / "scenes/ui/obtain_card.tscn"
_OBTAIN_SCRIPT = _REPO / "scripts/ui/obtain_card.gd"

for path in _REQUIRED_PATHS:
    if not path.is_file():
        errors.append(f"Missing required file: {path.relative_to(_REPO)}")

if _WIZARD_BAND.is_file():
    band_text = _WIZARD_BAND.read_text(encoding="utf-8")
    if "magical" not in band_text:
        errors.append("wizard_band_red.tres must include the magical tag")
    if "wizard_band_red" not in band_text:
        errors.append("wizard_band_red.tres must define id wizard_band_red")

if _PLAYER_SCENE.is_file():
    player_scene = _PLAYER_SCENE.read_text(encoding="utf-8")
    if 'name="WristBand"' not in player_scene or "type=\"Sprite2D\"" not in player_scene:
        errors.append("Player.tscn must define a WristBand Sprite2D node")
    if "wizard_band_red_wrist.png" not in player_scene:
        errors.append("Player.tscn must reference the wrist band texture")

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

# Only enforce critical structural checks here
# (Full validation in spec 1246)

if errors:
    for e in errors:
        print("FAIL:", e)
    sys.exit(1)

print("Bootstrap checks passed (spec 1246 will add full validation)")
sys.exit(0)
