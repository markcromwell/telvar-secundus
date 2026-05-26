#!/usr/bin/env python3
"""
TELVAR-RPG validation script (structural checks; no Godot binary).

Validates key scene files using plain-text parsing (see spec #1246 for expansion).
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
OVERWORLD_SCENE = REPO_ROOT / "scenes" / "Overworld.tscn"
LPC_TERRAIN_TILESET = REPO_ROOT / "assets" / "tilesets" / "lpc_terrain.tres"

errors: list[str] = []


def _require(cond: bool, msg: str) -> None:
    if not cond:
        errors.append(msg)


def _validate_overworld() -> None:
    _require(OVERWORLD_SCENE.is_file(), f"Missing required file: {OVERWORLD_SCENE}")
    _require(LPC_TERRAIN_TILESET.is_file(), f"Missing required file: {LPC_TERRAIN_TILESET}")
    if not OVERWORLD_SCENE.is_file():
        return
    text = OVERWORLD_SCENE.read_text(encoding="utf-8")
    _require(
        'path="res://assets/tilesets/lpc_terrain.tres"' in text,
        "Overworld.tscn must reference res://assets/tilesets/lpc_terrain.tres",
    )
    _require(
        '[node name="TileMap" type="TileMap" parent="."]' in text,
        "Overworld.tscn must contain a TileMap child of the root",
    )
    _require("layer_0/" in text and "layer_1/" in text, "Overworld TileMap must define layer_0 and layer_1")
    _require(
        "layer_0/tile_data = PackedInt32Array()" in text and "layer_1/tile_data = PackedInt32Array()" in text,
        "Overworld TileMap layers 0 and 1 must exist with empty tile_data",
    )
    _require(
        ("rendering_quadrant_size = 16" in text) or ("cell_quadrant_size = 16" in text),
        "Overworld TileMap must set rendering_quadrant_size=16 (or legacy cell_quadrant_size=16)",
    )
    _require(
        '[node name="Camera2D" type="Camera2D" parent="TileMap"]' in text,
        "Overworld must have Camera2D parented under TileMap",
    )
    _require("position_smoothing_enabled = true" in text, "Overworld Camera2D must enable position_smoothing")
    _require(
        '[node name="SpawnPoint" type="Marker2D" parent="TileMap"]' in text,
        "Overworld must have Marker2D SpawnPoint under TileMap",
    )
    _require(
        '[node name="DistrictZones" type="Node2D" parent="."]' in text,
        "Overworld must have DistrictZones Node2D under root",
    )
    _require(
        '[node name="BuildingEntrances" type="Node2D" parent="."]' in text,
        "Overworld must have BuildingEntrances Node2D under root",
    )


_validate_overworld()

if errors:
    for e in errors:
        print("FAIL:", e)
    sys.exit(1)

print("Validation passed.")
sys.exit(0)
