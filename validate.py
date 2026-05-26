#!/usr/bin/env python3
"""Structural validation for the Godot game project (no Godot runtime)."""
from __future__ import annotations

import re
import sys
from pathlib import Path


def fail(msg: str) -> None:
    print(f"validate: FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    root = Path(__file__).resolve().parent
    game = root / "game"
    project = game / "project.godot"
    scene = game / "scenes" / "Player.tscn"
    texture = game / "assets" / "sprites" / "lpc_base.png"

    if not project.is_file():
        fail(f"missing {project.relative_to(root)}")

    proj_text = project.read_text(encoding="utf-8")
    if "config_version=5" not in proj_text:
        fail("project.godot must contain config_version=5")
    if 'run/main_scene="res://scenes/Player.tscn"' not in proj_text:
        fail('run/main_scene must be "res://scenes/Player.tscn"')

    if not scene.is_file():
        fail(f"missing {scene.relative_to(root)}")

    tscn = scene.read_text(encoding="utf-8")
    if not re.search(
        r'\[node\s+name="Player"\s+type="CharacterBody2D"\s*\]',
        tscn,
    ):
        fail("Player.tscn root must be CharacterBody2D named Player")

    if not re.search(r'\[node\s+name="Sprite2D"\s+type="Sprite2D"', tscn):
        fail("Player.tscn must contain Sprite2D child named Sprite2D")

    if "res://assets/sprites/lpc_base.png" not in tscn:
        fail("Sprite2D must reference res://assets/sprites/lpc_base.png")

    if not re.search(r'\[node\s+name="CollisionShape2D"\s+type="CollisionShape2D"', tscn):
        fail("Player.tscn must contain CollisionShape2D child")

    if not re.search(
        r'\[node\s+name="Camera2D"\s+type="Camera2D"\s+parent="\."\s*\]',
        tscn,
    ):
        fail("Player.tscn must contain Camera2D as a direct child of the root node")

    if "position_smoothing_enabled = true" not in tscn:
        fail("Player.tscn Camera2D must set position_smoothing_enabled = true")

    if "position_smoothing_speed = 0.1" not in tscn:
        fail("Player.tscn Camera2D must set position_smoothing_speed = 0.1")

    if "current = true" not in tscn:
        fail("Player.tscn Camera2D must set current = true")

    if "shape = SubResource(" not in tscn:
        fail("CollisionShape2D must assign a SubResource shape")

    if not re.search(
        r'\[sub_resource\s+type="RectangleShape2D"',
        tscn,
    ):
        fail("Player.tscn must define a non-null RectangleShape2D sub-resource")

    if not texture.is_file():
        fail(f"missing texture {texture.relative_to(root)}")

    print("validate: OK")


if __name__ == "__main__":
    main()
