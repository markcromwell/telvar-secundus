#!/usr/bin/env python3
import sys
import os

def main():
    errors = []

    # Check files exist
    required_files = ["project.godot", "MainScene.tscn", "Player.gd", "CREDITS.md"]
    for path in required_files:
        if os.path.exists(path):
            print(f"PASS: {path} exists")
        else:
            print(f"FAIL: Missing {path}")
            errors.append(f"Missing {path}")

    # Check project.godot content
    if os.path.exists("project.godot"):
        with open("project.godot", "r", encoding="utf-8") as f:
            content = f.read()
            if "viewport_width=1280" in content:
                print("PASS: project.godot contains viewport_width=1280")
            else:
                print("FAIL: project.godot missing viewport_width=1280")
                errors.append("project.godot missing viewport_width=1280")

    # Check MainScene.tscn structure
    if os.path.exists("MainScene.tscn"):
        with open("MainScene.tscn", "r", encoding="utf-8") as f:
            content = f.read()
            if 'node name="TileMap"' in content and 'type="TileMap"' in content:
                print("PASS: MainScene.tscn contains TileMap node")
            else:
                print("FAIL: MainScene.tscn missing TileMap node")
                errors.append("MainScene.tscn missing TileMap node")

            if '[node name="Player" type="CharacterBody2D"' in content:
                print("PASS: MainScene.tscn contains Player as CharacterBody2D")
            else:
                print("FAIL: MainScene.tscn Player must be CharacterBody2D")
                errors.append('MainScene.tscn: expected [node name="Player" type="CharacterBody2D"')

            cam_block_ok = (
                'node name="Camera2D" type="Camera2D" parent="Player"' in content
                and "position_smoothing_enabled = true" in content
                and "position_smoothing_speed = 10.0" in content
            )
            if cam_block_ok:
                print("PASS: MainScene.tscn Player has Camera2D with position smoothing")
            else:
                print("FAIL: MainScene.tscn missing Camera2D smoothing under Player")
                errors.append(
                    "MainScene.tscn: Camera2D child of Player must set "
                    "position_smoothing_enabled=true and position_smoothing_speed=10.0"
                )

    # Check Player.gd line-by-line
    if os.path.exists("Player.gd"):
        found_speed = False
        found_can_move = False
        with open("Player.gd", "r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if stripped.startswith("@export") and "var speed" in line:
                    found_speed = True
                if stripped.startswith("@export") and "var can_move" in line:
                    found_can_move = True
        
        if found_speed:
            print("PASS: Player.gd declares speed export")
        else:
            print("FAIL: Player.gd missing speed export")
            errors.append("Player.gd missing speed export")
            
        if found_can_move:
            print("PASS: Player.gd declares can_move export")
        else:
            print("FAIL: Player.gd missing can_move export")
            errors.append("Player.gd missing can_move export")

    if errors:
        sys.exit(1)

    print("All checks passed")
    sys.exit(0)

if __name__ == "__main__":
    main()
