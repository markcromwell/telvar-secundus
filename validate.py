#!/usr/bin/env python3
"""
TELVAR-RPG validation script (bootstrap + structural checks).
Full validation is implemented in spec #1246.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent

errors = []

required_files = [
    REPO_ROOT / "project.godot",
    REPO_ROOT / "scenes/combat_ui.tscn",
    REPO_ROOT / "scripts/combat_ui.gd",
    REPO_ROOT / "scripts/combat_manager.gd",
]
for path in required_files:
    if not path.is_file():
        errors.append(f"Missing required file: {path.relative_to(REPO_ROOT)}")

project_path = REPO_ROOT / "project.godot"
if project_path.is_file():
    project_text = project_path.read_text(encoding="utf-8")
    if "CombatManager=" not in project_text or "scripts/combat_manager.gd" not in project_text:
        errors.append("project.godot must autoload CombatManager at scripts/combat_manager.gd")
    if "run/main_scene" not in project_text or "combat_ui.tscn" not in project_text:
        errors.append("project.godot should set run/main_scene to scenes/combat_ui.tscn")

combat_scene = REPO_ROOT / "scenes/combat_ui.tscn"
if combat_scene.is_file():
    tscn = combat_scene.read_text(encoding="utf-8")
    for needle in ("CanvasLayer", "ProgressBar", "VBoxContainer", "Attack", "Cast Spell", "Flee", "Use Item"):
        if needle not in tscn:
            errors.append(f"scenes/combat_ui.tscn must contain {needle!r}")

if errors:
    for e in errors:
        print("FAIL:", e)
    sys.exit(1)

print("Structural checks passed.")
sys.exit(0)
