#!/usr/bin/env python3
"""
TELVAR-RPG validation script (structural checks; no Godot binary).

Validates key scene files using plain-text parsing (see spec #1246 for expansion).
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
LPC_TERRAIN_TILESET = REPO_ROOT / "assets" / "tilesets" / "lpc_terrain.tres"

errors: list[str] = []

KEY_BUILDING_SUBSTRINGS = (
    "Orsson's Emporium",
    "Paladin Temple",
    "Cathedral of Aten",
    "King's Keep",
    "Veneficturis",
)


def _require(cond: bool, msg: str) -> None:
    if not cond:
        errors.append(msg)


def check_file(rel: str) -> Path | None:
    """Return repo-root path if the file exists; otherwise record an error."""
    p = REPO_ROOT / rel
    if not p.is_file():
        errors.append(f"Missing required file: {p}")
        return None
    return p


def _validate_overworld_section() -> None:
    """Overworld: required files, registry content, map script hooks, scene wiring, TileMap shell."""
    overworld_paths = [
        "scenes/Overworld.tscn",
        "scripts/BuildingRegistry.gd",
        "scripts/OverworldMap.gd",
        "scripts/DistrictZone.gd",
        "scripts/BuildingEntrance.gd",
    ]
    resolved: dict[str, Path] = {}
    for rel in overworld_paths:
        p = check_file(rel)
        if p is not None:
            resolved[rel] = p

    br = resolved.get("scripts/BuildingRegistry.gd")
    if br is not None:
        text = br.read_text(encoding="utf-8")
        _require("func get_buildings" in text, "BuildingRegistry.gd must define get_buildings")
        for key in KEY_BUILDING_SUBSTRINGS:
            _require(key in text, f"BuildingRegistry.gd must mention key location: {key!r}")
        _require(
            '"tile_theme": "dock"' in text,
            'BuildingRegistry.gd must include at least one tile_theme "dock"',
        )
        _require(
            '"tile_theme": "dark_stone"' in text,
            'BuildingRegistry.gd must include at least one tile_theme "dark_stone"',
        )
        _require(
            '"tile_theme": "stone_keep"' in text,
            'BuildingRegistry.gd must include at least one tile_theme "stone_keep"',
        )

    om = resolved.get("scripts/OverworldMap.gd")
    if om is not None:
        text = om.read_text(encoding="utf-8")
        _require("place_buildings" in text, "OverworldMap.gd must define place_buildings")
        _require("place_special_zones" in text, "OverworldMap.gd must define place_special_zones")

    ow = resolved.get("scenes/Overworld.tscn")
    if ow is not None:
        text = ow.read_text(encoding="utf-8")
        _require("DistrictZone.gd" in text, "Overworld.tscn must reference DistrictZone.gd")
        _require("BuildingEntrance.gd" in text, "Overworld.tscn must reference BuildingEntrance.gd")

        _require(LPC_TERRAIN_TILESET.is_file(), f"Missing required file: {LPC_TERRAIN_TILESET}")
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


_validate_overworld_section()

if errors:
    for e in errors:
        print("FAIL:", e)
    sys.exit(1)

print("Validation passed.")
sys.exit(0)
