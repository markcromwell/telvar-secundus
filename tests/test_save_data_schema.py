"""Parity tests for game/save_data_schema.gd merge + JSON round-trip.

Godot is not invoked in CI. Logic here must match SaveDataSchema in GDScript;
when changing defaults or merge_with_defaults, update both files.
"""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SAVE_SCHEMA_GD = REPO_ROOT / "game" / "save_data_schema.gd"

# Root keys from SaveDataSchema.default_save_dict() — keep in sync with game/save_data_schema.gd
EXPECTED_ROOT_KEYS: frozenset[str] = frozenset(
    {
        "version",
        "scene_path",
        "tile_coords",
        "quest_state",
        "lore_entries",
        "inventory",
        "hp",
        "max_hp",
        "mana",
        "max_mana",
        "act_flags",
        "dialogue_flags",
        "play_time_seconds",
    }
)

SCHEMA_VERSION = 1


def _default_save_dict() -> dict:
    return {
        "version": SCHEMA_VERSION,
        "scene_path": "",
        "tile_coords": {"x": 0, "y": 0},
        "quest_state": {},
        "lore_entries": [],
        "inventory": {},
        "hp": 1.0,
        "max_hp": 1.0,
        "mana": 0.0,
        "max_mana": 0.0,
        "act_flags": {},
        "dialogue_flags": {},
        "play_time_seconds": 0.0,
    }


def _merge_with_defaults(data: dict) -> dict:
    out = copy.deepcopy(_default_save_dict())
    for k, v in data.items():
        if k == "tile_coords" and isinstance(v, dict):
            merged = dict(out["tile_coords"])
            for ck, cv in v.items():
                merged[ck] = cv
            out["tile_coords"] = merged
        else:
            out[k] = v
    return out


def _export_state_to_dictionary(state: dict) -> dict:
    return copy.deepcopy(_merge_with_defaults(state))


def _populate_state_from_dictionary(target: dict, source: dict) -> None:
    merged = copy.deepcopy(_merge_with_defaults(source))
    target.clear()
    for k, v in merged.items():
        target[k] = v


def _to_json_string(data: dict, *, pretty: bool = False) -> str:
    if pretty:
        return json.dumps(data, indent="\t", ensure_ascii=False)
    return json.dumps(data, separators=(",", ":"), ensure_ascii=False)


def _from_json_string(text: str) -> dict:
    stripped = text.strip()
    if not stripped:
        return {}
    try:
        root = json.loads(stripped)
    except json.JSONDecodeError:
        return {}
    if not isinstance(root, dict):
        return {}
    return copy.deepcopy(root)


def _round_trip(data: dict) -> dict:
    return _from_json_string(_to_json_string(data, pretty=False))


def _deep_equal(a: object, b: object) -> bool:
    if type(a) is not type(b):
        # allow int vs float for JSON numeric round-trip
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            return float(a) == float(b)
        return False
    if isinstance(a, dict):
        if set(a) != set(b):
            return False
        return all(_deep_equal(a[k], b[k]) for k in a)
    if isinstance(a, list):
        if len(a) != len(b):
            return False
        return all(_deep_equal(x, y) for x, y in zip(a, b, strict=True))
    return a == b


def _default_save_dict_block(gd_text: str) -> str:
    marker = "static func default_save_dict"
    start = gd_text.index(marker)
    rest = gd_text[start:]
    next_fn = re.search(r"\nstatic func ", rest[len(marker) :])
    if next_fn is None:
        return rest
    return rest[: len(marker) + next_fn.start()]


def test_save_schema_gd_file_exists() -> None:
    assert SAVE_SCHEMA_GD.is_file()


def test_save_schema_paths_and_class_documented() -> None:
    text = SAVE_SCHEMA_GD.read_text(encoding="utf-8")
    assert 'SLOT_PATH_TEMPLATE := "user://save_slot_%d.json"' in text
    assert 'AUTOSAVE_PATH := "user://save_autosave.json"' in text
    assert "class_name SaveDataSchema" in text


def test_default_save_dict_defines_all_expected_keys() -> None:
    block = _default_save_dict_block(SAVE_SCHEMA_GD.read_text(encoding="utf-8"))
    for key in EXPECTED_ROOT_KEYS:
        assert f'"{key}"' in block, f"missing default key {key!r} in default_save_dict"


def test_merge_tile_coords_partial_does_not_drop_axis() -> None:
    merged = _merge_with_defaults({"tile_coords": {"x": 9}})
    assert merged["tile_coords"]["x"] == 9
    assert merged["tile_coords"]["y"] == 0


def test_merge_preserves_nested_quest_and_inventory() -> None:
    payload = {
        "quest_state": {"main": {"stage": 2, "flags": ["a", "b"]}, "side_x": True},
        "inventory": {"potion": 3, "nested": {"slot": "wand"}},
        "lore_entries": ["lore_a", "lore_b"],
    }
    merged = _merge_with_defaults(payload)
    assert _deep_equal(merged["quest_state"], payload["quest_state"])
    assert _deep_equal(merged["inventory"], payload["inventory"])
    assert merged["lore_entries"] == payload["lore_entries"]


def test_merge_unknown_top_level_key_round_trips() -> None:
    data = _merge_with_defaults({"future_field": {"a": 1}})
    back = _round_trip(data)
    assert _deep_equal(back, data)


def test_json_round_trip_no_data_loss_quest_inventory() -> None:
    doc = _merge_with_defaults(
        {
            "scene_path": "res://maps/secundus_street.tscn",
            "quest_state": {"trial": 1, "nested": {"k": [1, 2, 3]}},
            "inventory": {"gold": 42, "stack": {"id": "ember", "qty": 2}},
            "dialogue_flags": {"met_myramar": True},
            "play_time_seconds": 3600.5,
        }
    )
    rt = _round_trip(doc)
    assert _deep_equal(rt, doc)


def test_export_then_populate_matches_merge() -> None:
    partial = {"hp": 10.0, "mana": 5.0, "inventory": {"gem": 1}}
    snap = _export_state_to_dictionary(partial)
    live: dict = {"stale": True, "hp": 0.0}
    _populate_state_from_dictionary(live, snap)
    assert "stale" not in live
    assert _deep_equal(live, snap)
    assert live["inventory"]["gem"] == 1


def test_schema_version_constant_matches_python_mirror() -> None:
    text = SAVE_SCHEMA_GD.read_text(encoding="utf-8")
    m = re.search(r"const\s+SCHEMA_VERSION\s*:=\s*(\d+)", text)
    assert m is not None
    assert int(m.group(1)) == SCHEMA_VERSION
