"""Library scene filesystem checks (Godot text format, no engine)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
LIBRARY_SCENE = REPO_ROOT / "scenes/veneficturis/Library.tscn"
LIBRARY_TILEMAP = REPO_ROOT / "scripts/veneficturis/library_tilemap.gd"
LPC_TILESET = REPO_ROOT / "assets/tilesets/lpc_terrain.tres"
LIBRARY_LORE = REPO_ROOT / "data/lore.json"
NPC_BASE_SCENE = REPO_ROOT / "scenes/veneficturis/npcs/NPC.tscn"
READING_NPC_SCENE = REPO_ROOT / "scenes/veneficturis/npcs/reading_npc.tscn"


def test_library_scene_exists() -> None:
    assert LIBRARY_SCENE.is_file()


def test_library_scene_has_tilemap_and_tileset() -> None:
    text = LIBRARY_SCENE.read_text(encoding="utf-8")
    assert '[node name="TileMap" type="TileMap"' in text
    assert "lpc_terrain.tres" in text


def test_library_tilemap_dimensions_30x20() -> None:
    text = LIBRARY_TILEMAP.read_text(encoding="utf-8")
    assert "MAP_WIDTH := 30" in text
    assert "MAP_HEIGHT := 20" in text


def test_library_tilemap_has_six_shelf_rows() -> None:
    text = LIBRARY_TILEMAP.read_text(encoding="utf-8")
    assert "SHELF_ROWS" in text
    start = text.index("SHELF_ROWS")
    bracket = text.index("[", start)
    end = text.index("]", bracket)
    inner = text[bracket + 1 : end]
    entries = [p.strip() for p in inner.split(",") if p.strip()]
    assert len(entries) == 6


def test_lpc_tileset_declares_16px_tiles() -> None:
    text = LPC_TILESET.read_text(encoding="utf-8")
    assert "texture_region_size = Vector2i(16, 16)" in text
    assert "tile_size = Vector2i(16, 16)" in text


def test_lpc_tileset_has_wall_and_shelf_physics_layer() -> None:
    text = LPC_TILESET.read_text(encoding="utf-8")
    assert "physics_layer_0/collision_layer = 1" in text
    assert "physics_layer_0/polygon_0/points" in text
    assert "1:0/0/physics_layer_0/polygon_0/points" in text
    assert "2:0/0/physics_layer_0/polygon_0/points" in text


def test_library_lore_json_is_non_empty_array() -> None:
    data = json.loads(LIBRARY_LORE.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    assert len(data) >= 1
    assert isinstance(data[0], dict)


def test_npc_base_scene_structure() -> None:
    assert NPC_BASE_SCENE.is_file()
    text = NPC_BASE_SCENE.read_text(encoding="utf-8")
    assert '[node name="NPC" type="CharacterBody2D"' in text
    assert 'type="AnimatedSprite2D"' in text
    assert '[node name="InteractionZone" type="Area2D"' in text
    assert "npc.gd" in text


def test_reading_npc_inherits_npc_scene() -> None:
    assert READING_NPC_SCENE.is_file()
    text = READING_NPC_SCENE.read_text(encoding="utf-8")
    assert "NPC.tscn" in text
    assert "reading_npc.gd" in text


def test_library_has_three_reading_npc_instances() -> None:
    text = LIBRARY_SCENE.read_text(encoding="utf-8")
    assert text.count("reading_npc.tscn") == 1
    assert text.count('instance=ExtResource("7_npc")') == 3
    assert "library_reader_maren" in text
    assert "library_reader_soren" in text
    assert "library_reader_ilse" in text
