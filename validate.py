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
}


def main() -> int:
    errors: list[str] = []

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

    print("validate.py: structural checks passed (phase 2715 wings enter)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
