#!/usr/bin/env python3
"""Structural validation for Telvar Secundus Godot project (no Godot binary)."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent

_TSCN_NODE_RE = re.compile(r'^\[node name="([^"]+)" type="([^"]+)"', re.MULTILINE)


def _fail(msg: str) -> None:
    print("FAIL:", msg, file=sys.stderr)


def _tscn_node_types(tscn_text: str) -> dict[str, str]:
    """Map node name -> type from Godot 4 text scene [node ...] headers."""
    return {m.group(1): m.group(2) for m in _TSCN_NODE_RE.finditer(tscn_text)}


def _validate_dialogue_myramar(path: Path, errors: list[str]) -> None:
    if not path.is_file():
        return
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"myramar.json invalid JSON: {exc}")
        return
    if not isinstance(data, list) or not data:
        errors.append("myramar.json must be a non-empty JSON array")
        return

    ids: list[str] = []
    for i, entry in enumerate(data):
        if not isinstance(entry, dict):
            errors.append(f"myramar.json entry {i} must be an object")
            continue
        eid = entry.get("id")
        text = entry.get("text")
        speaker = entry.get("speaker")
        if not isinstance(eid, str) or not eid:
            errors.append(f"myramar.json entry {i} needs non-empty string id")
        if not isinstance(text, str):
            errors.append(f"myramar.json entry {i} needs string text")
        if not isinstance(speaker, str):
            errors.append(f"myramar.json entry {i} needs string speaker")
        if isinstance(eid, str) and eid:
            ids.append(eid)
        nxt = entry.get("next")
        if nxt is not None and (not isinstance(nxt, str) or not nxt):
            errors.append(f"myramar.json entry {i} next must be a non-empty string if present")

    if len(ids) != len(set(ids)):
        errors.append("myramar.json dialogue ids must be unique")

    id_set = set(ids)
    for entry in data:
        if not isinstance(entry, dict):
            continue
        nxt = entry.get("next")
        eid = entry.get("id", "?")
        if isinstance(nxt, str) and nxt and nxt not in id_set:
            errors.append(f"myramar.json unknown next id {nxt!r} from {eid!r}")

    combined = "\n".join(e["text"] for e in data if isinstance(e, dict) and isinstance(e.get("text"), str))
    if "Telvar Orsson" not in combined:
        errors.append("myramar.json candidate list reveal must name Telvar Orsson")
    if "start" not in id_set or "desk" not in id_set:
        errors.append("myramar.json must define start and desk dialogue entry ids")


def _validate_council_chamber_tscn(path: Path, errors: list[str]) -> None:
    if not path.is_file():
        return
    t = path.read_text(encoding="utf-8")
    for needle in ("res://scenes/council_chamber/council_chamber.gd", "res://assets/tilesets/lpc_terrain.tres"):
        if needle not in t:
            errors.append(f"council_chamber.tscn must reference {needle!r}")
    if 'type="TileMap"' not in t or "layer_0/tile_data = PackedInt32Array()" not in t:
        errors.append("council_chamber.tscn must declare a TileMap with layer_0 tile_data")
    if "scale = Vector2(2, 2)" not in t:
        errors.append("council_chamber.tscn TileMap must use 2x display scale")
    nodes = _tscn_node_types(t)
    expect = {
        "CouncilChamber": "Node2D",
        "Terrain": "TileMap",
        "TowerStairsExit": "Area2D",
        "OfficeDoor": "Area2D",
    }
    for name, want_type in expect.items():
        got = nodes.get(name)
        if got != want_type:
            errors.append(
                f"council_chamber.tscn node {name!r} must be type {want_type!r}, got {got!r}"
            )


def _validate_myramar_office_tscn(path: Path, errors: list[str]) -> None:
    if not path.is_file():
        return
    t = path.read_text(encoding="utf-8")
    for needle in ("res://scenes/myramar_office/myramar_office.gd", "res://assets/tilesets/lpc_terrain.tres"):
        if needle not in t:
            errors.append(f"myramar_office.tscn must reference {needle!r}")
    if 'type="TileMap"' not in t or "layer_0/tile_data = PackedInt32Array()" not in t:
        errors.append("myramar_office.tscn must declare a TileMap with layer_0 tile_data")
    if "scale = Vector2(2, 2)" not in t:
        errors.append("myramar_office.tscn TileMap must use 2x display scale")
    nodes = _tscn_node_types(t)
    expect = {
        "MyramarOffice": "Node2D",
        "Terrain": "TileMap",
        "CouncilReturn": "Area2D",
        "MyramarTalkArea": "Area2D",
        "DeskInspectArea": "Area2D",
    }
    for name, want_type in expect.items():
        got = nodes.get(name)
        if got != want_type:
            errors.append(
                f"myramar_office.tscn node {name!r} must be type {want_type!r}, got {got!r}"
            )


def _validate_council_chamber_gd(path: Path, errors: list[str]) -> None:
    if not path.is_file():
        return
    gd = path.read_text(encoding="utf-8")
    for needle, msg in (
        ("const GRID_SIZE := 12", "council_chamber.gd must define 12x12 grid"),
        ("set_cell", "council_chamber.gd must place tiles via set_cell"),
        ("TowerStairsExit", "council_chamber.gd must reference TowerStairsExit"),
        ("OfficeDoor", "council_chamber.gd must reference OfficeDoor"),
        ("OFFICE_DOOR_MIN", "council_chamber.gd must define office door cell constants"),
        ("DialogueManager", "council_chamber.gd must use DialogueManager"),
        ("myramar_office.tscn", "council_chamber.gd must transition to myramar_office.tscn"),
        ('get_flag("act"', "council_chamber.gd must gate office on act flag"),
    ):
        if needle not in gd:
            errors.append(msg)


def _validate_myramar_office_gd(path: Path, errors: list[str]) -> None:
    if not path.is_file():
        return
    gd = path.read_text(encoding="utf-8")
    for needle, msg in (
        ("const OFFICE_W := 10", "myramar_office.gd must define office width 10"),
        ("const OFFICE_H := 8", "myramar_office.gd must define office height 8"),
        ('show_dialogue("myramar"', "myramar_office.gd must call show_dialogue for myramar"),
        ('"desk"', "myramar_office.gd must open desk dialogue branch"),
        ('get_flag("act"', "myramar_office.gd must read act flag for Act 2+ gating"),
        ("council_chamber.tscn", "myramar_office.gd must return to council_chamber.tscn"),
        ("MYRAMAR_DIALOGUE", "myramar_office.gd must reference MYRAMAR_DIALOGUE constant"),
    ):
        if needle not in gd:
            errors.append(msg)


def main() -> int:
    errors: list[str] = []

    required = [
        REPO_ROOT / "project.godot",
        REPO_ROOT / "assets" / "tilesets" / "lpc_terrain.png",
        REPO_ROOT / "assets" / "tilesets" / "lpc_terrain.tres",
        REPO_ROOT / "assets" / "dialogue" / "myramar.json",
        REPO_ROOT / "scenes" / "council_chamber" / "council_chamber.tscn",
        REPO_ROOT / "scenes" / "council_chamber" / "council_chamber.gd",
        REPO_ROOT / "scenes" / "myramar_office" / "myramar_office.tscn",
        REPO_ROOT / "scenes" / "myramar_office" / "myramar_office.gd",
        REPO_ROOT / "autoload" / "dialogue_manager.gd",
    ]
    for path in required:
        if not path.is_file():
            errors.append(f"Missing required file: {path.relative_to(REPO_ROOT)}")

    pg = REPO_ROOT / "project.godot"
    if pg.is_file():
        text = pg.read_text(encoding="utf-8")
        if "[autoload]" not in text:
            errors.append("project.godot must define an [autoload] section")
        elif "autoload/dialogue_manager.gd" not in text:
            errors.append("project.godot must register DialogueManager autoload script")

    cc = REPO_ROOT / "scenes" / "council_chamber" / "council_chamber.tscn"
    _validate_council_chamber_tscn(cc, errors)

    mo = REPO_ROOT / "scenes" / "myramar_office" / "myramar_office.tscn"
    _validate_myramar_office_tscn(mo, errors)

    cc_gd = REPO_ROOT / "scenes" / "council_chamber" / "council_chamber.gd"
    _validate_council_chamber_gd(cc_gd, errors)

    mo_gd = REPO_ROOT / "scenes" / "myramar_office" / "myramar_office.gd"
    _validate_myramar_office_gd(mo_gd, errors)

    tres = REPO_ROOT / "assets" / "tilesets" / "lpc_terrain.tres"
    if tres.is_file():
        tt = tres.read_text(encoding="utf-8")
        if "4:0/0 = 0" not in tt or "5:0/0 = 0" not in tt or "6:0/0 = 0" not in tt:
            errors.append("lpc_terrain.tres must define atlas columns 4–6 for office props")

    dial = REPO_ROOT / "assets" / "dialogue" / "myramar.json"
    _validate_dialogue_myramar(dial, errors)

    dm = REPO_ROOT / "autoload" / "dialogue_manager.gd"
    if dm.is_file():
        dmt = dm.read_text(encoding="utf-8")
        for needle, msg in (
            ("func show_dialogue", "dialogue_manager.gd must define show_dialogue"),
            ("func get_flag", "dialogue_manager.gd must define get_flag"),
        ):
            if needle not in dmt:
                errors.append(msg)

    if errors:
        for e in errors:
            _fail(e)
        return 1

    print("validate.py: structural checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
