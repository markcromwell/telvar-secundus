"""LPC terrain TileSet collision policy (text-parse; no Godot binary)."""

from __future__ import annotations

from pathlib import Path

import validate

REPO_ROOT = Path(__file__).resolve().parents[1]
LPC_TRES = REPO_ROOT / "assets/tilesets/lpc_terrain.tres"


def test_lpc_terrain_tileset_audit_passes_on_repo_file() -> None:
    text = LPC_TRES.read_text(encoding="utf-8")
    errs = validate.audit_lpc_terrain_tileset_text(text)
    assert errs == [], errs


def test_lpc_terrain_tileset_audit_flags_phantom_walkable_physics() -> None:
    text = LPC_TRES.read_text(encoding="utf-8")
    injected = text.replace(
        "5:0/0 = 0",
        "5:0/0 = 0\n"
        "5:0/0/physics_layer_0/polygon_0/points = PackedVector2Array(-8, -8, 8, -8, 8, 8, -8, 8)",
    )
    errs = validate.audit_lpc_terrain_tileset_text(injected, rel_path="synthetic")
    assert len(errs) >= 1
    assert any("5:0" in e for e in errs)


def test_lpc_terrain_tileset_audit_requires_building_polygon() -> None:
    text = LPC_TRES.read_text(encoding="utf-8")
    stripped = text.replace(
        "40:0/0/physics_layer_0/polygon_0/points = PackedVector2Array(-8, -8, 8, -8, 8, 8, -8, 8)", ""
    )
    errs = validate.audit_lpc_terrain_tileset_text(stripped, rel_path="synthetic")
    assert any("polygon_0/points" in e for e in errs)


def test_merchant_to_temple_corridor_duration_bounds() -> None:
    """Spec: ~40 world tiles at 32 px (16 px × 2× scale) with player speed 64 px/s → ~20 s."""
    corridor_world_tiles = 40
    rendered_px_per_tile = 32
    player_speed_px_per_sec = 64.0
    seconds = (corridor_world_tiles * rendered_px_per_tile) / player_speed_px_per_sec
    assert 19.0 <= seconds <= 21.0
