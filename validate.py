#!/usr/bin/env python3
"""TELVAR-RPG structural validation (no Godot binary)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent

# LPC TileSet collision policy (Godot 4 TileSetAtlasSource text format):
# Walkable ground atlas tiles must not define physics_layer_* (avoids phantom TileMap collision).
# Atlas tile (40,0) is the canonical building-footprint tile and must keep a full-tile polygon.
BUILDING_ATLAS_TILE: tuple[int, int] = (40, 0)


def audit_lpc_terrain_tileset_text(text: str, *, rel_path: str = "assets/tilesets/lpc_terrain.tres") -> list[str]:
    """Return human-readable errors for TileSet physics policy; empty list means OK."""
    out: list[str] = []

    bx, by = BUILDING_ATLAS_TILE
    needle = f"{bx}:{by}/0/physics_layer_0/polygon_0/points = PackedVector2Array"
    if needle not in text:
        out.append(
            f"{rel_path}: building atlas tile {bx}:{by} must define physics_layer_0/polygon_0/points "
            "(building footprints must retain collision)"
        )

    for m in re.finditer(r"^(\d+):(\d+)/0/physics_layer_0/", text, re.MULTILINE):
        xs, ys = int(m.group(1)), int(m.group(2))
        if (xs, ys) != BUILDING_ATLAS_TILE:
            out.append(
                f"{rel_path}: unexpected physics_layer_0 on atlas tile {xs}:{ys} "
                f"(only building footprint {BUILDING_ATLAS_TILE[0]}:{BUILDING_ATLAS_TILE[1]} may use TileSet physics)"
            )

    return out


def main() -> int:
    errors: list[str] = []

    def _require_file(rel: str) -> None:
        p = REPO_ROOT / rel
        if not p.is_file():
            errors.append(f"Missing required file: {rel}")

    def _require_text(path: Path, needle: str, what: str) -> None:
        if not path.is_file():
            return
        t = path.read_text(encoding="utf-8")
        if needle not in t:
            errors.append(f"{path.relative_to(REPO_ROOT)}: expected {what}")

    _require_file("HUD.gd")
    _require_file("HUD.tscn")
    _require_file("scenes/overworld/Overworld.tscn")
    _require_file("assets/tilesets/lpc_terrain.png")
    _require_file("assets/tilesets/lpc_terrain.tres")

    _hud_tscn = REPO_ROOT / "HUD.tscn"
    _hud_gd = REPO_ROOT / "HUD.gd"
    _require_text(_hud_tscn, '[node name="DistrictLabel"', "DistrictLabel node")
    _require_text(_hud_tscn, '[node name="DistrictHoldTimer"', "DistrictHoldTimer node")
    _require_text(_hud_gd, "func show_district_name", "show_district_name function")

    _tiles_tres = REPO_ROOT / "assets/tilesets/lpc_terrain.tres"
    if _tiles_tres.is_file():
        errors.extend(audit_lpc_terrain_tileset_text(_tiles_tres.read_text(encoding="utf-8")))

    _overworld_tscn = REPO_ROOT / "scenes/overworld/Overworld.tscn"
    if _overworld_tscn.is_file():
        _ow = _overworld_tscn.read_text(encoding="utf-8")
        _expected_districts = (
            "Golden Bell",
            "Temple District",
            "Old City",
            "Merchant District",
            "Reagent's Hill",
            "Bazaar",
            "Harbor District",
            "Warehouse District",
            "Foreign Quarter",
            "Cemetery",
            "The Rookery",
            "The Iron Works",
        )
        for d in _expected_districts:
            needle = f'district_name = "{d}"'
            if needle not in _ow:
                errors.append(f"{_overworld_tscn.relative_to(REPO_ROOT)}: missing {needle}")
        _conn = _ow.count('signal="district_entered"')
        if _conn != 12:
            errors.append(
                f"{_overworld_tscn.relative_to(REPO_ROOT)}: expected 12 district_entered connections, found {_conn}"
            )
        _to_hud = _ow.count('to="HUD" method="show_district_name"')
        if _to_hud != 12:
            errors.append(
                f"{_overworld_tscn.relative_to(REPO_ROOT)}: expected 12 HUD signal bindings, found {_to_hud}"
            )
        _layer4 = _ow.count("collision_layer = 8")
        if _layer4 != 12:
            errors.append(
                f"{_overworld_tscn.relative_to(REPO_ROOT)}: expected collision_layer=8 on 12 zones, found {_layer4}"
            )

    if errors:
        for e in errors:
            print("FAIL:", e)
        return 1

    print("Structural checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
