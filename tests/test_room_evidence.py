"""Structural checks for room + DialogueManager evidence flow (spec phase 2712)."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ROOM_SCRIPT = REPO_ROOT / "scripts" / "room.gd"
ROOM_SCENE = REPO_ROOT / "scenes" / "room.tscn"
DIALOGUE_MANAGER = REPO_ROOT / "scripts" / "dialogue_manager.gd"
PROJECT_GODOT = REPO_ROOT / "project.godot"


def test_room_script_triggers_post_evidence_dialogue() -> None:
    src = ROOM_SCRIPT.read_text(encoding="utf-8")
    assert "evidence_collected" in src
    assert "after_evidence_choice" in src
    assert "show_dialogue" in src


def test_room_scene_references_room_script() -> None:
    text = ROOM_SCENE.read_text(encoding="utf-8")
    assert 'path="res://scripts/room.gd"' in text


def test_dialogue_manager_autoload_configured() -> None:
    text = PROJECT_GODOT.read_text(encoding="utf-8")
    assert "DialogueManager=" in text
    assert "scripts/dialogue_manager.gd" in text


def test_dialogue_manager_handles_outcomes() -> None:
    src = DIALOGUE_MANAGER.read_text(encoding="utf-8")
    assert "game_over_save_prompt" in src
    assert "transition_wings" in src
    assert "change_scene_to_file" in src
    assert "res://scenes/game_over.tscn" in src
    assert "res://scenes/wings.tscn" in src


def test_dialogue_manager_resolved_flag_constant() -> None:
    src = DIALOGUE_MANAGER.read_text(encoding="utf-8")
    assert "myramar_evidence_branch_resolved" in src
