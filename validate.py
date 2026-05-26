#!/usr/bin/env python3
"""
TELVAR-RPG validation script (bootstrap + structural checks).
Full validation is implemented in spec #1246.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent

errors = []

project_godot = REPO_ROOT / "project.godot"
dialogue_manager = REPO_ROOT / "scripts" / "DialogueManager.gd"
dialogue_box = REPO_ROOT / "scenes" / "DialogueBox.tscn"

if not dialogue_manager.is_file():
    errors.append(f"Missing DialogueManager script: {dialogue_manager}")
if not dialogue_box.is_file():
    errors.append(f"Missing DialogueBox scene: {dialogue_box}")
if project_godot.is_file():
    pg = project_godot.read_text(encoding="utf-8")
    if "[autoload]" not in pg:
        errors.append("project.godot missing [autoload] section")
    elif 'DialogueManager="*res://scripts/DialogueManager.gd"' not in pg:
        errors.append(
            'project.godot autoload must include '
            'DialogueManager="*res://scripts/DialogueManager.gd"'
        )
    if "[input]" not in pg:
        errors.append("project.godot missing [input] section")
    elif "interact=" not in pg or (
        'physical_keycode":69' not in pg and "physical_keycode=69" not in pg
    ):
        errors.append(
            "project.godot [input] must define interact with physical_keycode 69 (E)"
        )
    required_dm_markers = (
        "var is_dialogue_active",
        "func show_dialogue(",
        "func hide_dialogue(",
        "func set_flag(",
        "func get_flag(",
    )
    if dialogue_manager.is_file():
        dm_src = dialogue_manager.read_text(encoding="utf-8")
        for marker in required_dm_markers:
            if marker not in dm_src:
                errors.append(f"DialogueManager.gd missing required marker: {marker!r}")
        if "if is_dialogue_active:" not in dm_src:
            errors.append(
                "DialogueManager.show_dialogue must guard on is_dialogue_active"
            )

if errors:
    for e in errors:
        print("FAIL:", e)
    sys.exit(1)

print("Structural checks passed")
sys.exit(0)
