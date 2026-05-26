#!/usr/bin/env python3
"""Structural validation for the Telvar Secundus Godot project.

Uses filesystem checks and plain-text parsing of .tscn files — no Godot runtime.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent

REQUIRED_PATHS: tuple[tuple[str, ...], ...] = (
    ("scenes", "merchant_well", "MerchantWell.tscn"),
    ("scripts", "Npc.gd"),
    ("scripts", "EncounterZone.gd"),
    ("assets", "tilesets", "lpc_terrain.tres"),
)

MAIN_SCENE_PARTS: tuple[str, ...] = ("scenes", "MainScene.tscn")

MERCHANT_WELL_NPC_MARKERS: tuple[str, ...] = (
    "MarketTrader",
    "BeggarChild",
    "WomanNpc",
    "Thug",
)
MERCHANT_WELL_ENCOUNTER_MARKER = "EncounterZone"


def _rel(parts: tuple[str, ...]) -> str:
    return str(Path(*parts))


def _collect_errors() -> list[str]:
    errors: list[str] = []

    for parts in REQUIRED_PATHS:
        path = REPO_ROOT.joinpath(*parts)
        if not path.is_file():
            errors.append(f"Missing required file: {_rel(parts)}")

    mw_path = REPO_ROOT.joinpath(*REQUIRED_PATHS[0])
    if mw_path.is_file():
        text = mw_path.read_text(encoding="utf-8", errors="replace")
        for marker in MERCHANT_WELL_NPC_MARKERS:
            if marker not in text:
                errors.append(
                    f"MerchantWell.tscn must contain {marker!r} (node name / identifier)"
                )
        if MERCHANT_WELL_ENCOUNTER_MARKER not in text:
            errors.append(
                f"MerchantWell.tscn must contain {MERCHANT_WELL_ENCOUNTER_MARKER!r}"
            )

    main_scene = REPO_ROOT.joinpath(*MAIN_SCENE_PARTS)
    if not main_scene.is_file():
        errors.append(f"Missing MainScene: {_rel(MAIN_SCENE_PARTS)}")
    else:
        ms = main_scene.read_text(encoding="utf-8", errors="replace")
        if "MerchantWell.tscn" not in ms:
            errors.append("MainScene.tscn must reference MerchantWell.tscn (PackedScene path)")
        if "tile_set = null" in ms:
            errors.append(
                "MainScene.tscn must not use a bare TileMap with tile_set = null; "
                "use the MerchantWell scene instance instead"
            )

    return errors


def main() -> int:
    errors = _collect_errors()
    if errors:
        for e in errors:
            print("FAIL:", e)
        return 1
    print("Validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
