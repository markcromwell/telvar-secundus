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
npc_script = REPO_ROOT / "scripts" / "NPC.gd"
npc_scene = REPO_ROOT / "scenes" / "NPC.tscn"
player_script = REPO_ROOT / "scripts" / "Player.gd"

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

if not npc_script.is_file():
    errors.append(f"Missing NPC script: {npc_script}")
else:
    npc_src = npc_script.read_text(encoding="utf-8")
    for marker in (
        "@export var npc_id",
        'Input.is_action_just_pressed("interact")',
        "func _load_dialogue(",
    ):
        if marker not in npc_src:
            errors.append(f"NPC.gd missing required marker: {marker!r}")

if not npc_scene.is_file():
    errors.append(f"Missing NPC scene: {npc_scene}")
else:
    npc_tscn = npc_scene.read_text(encoding="utf-8")
    if 'type="Area2D"' not in npc_tscn:
        errors.append("NPC.tscn must include root or node type Area2D")
    if "res://scripts/NPC.gd" not in npc_tscn:
        errors.append("NPC.tscn must reference script res://scripts/NPC.gd")
    if "CircleShape2D" not in npc_tscn:
        errors.append("NPC.tscn must define a CircleShape2D for CollisionShape2D")
    if 'type="Sprite2D"' not in npc_tscn:
        errors.append("NPC.tscn must include a Sprite2D child node")

if not player_script.is_file():
    errors.append(f"Missing Player script: {player_script}")
else:
    player_src = player_script.read_text(encoding="utf-8")
    if "var can_move" not in player_src:
        errors.append("Player.gd must declare var can_move")
    if "if not can_move:" not in player_src:
        errors.append("Player.gd _physics_process must guard with if not can_move")

if errors:
    for e in errors:
        print("FAIL:", e)
    sys.exit(1)

print("Structural checks passed")
sys.exit(0)
