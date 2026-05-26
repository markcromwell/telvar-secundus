#!/usr/bin/env python3
"""Structural validation for Telvar Secundus (Godot 4.x) — text checks only, no Godot binary."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent

REQUIRED_PATHS = [
    REPO_ROOT / "player" / "Player.gd",
    REPO_ROOT / "scripts" / "inventory.gd",
    REPO_ROOT / "scripts" / "wings_enter_sequence.gd",
    REPO_ROOT / "scripts" / "final_cutscene_epilogue.gd",
    REPO_ROOT / "cutscenes" / "final_epilogue.tscn",
    REPO_ROOT / "scenes" / "main_menu.tscn",
    REPO_ROOT / "project.godot",
]

FILE_MARKERS: dict[str, list[str]] = {
    "player/Player.gd": [
        "class_name TelvarPlayer",
        "manual_input_enabled",
        "set_scripted_velocity",
        "move_and_slide",
    ],
    "scripts/inventory.gd": [
        "try_consume_sealed_wings_key",
        "sealed_wings_key",
        "unlock_ng_plus_for_active_slot",
        "is_ng_plus_unlocked",
        "get_active_slot",
        "user://slot_",
        "2717",
    ],
    "scripts/wings_enter_sequence.gd": [
        "WALK_TILE_COUNT",
        "RENDERED_TILE_PX",
        "try_begin_enter_from_choice",
        "try_consume_sealed_wings_key",
        "manual_input_enabled",
        "Inventory",
        "2715",
    ],
    "scripts/final_cutscene_epilogue.gd": [
        "2716",
        "2717",
        "PANEL_HOLD_SECONDS",
        "AnimationPlayer",
        "final_cut/epilogue",
        "_epilogue_complete",
        "CanvasLayer",
        "unlock_ng_plus_for_active_slot",
    ],
    "cutscenes/final_epilogue.tscn": [
        "AnimationPlayer",
        "CanvasLayer",
        "LabelPanel1",
        "FadeOverlay",
        "The End — To be continued in The Paladin's Vow",
        "EndScreen",
        "MainMenuButton",
        "pressed",
    ],
}


def main() -> int:
    errors: list[str] = []

    for path in REQUIRED_PATHS:
        rel = path.relative_to(REPO_ROOT).as_posix()
        if not path.is_file():
            errors.append(f"Missing required file: {rel}")

    for rel, needles in FILE_MARKERS.items():
        p = REPO_ROOT / rel
        if not p.is_file():
            errors.append(f"Missing required file: {rel}")
            continue
        text = p.read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel}: missing marker {needle!r}")

    pg = REPO_ROOT / "project.godot"
    if not pg.is_file():
        errors.append("Missing required file: project.godot")
    else:
        g = pg.read_text(encoding="utf-8")
        if "Inventory" not in g or "scripts/inventory.gd" not in g:
            errors.append("project.godot: missing Inventory autoload for scripts/inventory.gd")

    if errors:
        for e in errors:
            print("FAIL:", e)
        return 1

    print(
        "validate.py: structural checks passed "
        "(phases 2715 wings enter + 2716 final epilogue + 2717 end screen / NG+ slot)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
