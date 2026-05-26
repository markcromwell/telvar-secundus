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

for rel in ("scenes/game_over.tscn", "scripts/game_over.gd"):
    p = REPO / rel
    if not p.is_file():
        errors.append(f"Missing required file: {rel}")

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
