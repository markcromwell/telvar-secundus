"""Spec 2701: sealed-wings night event wiring and quest copy (filesystem + INI checks)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.test_godot_config import REPO_ROOT, _load_ini, PROJECT_GODOT

QUEST_JSON = REPO_ROOT / "data" / "quests" / "sealed_wings.json"
NIGHT_SCRIPT = REPO_ROOT / "scripts" / "night_scenes" / "sealed_wings_post_rest_event.gd"
TELVAR_ROOM_SCENE = REPO_ROOT / "scenes" / "telvar_room.tscn"
EXPECTED_OBJECTIVE = "I know what Myramar wants. He wants me to go in there."


def test_sealed_wings_quest_json_has_exact_post_rest_line() -> None:
    data = json.loads(QUEST_JSON.read_text(encoding="utf-8"))
    lines = data["objective_lines"]
    assert lines["after_telvar_room_rest_night"] == EXPECTED_OBJECTIVE


def test_night_event_script_has_no_dialogue_hooks() -> None:
    text = NIGHT_SCRIPT.read_text(encoding="utf-8")
    lowered = text.lower()
    for banned in ("dialogue", "acceptdialog", "window_title", "rich_text"):
        assert banned not in lowered


def test_telvar_room_scene_references_night_runner_and_growl() -> None:
    body = TELVAR_ROOM_SCENE.read_text(encoding="utf-8")
    assert "sealed_wings_post_rest_event.gd" in body
    assert "growl.wav" in body
    assert "SealedWingGrowl" in body
    assert "MyramarSpawn" in body


def test_project_autoloads_and_main_scene() -> None:
    cp = _load_ini(PROJECT_GODOT)
    assert cp.has_section("autoload")
    assert "GameFlags" in cp["autoload"]
    assert "QuestLog" in cp["autoload"]
    main = cp.get("application", "run/main_scene")
    assert main.strip('"') == "res://scenes/telvar_room.tscn"
