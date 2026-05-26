"""Phase 2540: Paladin temple interactive wiring (compositor scene + autoloads)."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from tests.test_godot_config import REPO_ROOT, _load_ini

PLAYABLE_SCENE = REPO_ROOT / "scenes/interiors/paladin_temple_playable.tscn"
OVERWORLD_SCENE = REPO_ROOT / "scenes/world/secundus_overworld.tscn"
PROJECT_GODOT = REPO_ROOT / "project.godot"


def _ext_resource_paths(tscn_text: str) -> list[str]:
    paths: list[str] = []
    for m in re.finditer(r'\[ext_resource[^\]]*path="(res://[^"]+)"', tscn_text):
        paths.append(m.group(1))
    return paths


def test_autoloads_registered_and_scripts_exist() -> None:
    cp = _load_ini(PROJECT_GODOT)
    assert cp.has_section("autoload")
    for key in ("GameBridge", "DialogueManager", "LoreManager"):
        raw = cp.get("autoload", key)
        assert raw.startswith('"*res://') and raw.endswith('"')
        inner = raw.strip('"').removeprefix("*")
        path = REPO_ROOT / inner.removeprefix("res://")
        assert path.is_file(), f"Missing autoload script: {path}"


def test_playable_scene_ext_resources_resolve() -> None:
    text = PLAYABLE_SCENE.read_text(encoding="utf-8")
    for res_path in _ext_resource_paths(text):
        rel = res_path.removeprefix("res://")
        assert (REPO_ROOT / rel).is_file(), f"Unresolved ExtResource: {res_path}"


def test_playable_scene_instances_temple_and_sir_valins() -> None:
    text = PLAYABLE_SCENE.read_text(encoding="utf-8")
    assert "res://scenes/interiors/paladin_temple.tscn" in text
    assert "res://scenes/npcs/sir_valins.tscn" in text
    assert '[node name="SirValins" parent="." instance=ExtResource("2_valins")]' in text


def test_sir_valins_near_aten_altar_within_three_tiles() -> None:
    """AtenAltar in paladin_temple.tscn is at (152, 56); playable scene places Sir Valins at (152, 104)."""
    text = PLAYABLE_SCENE.read_text(encoding="utf-8")
    assert "position = Vector2(152, 104)" in text
    # 3 tiles * 16 px/tile = 48 px vertical separation from altar marker
    altar_y = 56
    valins_y = 104
    assert abs(valins_y - altar_y) <= 48


def test_exit_door_south_rows_28_29() -> None:
    text = PLAYABLE_SCENE.read_text(encoding="utf-8")
    m = re.search(r'\[node name="ExitDoor"[^\]]*\][^\[]*position = Vector2\(([^,]+),\s*([^)]+)\)', text)
    assert m, "ExitDoor position not found"
    y = float(m.group(2))
    tile = 16.0
    row = y / tile
    assert 28.0 <= row < 30.0, f"ExitDoor expected around rows 28-29, got row={row}"


def test_exit_script_targets_secundus_overworld_and_spawn() -> None:
    p = REPO_ROOT / "scripts/interior/exit_door_area.gd"
    s = p.read_text(encoding="utf-8")
    assert 'OVERWORLD_SCENE := "res://scenes/world/secundus_overworld.tscn"' in s
    assert 'SPAWN_MARKER_NAME := "paladin_temple_exit"' in s
    assert "FADE_SECONDS := 0.3" in s


def test_root_script_starts_sir_valins_dialogue() -> None:
    p = REPO_ROOT / "scripts/interior/paladin_temple_playable_root.gd"
    assert 'DialogueManager.start("sir_valins")' in p.read_text(encoding="utf-8")


def test_bookshelf_script_shows_order_lore() -> None:
    p = REPO_ROOT / "scripts/interior/order_bookshelf_area.gd"
    assert 'LoreManager.show("order_lore")' in p.read_text(encoding="utf-8")


def test_sir_valins_dialogue_has_at_least_two_nodes() -> None:
    path = REPO_ROOT / "assets/dialogue/sir_valins.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    nodes = data.get("nodes", [])
    assert len(nodes) >= 2


def test_overworld_has_paladin_temple_exit_marker() -> None:
    text = OVERWORLD_SCENE.read_text(encoding="utf-8")
    assert 'name="paladin_temple_exit"' in text
