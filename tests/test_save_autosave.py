"""Spec 2617: autosave on scene transition wiring (filesystem checks, no Godot binary)."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
PROJECT_GODOT = REPO_ROOT / "project.godot"
SAVE_MANAGER = REPO_ROOT / "game" / "save_manager.gd"
SCENE_TRANSITION = REPO_ROOT / "game" / "scene_transition.gd"


def test_save_manager_script_exists() -> None:
    assert SAVE_MANAGER.is_file()


def test_scene_transition_script_exists() -> None:
    assert SCENE_TRANSITION.is_file()


def test_autosave_path_constant() -> None:
    text = SAVE_MANAGER.read_text(encoding="utf-8")
    assert 'user://save_autosave.json' in text


def test_autosave_slot_label_constant() -> None:
    text = SAVE_MANAGER.read_text(encoding="utf-8")
    assert 'Autosave' in text


def test_autosave_silent_has_no_ui_calls() -> None:
    """Silent autosave must not open dialogs or push notifications."""
    text = SAVE_MANAGER.read_text(encoding="utf-8")
    lowered = text.lower()
    assert "acceptdialog" not in lowered
    assert "windowdialog" not in lowered
    assert "push_error" not in lowered
    assert "push_warning" not in lowered
    assert "print(" not in text  # avoid noisy console on every transition


def test_scene_transition_autosaves_before_change() -> None:
    body = SCENE_TRANSITION.read_text(encoding="utf-8")
    assert "SaveManager.autosave_silent()" in body
    for sep, load_call in (
        ("func change_scene_to_file", "get_tree().change_scene_to_file"),
        ("func change_scene_to_packed", "get_tree().change_scene_to_packed"),
    ):
        start = body.find(sep)
        assert start != -1, f"missing {sep}"
        chunk = body[start : start + 500]
        autosave_idx = chunk.find("SaveManager.autosave_silent()")
        load_idx = chunk.find(load_call)
        assert autosave_idx != -1 and load_idx != -1
        assert autosave_idx < load_idx, f"autosave must run before {load_call}"


def test_project_autoloads_registered() -> None:
    text = PROJECT_GODOT.read_text(encoding="utf-8")
    assert re.search(r'^\s*SaveManager\s*=\s*"\*res://game/save_manager\.gd"', text, re.MULTILINE)
    assert re.search(r'^\s*SceneTransition\s*=\s*"\*res://game/scene_transition\.gd"', text, re.MULTILINE)


def test_save_manager_listed_before_scene_transition() -> None:
    """SceneTransition calls SaveManager; autoload order must instantiate SaveManager first."""
    text = PROJECT_GODOT.read_text(encoding="utf-8")
    s_idx = text.find("SaveManager=")
    t_idx = text.find("SceneTransition=")
    assert s_idx != -1 and t_idx != -1
    assert s_idx < t_idx
