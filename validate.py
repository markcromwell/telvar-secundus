#!/usr/bin/env python3
"""
TELVAR-RPG validation script (bootstrap + phase checks).
Structural checks only — no Godot runtime.
"""
from __future__ import annotations

import json
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

myramar_json = REPO / "assets" / "dialogue" / "myramar.json"
if myramar_json.is_file():
    try:
        myramar_data = json.loads(myramar_json.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"myramar.json is not valid JSON: {exc}")
    else:
        if not isinstance(myramar_data, list):
            errors.append("myramar.json root must be a JSON array")
        else:
            has_walk_away_choice = False
            has_walk_in_choice = False
            for i, entry in enumerate(myramar_data):
                if not isinstance(entry, dict):
                    errors.append(f"myramar.json entry {i} must be an object")
                    continue
                for j, choice in enumerate(entry.get("choices") or []):
                    if not isinstance(choice, dict):
                        errors.append(f"myramar.json entry {i} choice {j} must be an object")
                        continue
                    text = str(choice.get("text", ""))
                    if text == "Walk away":
                        has_walk_away_choice = True
                    if "Walk in" in text:
                        has_walk_in_choice = True
            if not has_walk_away_choice:
                errors.append("myramar.json must include a choice labeled exactly 'Walk away'")
            if not has_walk_in_choice:
                errors.append(
                    "myramar.json must include a choice whose text contains 'Walk in' "
                    "(e.g. 'Walk into the wings')"
                )

go_scene = REPO / "scenes" / "game_over.tscn"
if go_scene.is_file():
    body = go_scene.read_text(encoding="utf-8")
    if 'path="res://scripts/game_over.gd"' not in body:
        errors.append("game_over.tscn must ext_resource scripts/game_over.gd")
    if '[node name="GameOver" type="Control"]' not in body:
        errors.append('game_over.tscn must have root Control node named "GameOver"')
    for need in ("LoadLastSaveButton", "ErrorLabel", "Title", "Prompt"):
        if need not in body:
            errors.append(f"game_over.tscn must contain node {need}")
    if "Load last save" not in body:
        errors.append('game_over.tscn must show button text including "Load last save"')
    if "Game Over" not in body:
        errors.append('game_over.tscn must show title text "Game Over"')
    if "Load from your last save" not in body:
        errors.append("game_over.tscn must prompt loading from last save in label copy")
    if 'method="_on_load_last_save_pressed"' not in body or 'signal="pressed"' not in body:
        errors.append(
            "game_over.tscn must connect LoadLastSaveButton pressed to _on_load_last_save_pressed"
        )
    if "unique_name_in_owner = true" not in body:
        errors.append("game_over.tscn should set unique_name_in_owner on script-targeted nodes")
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
