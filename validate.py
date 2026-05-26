#!/usr/bin/env python3
"""
TELVAR-RPG validation script (bootstrap + phase checks).
Structural checks only — no Godot runtime.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
errors: list[str] = []

for rel in (
    "scenes/game_over.tscn",
    "scripts/game_over.gd",
    "scenes/room.tscn",
    "scripts/room.gd",
    "scenes/wings.tscn",
    "scripts/wings.gd",
    "scenes/dialogue_box.tscn",
    "scripts/dialogue_box.gd",
    "scripts/dialogue_manager.gd",
    "assets/dialogue/myramar.json",
):
    p = REPO / rel
    if not p.is_file():
        errors.append(f"Missing required file: {rel}")

proj = REPO / "project.godot"
if proj.is_file():
    pg = proj.read_text(encoding="utf-8")
    if "DialogueManager=" not in pg or "scripts/dialogue_manager.gd" not in pg:
        errors.append("project.godot must autoload DialogueManager from scripts/dialogue_manager.gd")
    if 'run/main_scene="res://scenes/room.tscn"' not in pg:
        errors.append('project.godot should set run/main_scene to res://scenes/room.tscn')
else:
    errors.append("Missing required file: project.godot")

room_scene = REPO / "scenes" / "room.tscn"
if room_scene.is_file():
    body = room_scene.read_text(encoding="utf-8")
    if 'path="res://scripts/room.gd"' not in body:
        errors.append("room.tscn must ext_resource scripts/room.gd")
    for m in re.finditer(r'\[ext_resource[^\]]*path="(res://[^"]+)"', body):
        res_path = m.group(1)
        rel_asset = res_path.removeprefix("res://")
        candidate = REPO / rel_asset
        if not candidate.is_file():
            errors.append(f"room.tscn references missing resource: {rel_asset}")

db_scene = REPO / "scenes" / "dialogue_box.tscn"
if db_scene.is_file():
    body = db_scene.read_text(encoding="utf-8")
    if 'path="res://scripts/dialogue_box.gd"' not in body:
        errors.append("dialogue_box.tscn must ext_resource scripts/dialogue_box.gd")
    for need in ("NameLabel", "TextLabel", "ChoicesContainer"):
        if need not in body:
            errors.append(f"dialogue_box.tscn must contain node {need}")
    for m in re.finditer(r'\[ext_resource[^\]]*path="(res://[^"]+)"', body):
        res_path = m.group(1)
        rel_asset = res_path.removeprefix("res://")
        candidate = REPO / rel_asset
        if not candidate.is_file():
            errors.append(f"dialogue_box.tscn references missing resource: {rel_asset}")

go_scene = REPO / "scenes" / "game_over.tscn"
if go_scene.is_file():
    body = go_scene.read_text(encoding="utf-8")
    if 'path="res://scripts/game_over.gd"' not in body:
        errors.append("game_over.tscn must ext_resource scripts/game_over.gd")
    for m in re.finditer(r'\[ext_resource[^\]]*path="(res://[^"]+)"', body):
        res_path = m.group(1)
        rel_asset = res_path.removeprefix("res://")
        candidate = REPO / rel_asset
        if not candidate.is_file():
            errors.append(f"game_over.tscn references missing resource: {rel_asset}")

if errors:
    for e in errors:
        print("FAIL:", e)
    sys.exit(1)

print("Validation checks passed.")
sys.exit(0)
