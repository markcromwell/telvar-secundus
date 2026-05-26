#!/usr/bin/env python3
"""Structural validation for Telvar Secundus Godot project (no Godot binary).

Checks file presence and text-format scene/script structure. Exit 0 on success.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent

SETTINGS_MENU_SCENE = REPO_ROOT / "settings_menu.tscn"
MAIN_MENU_SCENE = REPO_ROOT / "main_menu.tscn"
GAME_WORLD_SCENE = REPO_ROOT / "game_world.tscn"
PROJECT_GODOT = REPO_ROOT / "project.godot"


def _fail(msg: str) -> None:
    print("FAIL:", msg)


def _check_settings_menu_scene() -> list[str]:
    errs: list[str] = []
    if not SETTINGS_MENU_SCENE.is_file():
        errs.append(f"Missing {SETTINGS_MENU_SCENE.name}")
        return errs
    text = SETTINGS_MENU_SCENE.read_text(encoding="utf-8")
    if 'name="SettingsMenu"' not in text:
        errs.append("settings_menu.tscn: root node must be named SettingsMenu")
    if 'type="Control"' not in text:
        errs.append("settings_menu.tscn: expected Control node(s)")
    if text.count('type="HSlider"') != 3:
        errs.append("settings_menu.tscn: expected exactly 3 HSlider nodes")
    for name in ("MasterSlider", "MusicSlider", "SfxSlider"):
        if f'name="{name}"' not in text:
            errs.append(f"settings_menu.tscn: missing slider {name}")
    if "min_value = 0.0" not in text or "max_value = 100.0" not in text:
        errs.append("settings_menu.tscn: sliders must use 0–100 range")
    return errs


def _check_main_menu_settings_access() -> list[str]:
    errs: list[str] = []
    if not MAIN_MENU_SCENE.is_file():
        errs.append("Missing main_menu.tscn")
        return errs
    text = MAIN_MENU_SCENE.read_text(encoding="utf-8")
    if 'path="res://settings_menu.tscn"' not in text:
        errs.append("main_menu.tscn: must reference res://settings_menu.tscn")
    if "instance=ExtResource(" not in text:
        errs.append("main_menu.tscn: must instance the settings scene")
    if 'name="SettingsMenu"' not in text or "SettingsHost" not in text:
        errs.append("main_menu.tscn: expected SettingsHost with SettingsMenu instance")
    if 'name="SettingsButton"' not in text:
        errs.append("main_menu.tscn: expected SettingsButton for menu access")
    return errs


def _check_game_world_pause_settings() -> list[str]:
    errs: list[str] = []
    if not GAME_WORLD_SCENE.is_file():
        errs.append("Missing game_world.tscn")
        return errs
    text = GAME_WORLD_SCENE.read_text(encoding="utf-8")
    if 'path="res://settings_menu.tscn"' not in text:
        errs.append("game_world.tscn: must reference res://settings_menu.tscn")
    if 'name="PauseLayer"' not in text:
        errs.append("game_world.tscn: expected PauseLayer for in-game pause")
    if 'path="res://pause_layer.gd"' not in text:
        errs.append("game_world.tscn: PauseLayer must use pause_layer.gd")
    if 'path="res://pause_input.gd"' not in text:
        errs.append("game_world.tscn: expected pause_input.gd for ESC handling")
    if "SettingsHost" not in text or 'name="SettingsMenu"' not in text:
        errs.append("game_world.tscn: expected SettingsHost with SettingsMenu instance")
    if 'name="SettingsButton"' not in text:
        errs.append("game_world.tscn: expected pause SettingsButton")
    return errs


def _check_run_main_scene() -> list[str]:
    errs: list[str] = []
    if not PROJECT_GODOT.is_file():
        errs.append("Missing project.godot")
        return errs
    text = PROJECT_GODOT.read_text(encoding="utf-8")
    if 'run/main_scene="res://main_menu.tscn"' not in text:
        errs.append('project.godot: run/main_scene must be res://main_menu.tscn')
    return errs


def main() -> int:
    errors: list[str] = []
    errors.extend(_check_settings_menu_scene())
    errors.extend(_check_main_menu_settings_access())
    errors.extend(_check_game_world_pause_settings())
    errors.extend(_check_run_main_scene())
    if errors:
        for e in errors:
            _fail(e)
        return 1
    print("Validation OK: SettingsMenu structure; Main Menu and Pause Menu settings access.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
