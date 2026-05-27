"""JSON save schema checks (mirrors scripts/save_manager.gd contract)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "fixtures" / "save_valid_v1.json"

REQUIRED_TOP_LEVEL = (
    "format_version",
    "timestamp_unix",
    "act_number",
    "current_quest_name",
    "scene_path",
    "player",
    "inventory",
    "quest_state",
    "flags",
)


def test_save_fixture_exists() -> None:
    assert FIXTURE.is_file(), f"Missing fixture: {FIXTURE}"


def test_save_fixture_parses_and_has_required_keys() -> None:
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    for key in REQUIRED_TOP_LEVEL:
        assert key in data
    assert data["format_version"] == 1
    assert isinstance(data["timestamp_unix"], int)
    assert isinstance(data["act_number"], int)
    assert isinstance(data["current_quest_name"], str)
    assert isinstance(data["scene_path"], str)
    assert isinstance(data["player"], dict)
    assert "position" in data["player"]
    assert isinstance(data["player"]["position"], dict)
    assert isinstance(data["inventory"], list)
    assert isinstance(data["quest_state"], dict)
    assert isinstance(data["flags"], dict)


def test_save_manager_gd_exists_and_declares_constants() -> None:
    gd = REPO_ROOT / "scripts" / "save_manager.gd"
    text = gd.read_text(encoding="utf-8")
    assert "SAVE_FORMAT_VERSION" in text
    assert "SLOT_COUNT" in text
    assert "read_slot_metadata" in text
    assert "read_save_dict" in text
    assert "restore_from_slot" in text


def test_gdunit_save_manager_suite_and_stubs_exist() -> None:
    """CI smoke: GdUnit suite is present (Godot runs it via gdUnit4 plugin)."""
    suite = REPO_ROOT / "tests" / "gdunit" / "test_save_manager.gd"
    assert suite.is_file()
    body = suite.read_text(encoding="utf-8")
    assert "extends GdUnitTestSuite" in body
    for name in (
        "save_test_inventory.gd",
        "save_test_quest_state.gd",
        "save_test_flags.gd",
    ):
        assert (suite.parent / name).is_file()
