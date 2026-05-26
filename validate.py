#!/usr/bin/env python3
"""Structural validation for key Godot 4.x scenes (.tscn text format).

Parses scene files without invoking Godot. Checks file presence, TileMap usage,
LPC tileset wiring, and Main Hall door Area2D nodes with correct target_scene.

Exit 0 on success; prints ``FAIL:`` lines and exits 1 on failure.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
LPC_TILESET_RES = "res://assets/tilesets/lpc_terrain.tres"


def _fail(errors: list[str], message: str) -> None:
    errors.append(message)


def _read_scene(errors: list[str], path: Path) -> str | None:
    if not path.is_file():
        _fail(errors, f"missing file: {path.relative_to(REPO_ROOT)}")
        return None
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        _fail(errors, f"cannot read {path.relative_to(REPO_ROOT)}: {exc}")
        return None


def _node_section(text: str, node_name: str) -> str | None:
    needle = f'[node name="{node_name}"'
    start = text.find(needle)
    if start == -1:
        return None
    nxt = text.find("\n[node ", start + 1)
    if nxt == -1:
        return text[start:]
    return text[start:nxt]


def _node_subtree_until_root_sibling(text: str, node_name: str) -> str | None:
    """Slice from ``[node name="node_name"`` through direct children; stop at next ``parent="."`` node."""
    needle = f'[node name="{node_name}"'
    start = text.find(needle)
    if start == -1:
        return None
    pos = start + 1
    while True:
        j = text.find("\n[node ", pos)
        if j == -1:
            return text[start:]
        line_end = text.find("]", j)
        if line_end == -1:
            return text[start:]
        header = text[j : line_end + 1]
        if f'parent="{node_name}"]' in header:
            pos = j + 1
            continue
        if 'parent="."]' in header:
            return text[start:j]
        pos = j + 1


def _validate_godot4_scene_header(errors: list[str], rel_path: str, text: str) -> None:
    lines = text.lstrip("\ufeff").splitlines()
    if not lines:
        _fail(errors, f"{rel_path}: empty file")
        return
    head = lines[0]
    if "[gd_scene" not in head or "format=3" not in head:
        _fail(errors, f"{rel_path}: expected Godot 4 text scene header [gd_scene ... format=3]")


def validate_tilemap_room(errors: list[str], rel_path: str, root_name: str) -> None:
    """Classroom / Laboratory: root Node2D, Terrain TileMap, LPC tileset."""
    path = REPO_ROOT / rel_path
    text = _read_scene(errors, path)
    if text is None:
        return

    _validate_godot4_scene_header(errors, rel_path, text)

    if f'[node name="{root_name}" type="Node2D"]' not in text:
        _fail(errors, f'{rel_path}: missing root node [node name="{root_name}" type="Node2D"]')

    terrain = _node_section(text, "Terrain")
    if terrain is None:
        _fail(errors, f'{rel_path}: missing [node name="Terrain" ...] block')
        return

    if 'type="TileMap"' not in terrain.split("\n", 1)[0]:
        _fail(errors, f'{rel_path}: node "Terrain" must be type="TileMap"')

    if LPC_TILESET_RES not in text:
        _fail(errors, f"{rel_path}: must reference tileset {LPC_TILESET_RES}")

    if "tile_set = ExtResource(" not in terrain:
        _fail(errors, f'{rel_path}: Terrain TileMap must set tile_set = ExtResource(...)')

    if "format = 2" not in terrain:
        _fail(errors, f"{rel_path}: Terrain TileMap must use Godot 4 format = 2")


def validate_main_hall_doors(errors: list[str]) -> None:
    """Main Hall: Terrain TileMap plus Area2D doors to Classroom and Laboratory."""
    rel = Path("scenes") / "MainHall.tscn"
    path = REPO_ROOT / rel
    text = _read_scene(errors, path)
    if text is None:
        return

    _validate_godot4_scene_header(errors, str(rel), text)

    terrain = _node_section(text, "Terrain")
    if terrain is None or 'type="TileMap"' not in terrain.split("\n", 1)[0]:
        _fail(errors, f"{rel}: missing Terrain TileMap")

    if LPC_TILESET_RES not in text:
        _fail(errors, f"{rel}: must reference tileset {LPC_TILESET_RES}")

    doors = (
        ("DoorToClassroom", "res://scenes/Classroom.tscn"),
        ("DoorToLaboratory", "res://scenes/Laboratory.tscn"),
    )
    for door_name, target in doors:
        sec = _node_subtree_until_root_sibling(text, door_name)
        if sec is None:
            _fail(errors, f'{rel}: missing door node "{door_name}"')
            continue
        header = sec.split("\n", 1)[0]
        if 'type="Area2D"' not in header:
            _fail(errors, f'{rel}: "{door_name}" must be type="Area2D"')
        want = f'target_scene = "{target}"'
        if want not in sec:
            _fail(errors, f'{rel}: "{door_name}" must set {want}')
        if "CollisionShape2D" not in sec:
            _fail(errors, f'{rel}: "{door_name}" should include a CollisionShape2D child')


def main() -> int:
    errors: list[str] = []

    validate_tilemap_room(errors, str(Path("scenes") / "Classroom.tscn"), "Classroom")
    validate_tilemap_room(errors, str(Path("scenes") / "Laboratory.tscn"), "Laboratory")
    validate_main_hall_doors(errors)

    if errors:
        for msg in errors:
            print("FAIL:", msg)
        return 1

    print("Scene structure validation passed (Classroom, Laboratory, Main Hall doors).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
