#!/usr/bin/env python3
"""Structural validation for Telvar Secundus (Godot 4.3 text resources, no engine binary)."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent

REQUIRED_PATHS = (
    "CREDITS.md",
    "project.godot",
    "export_presets.cfg",
    "scenes/main_menu.tscn",
    "scenes/credits_roll.tscn",
    "scenes/end_screen_main.tscn",
    "scenes/cutscene_myramar_corridor.tscn",
    "scripts/main_menu.gd",
    "scripts/credits_roll.gd",
    "scripts/end_screen_main.gd",
    "scripts/cutscene_myramar_corridor.gd",
    "scripts/game_session.gd",
    "scripts/progress_store.gd",
    "assets/tilesets/lpc_terrain.png",
)

EXACT_DIALOGUE = "And so it begins."


def _fail(msg: str) -> None:
    print("FAIL:", msg)


def _read(rel: str) -> str:
    return (REPO / rel).read_text(encoding="utf-8")


def _check_files_exist(errors: list[str]) -> None:
    for rel in REQUIRED_PATHS:
        p = REPO / rel
        if not p.is_file():
            errors.append(f"Missing required file: {rel}")


def _check_credits(errors: list[str]) -> None:
    text = _read("CREDITS.md")
    if "New Paladin Order" not in text:
        errors.append("CREDITS.md must mention New Paladin Order (NPO attribution).")
    if "Mark Cromwell" not in text:
        errors.append("CREDITS.md must credit Mark Cromwell for the story series.")
    if "Godot Engine" not in text or "MIT" not in text:
        errors.append("CREDITS.md must credit Godot Engine with MIT license (engine licenses).")


def _check_project_godot(errors: list[str]) -> None:
    pg = _read("project.godot")
    if 'run/main_scene="res://scenes/main_menu.tscn"' not in pg:
        errors.append("project.godot must set run/main_scene to the main menu scene.")
    if "ProgressStore=" not in pg or "GameSession=" not in pg:
        errors.append("project.godot must register GameSession and ProgressStore autoloads.")


def _check_main_menu_scene(errors: list[str]) -> None:
    tscn = _read("scenes/main_menu.tscn")
    if "CreditsButton" not in tscn:
        errors.append("scenes/main_menu.tscn must define a CreditsButton for the credits entry point.")
    if "main_menu.gd" not in tscn:
        errors.append("Main menu scene must attach main_menu.gd.")


def _check_main_menu_script(errors: list[str]) -> None:
    gd = _read("scripts/main_menu.gd")
    if "res://scenes/credits_roll.tscn" not in gd:
        errors.append("main_menu.gd must load the credits roll scene when Credits is pressed.")
    if "res://scenes/cutscene_myramar_corridor.tscn" not in gd:
        errors.append("main_menu.gd must start the Myramar corridor cutscene from Play.")
    if "credits_exit_to_main_menu" not in gd:
        errors.append("main_menu.gd must set GameSession.credits_exit_to_main_menu before opening credits.")


def _check_credits_roll_script(errors: list[str]) -> None:
    gd = _read("scripts/credits_roll.gd")
    if "CREDITS.md" not in gd:
        errors.append("credits_roll.gd must read CREDITS.md for scrolling attribution text.")
    if "res://scenes/end_screen_main.tscn" not in gd:
        errors.append("credits_roll.gd must transition to the end screen after story credits (non-menu path).")
    if "res://scenes/main_menu.tscn" not in gd:
        errors.append("credits_roll.gd must return to the main menu when credits were opened from the menu.")
    if "credits_exit_to_main_menu" not in gd:
        errors.append("credits_roll.gd must branch on GameSession.credits_exit_to_main_menu.")


def _check_cutscene_scene(errors: list[str]) -> None:
    tscn = _read("scenes/cutscene_myramar_corridor.tscn")
    for token in ("TileMap", "CharacterBody2D", "Area2D"):
        if token not in tscn:
            errors.append(f"scenes/cutscene_myramar_corridor.tscn must contain a {token} node.")
    if "cutscene_myramar_corridor.gd" not in tscn:
        errors.append("Cutscene scene must attach cutscene_myramar_corridor.gd.")


def _check_cutscene_script(errors: list[str]) -> None:
    gd = _read("scripts/cutscene_myramar_corridor.gd")
    if EXACT_DIALOGUE not in gd:
        errors.append(f"Cutscene script must include the exact dialogue line: {EXACT_DIALOGUE!r}")
    if "res://scenes/credits_roll.tscn" not in gd:
        errors.append("Cutscene script must hand off to credits_roll.tscn after the corridor beat.")
    if "credits_exit_to_main_menu" not in gd:
        errors.append("Cutscene script must clear GameSession.credits_exit_to_main_menu before credits.")


def _check_end_screen_script(errors: list[str]) -> None:
    gd = _read("scripts/end_screen_main.gd")
    if "mark_game_complete" not in gd:
        errors.append("End screen script must call ProgressStore.mark_game_complete() when finishing.")
    if "get_elapsed_seconds" not in gd:
        errors.append("End screen script must read play time via GameSession.get_elapsed_seconds().")
    if "Test of Fire" not in gd:
        errors.append("End screen script must surface a Test of Fire link or label for the player.")
    if 'OS.has_feature("web")' not in gd:
        errors.append('End screen script must detect Web export via OS.has_feature("web") for external links.')
    if '"JavaScriptBridge"' not in gd or "JSON.stringify" not in gd:
        errors.append(
            "End screen script must open external URLs on Web using JavaScriptBridge + JSON.stringify (safe shell_open substitute)."
        )


def _check_game_session_script(errors: list[str]) -> None:
    gd = _read("scripts/game_session.gd")
    if "credits_exit_to_main_menu" not in gd:
        errors.append("game_session.gd must define credits_exit_to_main_menu for credits routing.")


def _check_export_presets(errors: list[str]) -> None:
    raw = _read("export_presets.cfg")
    if "[preset.0]" not in raw or 'platform="Web"' not in raw:
        errors.append("export_presets.cfg must define preset.0 for Web export.")
    if "[preset.1]" not in raw or 'platform="Linux"' not in raw:
        errors.append("export_presets.cfg must define preset.1 for Linux export (second target).")


def _check_png_small(errors: list[str]) -> None:
    p = REPO / "assets/tilesets/lpc_terrain.png"
    size = p.stat().st_size
    if size > 5 * 1024 * 1024:
        errors.append("lpc_terrain.png exceeds 5MB web-safe budget.")
    if size < 32:
        errors.append("lpc_terrain.png appears truncated or invalid (too small).")


def main() -> int:
    errors: list[str] = []
    _check_files_exist(errors)
    if errors:
        for e in errors:
            _fail(e)
        return 1
    _check_credits(errors)
    _check_project_godot(errors)
    _check_main_menu_scene(errors)
    _check_main_menu_script(errors)
    _check_credits_roll_script(errors)
    _check_cutscene_scene(errors)
    _check_cutscene_script(errors)
    _check_end_screen_script(errors)
    _check_game_session_script(errors)
    _check_export_presets(errors)
    _check_png_small(errors)
    if errors:
        for e in errors:
            _fail(e)
        return 1
    print("Validation passed (main menu, cutscene → credits → end, dual export targets).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
