"""Structural checks for the sealed door scene and inventory autoload."""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SEALED_SCENE = REPO_ROOT / "scenes/world/sealed_door.tscn"
SEALED_SCRIPT = REPO_ROOT / "scripts/world/SealedDoor.gd"
INVENTORY_SCRIPT = REPO_ROOT / "scripts/autoload/Inventory.gd"
PROJECT_GODOT = REPO_ROOT / "project.godot"


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
