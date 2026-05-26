#!/usr/bin/env python3
"""Structural validation for Telvar Secundus Godot resources (text-only, no Godot binary)."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent

LIBRARY_SCENE_REL = Path("scenes/veneficturis/Library.tscn")


def _fail(errors: list[str], msg: str) -> None:
    errors.append(msg)


def _require_file(errors: list[str], path: Path) -> None:
    if not path.is_file():
        _fail(errors, f"Missing required file: {path.relative_to(REPO_ROOT)}")


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _shelf_rows_int_count(gd_text: str) -> int | None:
    """Count comma-separated integers inside `const SHELF_ROWS := [ ... ]`."""
    marker = "const SHELF_ROWS := ["
    if marker not in gd_text:
        return None
    start = gd_text.index(marker) + len(marker)
    try:
        end = gd_text.index("]", start)
    except ValueError:
        return None
    inner = gd_text[start:end]
    parts = [p.strip() for p in inner.split(",") if p.strip()]
    if not parts:
        return None
    for p in parts:
        if not re.fullmatch(r"-?\d+", p):
            return None
    return len(parts)


def _validate_library_scene(errors: list[str]) -> None:
    scene_path = REPO_ROOT / LIBRARY_SCENE_REL
    tilemap_script = REPO_ROOT / "scripts/veneficturis/library_tilemap.gd"
    physics_script = REPO_ROOT / "scripts/veneficturis/library_physics.gd"
    shelf_script = REPO_ROOT / "scripts/veneficturis/shelf_inspect.gd"
    lore_popup_script = REPO_ROOT / "scripts/veneficturis/lore_popup.gd"
    dialogue_data_script = REPO_ROOT / "scripts/veneficturis/dialogue_data.gd"
    lore_path = REPO_ROOT / "data/lore.json"
    tileset_path = REPO_ROOT / "assets/tilesets/lpc_terrain.tres"
    png_path = REPO_ROOT / "assets/tilesets/lpc_terrain.png"
    reading_npc_scene = REPO_ROOT / "scenes/veneficturis/npcs/reading_npc.tscn"
    portrait_maren = REPO_ROOT / "assets/portraits/reader_maren.png"
    portrait_soren = REPO_ROOT / "assets/portraits/reader_soren.png"
    portrait_ilse = REPO_ROOT / "assets/portraits/reader_ilse.png"

    _require_file(errors, scene_path)
    _require_file(errors, tilemap_script)
    _require_file(errors, physics_script)
    _require_file(errors, shelf_script)
    _require_file(errors, lore_popup_script)
    _require_file(errors, dialogue_data_script)
    _require_file(errors, lore_path)
    _require_file(errors, tileset_path)
    _require_file(errors, png_path)
    _require_file(errors, reading_npc_scene)
    _require_file(errors, portrait_maren)
    _require_file(errors, portrait_soren)
    _require_file(errors, portrait_ilse)

    if errors:
        return

    scene_txt = _read_text(scene_path)
    tilemap_txt = _read_text(tilemap_script)
    physics_txt = _read_text(physics_script)

    # Root + core gameplay nodes (Godot 4 text scene format).
    if '[node name="Library" type="Node2D"]' not in scene_txt:
        _fail(errors, 'Library.tscn must have root node [node name="Library" type="Node2D"]')
    if '[node name="DialogueData" type="Node" parent="."]' not in scene_txt:
        _fail(errors, "Library.tscn must contain DialogueData node for dialogue integration")
    if "dialogue_data.gd" not in scene_txt:
        _fail(errors, "Library.tscn must reference dialogue_data.gd")
    if '[node name="TileMap" type="TileMap" parent="."]' not in scene_txt:
        _fail(errors, "Library.tscn must contain a TileMap node named TileMap")
    if "lpc_terrain.tres" not in scene_txt:
        _fail(errors, "Library.tscn must reference lpc_terrain.tres on the TileMap")
    if "library_tilemap.gd" not in scene_txt:
        _fail(errors, "Library.tscn must attach library_tilemap.gd to the TileMap")
    if '[node name="Physics" type="Node2D" parent="."]' not in scene_txt:
        _fail(errors, "Library.tscn must contain Physics node (runtime rope barrier / colliders)")
    if "library_physics.gd" not in scene_txt:
        _fail(errors, "Library.tscn must reference library_physics.gd on the Physics node")
    if '[node name="Shelves" type="Node2D" parent="."]' not in scene_txt:
        _fail(errors, "Library.tscn must contain Shelves Node2D for shelf inspection zones")
    shelf_areas = scene_txt.count('type="Area2D" parent="Shelves"')
    if shelf_areas != 6:
        _fail(errors, f"Library.tscn must define exactly 6 Area2D shelf rows under Shelves (found {shelf_areas})")
    if "shelf_inspect.gd" not in scene_txt:
        _fail(errors, "Library.tscn must reference shelf_inspect.gd for inspectable shelves")
    if '[node name="UI" type="CanvasLayer" parent="."]' not in scene_txt:
        _fail(errors, "Library.tscn must contain UI CanvasLayer")
    if '[node name="PromptLabel" type="Label" parent="UI"]' not in scene_txt:
        _fail(errors, "Library.tscn must contain UI/PromptLabel for shelf interaction prompt")
    if '[node name="LorePopup" type="AcceptDialog" parent="UI"]' not in scene_txt:
        _fail(errors, "Library.tscn must contain UI/LorePopup AcceptDialog")
    if "lore_popup.gd" not in scene_txt:
        _fail(errors, "Library.tscn must attach lore_popup.gd to LorePopup")
    if '[node name="NPCs" type="Node2D" parent="."]' not in scene_txt:
        _fail(errors, "Library.tscn must contain NPCs Node2D")
    if "reading_npc.tscn" not in scene_txt:
        _fail(errors, "Library.tscn must instance reading_npc.tscn for library readers")
    if scene_txt.count('instance=ExtResource("7_npc")') != 3:
        _fail(errors, "Library.tscn must instance exactly three reading_npc PackedScenes")
    for dialogue_id in ("library_reader_maren", "library_reader_soren", "library_reader_ilse"):
        if dialogue_id not in scene_txt:
            _fail(errors, f"Library.tscn must set dialogue_id for reader NPC ({dialogue_id})")
    for portrait in ("reader_maren.png", "reader_soren.png", "reader_ilse.png"):
        if portrait not in scene_txt:
            _fail(errors, f"Library.tscn must reference portrait {portrait}")

    if "MAP_WIDTH := 30" not in tilemap_txt:
        _fail(errors, "library_tilemap.gd must define MAP_WIDTH := 30")
    if "MAP_HEIGHT := 20" not in tilemap_txt:
        _fail(errors, "library_tilemap.gd must define MAP_HEIGHT := 20")

    row_count = _shelf_rows_int_count(tilemap_txt)
    if row_count is None:
        _fail(errors, "library_tilemap.gd must define a numeric const SHELF_ROWS := [ ... ] list")
    elif row_count != 6:
        _fail(errors, f"library_tilemap.gd must define exactly 6 SHELF_ROWS (found {row_count})")

    if "ATLAS_ROPE" not in tilemap_txt or "_paint_rope_decor" not in tilemap_txt:
        _fail(errors, "library_tilemap.gd must paint rope decor (ATLAS_ROPE + _paint_rope_decor) for Restricted Section cordon")

    if "rope_barrier" not in physics_txt or "ROPE_TILE_X" not in physics_txt:
        _fail(errors, "library_physics.gd must build a rope_barrier collider aligned to ROPE_TILE_X")

    tileset_txt = _read_text(tileset_path)
    if 'type="TileSet"' not in tileset_txt and "type='TileSet'" not in tileset_txt:
        _fail(errors, "lpc_terrain.tres must declare a TileSet resource")
    if "texture_region_size = Vector2i(16, 16)" not in tileset_txt:
        _fail(errors, "lpc_terrain.tres must use 16x16 texture_region_size (LPC cell size)")
    if "tile_size = Vector2i(16, 16)" not in tileset_txt:
        _fail(errors, "lpc_terrain.tres must set tile_size = Vector2i(16, 16)")
    if "physics_layer_0/collision_layer = 1" not in tileset_txt:
        _fail(errors, "lpc_terrain.tres must define physics_layer_0/collision_layer = 1 for wall collisions")
    if "physics_layer_0/polygon_0/points" not in tileset_txt:
        _fail(errors, "lpc_terrain.tres must define tile physics polygons on atlas tiles")
    if "1:0/0/physics_layer_0/polygon_0/points" not in tileset_txt:
        _fail(errors, "lpc_terrain.tres must assign physics to wall atlas tile 1:0/0")
    if "2:0/0/physics_layer_0/polygon_0/points" not in tileset_txt:
        _fail(errors, "lpc_terrain.tres must assign physics to shelf atlas tile 2:0/0")

    try:
        lore = json.loads(_read_text(lore_path))
    except json.JSONDecodeError as exc:
        _fail(errors, f"lore.json is not valid JSON: {exc}")
        return

    if not isinstance(lore, list) or len(lore) < 1:
        _fail(errors, "lore.json must be a non-empty JSON array")
        return

    for i, entry in enumerate(lore):
        if not isinstance(entry, dict):
            _fail(errors, f"lore.json entry {i} must be a JSON object")
            continue
        for key in ("id", "title", "body"):
            if key not in entry:
                _fail(errors, f"lore.json entry {i} must include '{key}'")


def main() -> int:
    errors: list[str] = []
    _validate_library_scene(errors)

    if errors:
        for e in errors:
            print("FAIL:", e)
        return 1

    print(
        "Validation passed (Veneficturis Library scene structure, "
        "30×20 tilemap scripts, rope barrier, shelves/NPCs, tileset, lore JSON)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
