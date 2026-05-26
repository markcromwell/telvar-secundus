#!/usr/bin/env python3
"""
Structural validation for Telvar Secundus Godot project (no Godot binary).

Checks quest JSON and Aelyn's room scene text per spec phase 2693.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent

QUEST_PATH = REPO_ROOT / "assets" / "quests" / "where_is_aelyn.json"
ROOM_SCENE_PATH = REPO_ROOT / "scenes" / "rooms" / "aelyns_room.tscn"

NOTE_TEXT = "Exiled to Antica. Reason: [blank]"

# Node names suggesting furniture / belongings (substring match on extracted name, lowercased).
_FORBIDDEN_NODE_NAME_SUBSTRINGS = (
    "bed",
    "chest",
    "dresser",
    "bookshelf",
    "wardrobe",
    "desk",
    "chair",
    "nightstand",
    "trunk",
    "locker",
    "cabinet",
    "closet",
    "mirror",
    "rug",
    "lamp",
    "shelf",
    "drawer",
    "bureau",
    "armoire",
)

_NODE_LINE_RE = re.compile(r'^\[node name="([^"]+)"')


def _fail(errors: list[str], msg: str) -> None:
    errors.append(msg)


def _validate_quest_json(errors: list[str]) -> None:
    if not QUEST_PATH.is_file():
        _fail(errors, f"Missing quest file: {QUEST_PATH.relative_to(REPO_ROOT)}")
        return
    try:
        data = json.loads(QUEST_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        _fail(errors, f"Invalid JSON in {QUEST_PATH.relative_to(REPO_ROOT)}: {exc}")
        return
    if not isinstance(data, dict):
        _fail(errors, "Quest JSON root must be an object")
        return
    qid = data.get("id")
    if qid != "where_is_aelyn":
        _fail(errors, f'Quest id must be "where_is_aelyn", got {qid!r}')
    title = data.get("title")
    if title != "Where is Aelyn?":
        _fail(errors, f'Quest title must be "Where is Aelyn?", got {title!r}')
    objectives = data.get("objectives")
    if not isinstance(objectives, list) or len(objectives) < 1:
        _fail(errors, "Quest must include a non-empty objectives array")
        return
    seen: set[str] = set()
    for i, obj in enumerate(objectives):
        if not isinstance(obj, dict):
            _fail(errors, f"objectives[{i}] must be an object")
            continue
        oid = obj.get("id")
        desc = obj.get("desc")
        if not isinstance(oid, str) or not oid.strip():
            _fail(errors, f"objectives[{i}].id must be a non-empty string")
        elif oid in seen:
            _fail(errors, f'Duplicate objective id: {oid!r}')
        else:
            seen.add(oid)
        if not isinstance(desc, str) or not desc.strip():
            _fail(errors, f"objectives[{i}].desc must be a non-empty string")
    required = {"enter_aelyns_room", "read_floor_note"}
    missing = required - seen
    if missing:
        _fail(errors, f"Quest missing required objective ids: {sorted(missing)}")


def _collect_node_names(scene_text: str) -> list[str]:
    names: list[str] = []
    for line in scene_text.splitlines():
        m = _NODE_LINE_RE.match(line.strip())
        if m:
            names.append(m.group(1))
    return names


def _validate_room_scene(errors: list[str]) -> None:
    if not ROOM_SCENE_PATH.is_file():
        _fail(errors, f"Missing room scene: {ROOM_SCENE_PATH.relative_to(REPO_ROOT)}")
        return
    text = ROOM_SCENE_PATH.read_text(encoding="utf-8")
    if not text.startswith("[gd_scene"):
        _fail(errors, "Room scene must start with [gd_scene")
    if "TileMapLayer" not in text:
        _fail(errors, "Room scene must include a TileMapLayer (floor)")
    if "res://assets/tilesets/lpc_terrain.png" not in text:
        _fail(errors, "Room scene must reference lpc_terrain.png tileset")
    if "FloorNote" not in text:
        _fail(errors, "Room scene must include FloorNote pickup area")
    # Exact label copy for the floor note (Godot serializes as text = "...")
    if f'text = "{NOTE_TEXT}"' not in text:
        _fail(
            errors,
            f'Floor note Label must set text = "{NOTE_TEXT}" (exact match)',
        )
    # Empty quarters: no instanced furniture scenes
    if re.search(r'type="PackedScene"', text):
        _fail(errors, "Empty room must not instance PackedScene furniture assets")
    # No obvious belonging / furniture node names
    for name in _collect_node_names(text):
        lower = name.lower()
        for bad in _FORBIDDEN_NODE_NAME_SUBSTRINGS:
            if bad in lower:
                _fail(
                    errors,
                    f'Room scene node name {name!r} suggests belongings/furniture ("{bad}")',
                )
                break


def main() -> int:
    errors: list[str] = []
    _validate_quest_json(errors)
    _validate_room_scene(errors)
    if errors:
        for e in errors:
            print("FAIL:", e)
        return 1
    print("validate.py: quest JSON and Aelyn's room scene checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
