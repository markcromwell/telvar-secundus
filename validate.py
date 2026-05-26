#!/usr/bin/env python3
"""Structural validation for Telvar Secundus Godot resources (text-only, no Godot binary)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent


def _fail(errors: list[str], msg: str) -> None:
    errors.append(msg)


def _require_file(errors: list[str], path: Path) -> None:
    if not path.is_file():
        _fail(errors, f"Missing required file: {path.relative_to(REPO_ROOT)}")


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _validate_library_scene(errors: list[str]) -> None:
    scene_path = REPO_ROOT / "scenes/veneficturis/Library.tscn"
    tilemap_script = REPO_ROOT / "scripts/veneficturis/library_tilemap.gd"
    lore_path = REPO_ROOT / "data/library_lore.json"
    tileset_path = REPO_ROOT / "assets/tilesets/lpc_terrain.tres"
    png_path = REPO_ROOT / "assets/tilesets/lpc_terrain.png"

    _require_file(errors, scene_path)
    _require_file(errors, tilemap_script)
    _require_file(errors, lore_path)
    _require_file(errors, tileset_path)
    _require_file(errors, png_path)

    if errors:
        return

    scene_txt = _read_text(scene_path)
    if '[node name="TileMap" type="TileMap"' not in scene_txt:
        _fail(errors, "Library.tscn must contain a TileMap node named TileMap")
    if "lpc_terrain.tres" not in scene_txt:
        _fail(errors, "Library.tscn must reference lpc_terrain.tres on the TileMap")
    if "library_tilemap.gd" not in scene_txt:
        _fail(errors, "Library.tscn must attach library_tilemap.gd to the TileMap")

    if "MAP_WIDTH := 30" not in _read_text(tilemap_script):
        _fail(errors, "library_tilemap.gd must define MAP_WIDTH := 30")
    if "MAP_HEIGHT := 20" not in _read_text(tilemap_script):
        _fail(errors, "library_tilemap.gd must define MAP_HEIGHT := 20")

    if "SHELF_ROWS := [" not in _read_text(tilemap_script):
        _fail(errors, "library_tilemap.gd must define SHELF_ROWS for shelf layout")

    tileset_txt = _read_text(tileset_path)
    if "type=\"TileSet\"" not in tileset_txt and "type='TileSet'" not in tileset_txt:
        _fail(errors, "lpc_terrain.tres must declare a TileSet resource")
    if "texture_region_size = Vector2i(16, 16)" not in tileset_txt:
        _fail(errors, "lpc_terrain.tres must use 16x16 texture_region_size (LPC cell size)")
    if "physics_layer_0/collision_layer = 1" not in tileset_txt:
        _fail(errors, "lpc_terrain.tres must define physics_layer_0/collision_layer = 1 for wall collisions")

    try:
        lore = json.loads(_read_text(lore_path))
    except json.JSONDecodeError as exc:
        _fail(errors, f"library_lore.json is not valid JSON: {exc}")
        return

    if not isinstance(lore, list) or len(lore) < 1:
        _fail(errors, "library_lore.json must be a non-empty JSON array")
        return

    first = lore[0]
    if not isinstance(first, dict):
        _fail(errors, "library_lore.json entries must be JSON objects")
        return

    for key in ("id", "title", "body"):
        if key not in first:
            _fail(errors, f"library_lore.json entries must include '{key}'")


def main() -> int:
    errors: list[str] = []
    _validate_library_scene(errors)

    if errors:
        for e in errors:
            print("FAIL:", e)
        return 1

    print("Validation passed (library scene + tileset + lore JSON)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
