"""Structural checks for CombatManager → AudioManager integration (phase 2742)."""

from __future__ import annotations

import configparser
from pathlib import Path

import pytest

from tests.test_godot_config import _unquote_godot_value

REPO_ROOT = Path(__file__).resolve().parents[1]
PROJECT_GODOT = REPO_ROOT / "project.godot"
COMBAT_MANAGER_GD = REPO_ROOT / "autoload" / "CombatManager.gd"
COMBAT_MANAGER_TSCN = REPO_ROOT / "autoload" / "CombatManager.tscn"


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


def test_combat_manager_gd_exists() -> None:
    assert COMBAT_MANAGER_GD.is_file(), "autoload/CombatManager.gd must exist"


def test_combat_manager_tscn_exists() -> None:
    assert COMBAT_MANAGER_TSCN.is_file(), "autoload/CombatManager.tscn must exist"


def test_project_autoload_registers_combat_manager_after_audio() -> None:
    cp = _load_project_godot()
    assert cp.has_section("autoload"), "project.godot must define [autoload]"
    assert cp.has_option("autoload", "CombatManager")
    raw = _unquote_godot_value(cp.get("autoload", "CombatManager"))
    assert "res://autoload/CombatManager.tscn" in raw
    assert raw.startswith("*"), "CombatManager should be a singleton autoload (* prefix)"

    text = PROJECT_GODOT.read_text(encoding="utf-8")
    in_autoload = False
    order: list[str] = []
    for line in text.splitlines():
        s = line.strip()
        if s == "[autoload]":
            in_autoload = True
            continue
        if in_autoload:
            if s.startswith("[") and s.endswith("]"):
                break
            if "=" in s and not s.startswith(";"):
                order.append(s.split("=", 1)[0].strip())
    assert "AudioManager" in order and "CombatManager" in order
    assert order.index("AudioManager") < order.index("CombatManager"), (
        "AudioManager must be declared before CombatManager so the singleton exists at parse time"
    )


def test_combat_manager_wires_audio_manager_lifecycle() -> None:
    src = COMBAT_MANAGER_GD.read_text(encoding="utf-8")
    assert "AudioManager.enter_combat" in src
    assert "AudioManager.play_victory_sting" in src
    assert "AudioManager.exit_combat_resume_ambient_only" in src
    assert "on_combat_started" in src
    assert "on_combat_victory" in src
