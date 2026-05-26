#!/usr/bin/env python3
"""
TELVAR-RPG validation script (bootstrap stub).
Full validation is implemented in spec #1246.
Checks critical paths for the sealed door phase (2708) plus bootstrap success.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent

errors: list[str] = []

required_paths = [
    REPO_ROOT / "scenes/world/sealed_door.tscn",
    REPO_ROOT / "scripts/world/SealedDoor.gd",
    REPO_ROOT / "scripts/autoload/Inventory.gd",
    REPO_ROOT / "resources/items/item_table.tres",
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

if errors:
    for e in errors:
        print("FAIL:", e)
    sys.exit(1)

print("Validation passed (sealed door + bootstrap).")
sys.exit(0)
