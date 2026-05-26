#!/usr/bin/env python3
"""
TELVAR-RPG validation script (bootstrap stub).
Full validation is implemented in spec #1246.
Checks critical paths for the sealed door / Veneficturis wing (phase 2709) plus bootstrap success.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent

errors: list[str] = []

required_paths = [
    REPO_ROOT / "scenes/world/sealed_door.tscn",
    REPO_ROOT / "scenes/world/wizard_academy.tscn",
    REPO_ROOT / "scripts/world/SealedDoor.gd",
    REPO_ROOT / "scripts/autoload/Inventory.gd",
    REPO_ROOT / "resources/items/item_table.tres",
    REPO_ROOT / "resources/items/sealed_wing_key.tres",
    REPO_ROOT / "resources/tilesets/lpc_terrain.tres",
    REPO_ROOT / "assets/tilesets/lpc_terrain.png",
]

for p in required_paths:
    if not p.is_file():
        errors.append(f"Missing required file: {p.relative_to(REPO_ROOT)}")

project_godot = REPO_ROOT / "project.godot"
if project_godot.is_file():
    text = project_godot.read_text(encoding="utf-8")
    if 'Inventory="*res://scripts/autoload/Inventory.gd"' not in text:
        errors.append("project.godot must autoload Inventory at res://scripts/autoload/Inventory.gd")

sealed_scene = REPO_ROOT / "scenes/world/sealed_door.tscn"
if sealed_scene.is_file():
    st = sealed_scene.read_text(encoding="utf-8")
    for needle in (
        'path="res://scripts/world/SealedDoor.gd"',
        '[node name="DoorPivot" type="Node2D"',
        '[node name="StaticBody2D" type="StaticBody2D"',
        '[node name="InteractArea" type="Area2D"',
    ):
        if needle not in st:
            errors.append(f"sealed_door.tscn missing expected scene structure: {needle!r}")

item_table = REPO_ROOT / "resources/items/item_table.tres"
if item_table.is_file():
    it = item_table.read_text(encoding="utf-8")
    if '&"sealed_wing_key"' not in it:
        errors.append("item_table.tres must register sealed_wing_key")

key_res = REPO_ROOT / "resources/items/sealed_wing_key.tres"
if key_res.is_file():
    kt = key_res.read_text(encoding="utf-8")
    if 'id = &"sealed_wing_key"' not in kt:
        errors.append('sealed_wing_key.tres must define id = &"sealed_wing_key"')

academy = REPO_ROOT / "scenes/world/wizard_academy.tscn"
if academy.is_file():
    ac = academy.read_text(encoding="utf-8")
    for needle in (
        'path="res://scenes/world/sealed_door.tscn"',
        'type="TileMap"',
        'path="res://resources/tilesets/lpc_terrain.tres"',
    ):
        if needle not in ac:
            errors.append(f"wizard_academy.tscn missing expected structure: {needle!r}")
    if "instance=ExtResource(" not in ac:
        errors.append("wizard_academy.tscn must instance the sealed door (PackedScene child)")

tileset = REPO_ROOT / "resources/tilesets/lpc_terrain.tres"
if tileset.is_file():
    tt = tileset.read_text(encoding="utf-8")
    for needle in (
        'path="res://assets/tilesets/lpc_terrain.png"',
        "texture_region_size = Vector2i(16, 16)",
        'type="TileSetAtlasSource"',
    ):
        if needle not in tt:
            errors.append(f"lpc_terrain.tres missing expected tileset structure: {needle!r}")

if errors:
    for e in errors:
        print("FAIL:", e)
    sys.exit(1)

print("Validation passed (wizard academy tilemap, sealed door, Sealed Wing Key, bootstrap).")
sys.exit(0)
