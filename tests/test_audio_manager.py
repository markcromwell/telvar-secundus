"""Structural checks for AudioManager autoload (Godot 4.3, phase 2741)."""

from __future__ import annotations

import configparser
from pathlib import Path

import pytest

from tests.test_godot_config import _unquote_godot_value

REPO_ROOT = Path(__file__).resolve().parents[1]
PROJECT_GODOT = REPO_ROOT / "project.godot"
AUDIO_MANAGER_GD = REPO_ROOT / "autoload" / "AudioManager.gd"
AUDIO_MANAGER_TSCN = REPO_ROOT / "autoload" / "AudioManager.tscn"


def _wrap_godot_root_section(text: str) -> str:
    stripped = text.lstrip("\ufeff")
    if not stripped.lstrip().startswith("["):
        return "[__godot_root__]\n" + text
    return text


def _load_project_godot() -> configparser.ConfigParser:
    text = PROJECT_GODOT.read_text(encoding="utf-8")
    text = _wrap_godot_root_section(text)
    cp = configparser.ConfigParser(interpolation=None)
    cp.read_string(text)
    return cp


def test_audio_manager_gd_exists() -> None:
    assert AUDIO_MANAGER_GD.is_file(), "autoload/AudioManager.gd must exist"


def test_audio_manager_tscn_exists() -> None:
    assert AUDIO_MANAGER_TSCN.is_file(), "autoload/AudioManager.tscn must exist"


def test_project_autoload_registers_audio_manager() -> None:
    cp = _load_project_godot()
    assert cp.has_section("autoload"), "project.godot must define [autoload]"
    assert cp.has_option("autoload", "AudioManager")
    raw = _unquote_godot_value(cp.get("autoload", "AudioManager"))
    assert "res://autoload/AudioManager.tscn" in raw
    assert raw.startswith("*"), "AudioManager should be a singleton autoload (* prefix)"


def test_audio_manager_tscn_has_dedicated_stream_players() -> None:
    body = AUDIO_MANAGER_TSCN.read_text(encoding="utf-8")
    assert 'type="AudioStreamPlayer"' in body
    assert '[node name="AmbientPlayer"' in body
    assert '[node name="CombatPlayer"' in body
    assert '[node name="VictoryStingPlayer"' in body


def test_audio_manager_gd_has_tween_fade_and_victory_api() -> None:
    src = AUDIO_MANAGER_GD.read_text(encoding="utf-8")
    assert "fade_out_ambient" in src
    assert "create_tween()" in src
    assert "play_victory_sting" in src
    assert "0.5" in src or "FADE_OUT_AMBIENT_SEC" in src
