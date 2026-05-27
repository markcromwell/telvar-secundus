"""Structural checks for the sealed door scene and inventory autoload."""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SEALED_SCENE = REPO_ROOT / "scenes/world/sealed_door.tscn"
ACADEMY_SCENE = REPO_ROOT / "scenes/world/wizard_academy.tscn"
SEALED_SCRIPT = REPO_ROOT / "scripts/world/SealedDoor.gd"
INVENTORY_SCRIPT = REPO_ROOT / "scripts/autoload/Inventory.gd"
PROJECT_GODOT = REPO_ROOT / "project.godot"
ITEM_TABLE = REPO_ROOT / "resources/items/item_table.tres"
SEALED_KEY_RES = REPO_ROOT / "resources/items/sealed_wing_key.tres"
LPC_TILESET = REPO_ROOT / "resources/tilesets/lpc_terrain.tres"
LPC_PNG = REPO_ROOT / "assets/tilesets/lpc_terrain.png"


def test_sealed_door_scene_exists() -> None:
    assert SEALED_SCENE.is_file()


def test_sealed_door_script_exists() -> None:
    assert SEALED_SCRIPT.is_file()
    body = SEALED_SCRIPT.read_text(encoding="utf-8")
    assert "&\"sealed_wing_key\"" in body


def test_inventory_autoload_registered() -> None:
    text = PROJECT_GODOT.read_text(encoding="utf-8")
    assert 'Inventory="*res://scripts/autoload/Inventory.gd"' in text


def test_inventory_script_exists() -> None:
    assert INVENTORY_SCRIPT.is_file()


def test_sealed_door_scene_wires_script_and_nodes() -> None:
    body = SEALED_SCENE.read_text(encoding="utf-8")
    assert 'path="res://scripts/world/SealedDoor.gd"' in body
    assert "[node name=\"DoorPivot\" type=\"Node2D\"" in body
    assert "[node name=\"InteractArea\" type=\"Area2D\"" in body
    assert "RectangleShape2D" in body


def test_wizard_academy_scene_has_tilemap_and_door_instance() -> None:
    assert ACADEMY_SCENE.is_file()
    body = ACADEMY_SCENE.read_text(encoding="utf-8")
    assert 'path="res://scenes/world/sealed_door.tscn"' in body
    assert 'path="res://resources/tilesets/lpc_terrain.tres"' in body
    assert 'type="TileMap"' in body
    assert "instance=ExtResource(" in body


def test_sealed_wing_key_registered_in_item_table() -> None:
    assert ITEM_TABLE.is_file()
    assert SEALED_KEY_RES.is_file()
    assert '&"sealed_wing_key"' in ITEM_TABLE.read_text(encoding="utf-8")
    assert 'id = &"sealed_wing_key"' in SEALED_KEY_RES.read_text(encoding="utf-8")


def test_lpc_tileset_points_at_16px_source() -> None:
    assert LPC_TILESET.is_file()
    assert LPC_PNG.is_file()
    ts = LPC_TILESET.read_text(encoding="utf-8")
    assert 'path="res://assets/tilesets/lpc_terrain.png"' in ts
    assert "texture_region_size = Vector2i(16, 16)" in ts
