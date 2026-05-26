#!/usr/bin/env python3
import sys, os, re
errors = []

# Check files exist
for path in ["project.godot", "MainScene.tscn", "Player.gd", "CREDITS.md"]:
    if not os.path.exists(path):
        errors.append(f"Missing: {path}")

# Check project.godot content
if os.path.exists("project.godot"):
    txt = open("project.godot").read()
    if "viewport_width=1280" not in txt:
        errors.append("project.godot: missing viewport_width=1280")

# Check Player.gd exports
if os.path.exists("Player.gd"):
    txt = open("Player.gd").read()
    if "@export var speed" not in txt:
        errors.append("Player.gd: missing @export var speed")
    if "@export var can_move" not in txt:
        errors.append("Player.gd: missing @export var can_move")
    if "extends CharacterBody2D" not in txt:
        errors.append("Player.gd: missing 'extends CharacterBody2D'")

# Check MainScene.tscn structure
if os.path.exists("MainScene.tscn"):
    txt = open("MainScene.tscn").read()
    if "TileMap" not in txt:
        errors.append("MainScene.tscn: missing TileMap node")
    if "Player" not in txt:
        errors.append("MainScene.tscn: missing Player node")
    if "Player.gd" not in txt:
        errors.append("MainScene.tscn: Player node does not reference Player.gd")

# Check export_presets.cfg for HTML5
if os.path.exists("export_presets.cfg"):
    txt = open("export_presets.cfg").read()
    if "HTML5" not in txt and "Web" not in txt:
        errors.append("export_presets.cfg: missing HTML5/Web preset")
else:
    errors.append("Missing: export_presets.cfg")

if errors:
    for e in errors: print("FAIL:", e)
    sys.exit(1)
print("All checks passed")
sys.exit(0)
