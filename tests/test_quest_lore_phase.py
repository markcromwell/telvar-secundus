"""Phase 2561: quest/lore JSON, autoload scripts, and project.godot wiring."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
QUEST_JSON = REPO_ROOT / "assets" / "quests" / "merchants_delivery.json"
LORE_JSON = REPO_ROOT / "assets" / "lore" / "lore_entries.json"
QUEST_MANAGER = REPO_ROOT / "scripts" / "quest_manager.gd"
LORE_MANAGER = REPO_ROOT / "scripts" / "lore_manager.gd"
PROJECT_GODOT = REPO_ROOT / "project.godot"


def test_merchants_delivery_quest_json() -> None:
    assert QUEST_JSON.is_file()
    data = json.loads(QUEST_JSON.read_text(encoding="utf-8"))
    assert data["id"] == "merchants_delivery"
    assert isinstance(data["title"], str) and data["title"]
    objs = data["objectives"]
    assert isinstance(objs, list) and objs
    for o in objs:
        assert "id" in o and "desc" in o
        assert isinstance(o["id"], str) and o["id"]
        assert isinstance(o["desc"], str) and o["desc"]


def test_lore_entries_json() -> None:
    assert LORE_JSON.is_file()
    data = json.loads(LORE_JSON.read_text(encoding="utf-8"))
    assert isinstance(data, list) and data
    entry = data[0]
    for key in ("id", "title", "text"):
        assert key in entry
        assert isinstance(entry[key], str) and entry[key]


def test_quest_manager_script_contract() -> None:
    text = QUEST_MANAGER.read_text(encoding="utf-8")
    assert "var quests: Dictionary" in text
    for name in ("start_quest", "complete_objective", "is_complete"):
        assert f"func {name}" in text
    assert "signal quest_updated" in text
    assert "signal objective_completed" in text


def test_lore_manager_script_contract() -> None:
    text = LORE_MANAGER.read_text(encoding="utf-8")
    assert "var unlocked: Array[String]" in text
    assert "func unlock" in text
    assert "func is_unlocked" in text
    assert "signal lore_unlocked" in text


def test_project_godot_autoloads_and_open_journal() -> None:
    raw = PROJECT_GODOT.read_text(encoding="utf-8")
    assert '[autoload]' in raw
    assert 'QuestManager="*res://scripts/quest_manager.gd"' in raw
    assert 'LoreManager="*res://scripts/lore_manager.gd"' in raw
    assert "[input]" in raw
    assert "open_journal=" in raw
    # KEY_J (Godot Key enum value 74) in serialized InputEventKey
    assert '"keycode":74' in raw
