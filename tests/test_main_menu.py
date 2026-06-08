"""Filesystem validation for the MainMenu scene and its wiring.

Mirrors the configparser/no-Godot-binary pattern of test_godot_config.py: every
assertion reads project.godot, the .tscn/.gd text, or checks file presence. No
Godot binary is imported and no scene is instantiated.

project.godot's run/main_scene points at res://scenes/MainMenu.tscn (set by the
project.godot-owning phase); the scene/script files themselves may live there or
at the repo root depending on integration layout, so the scene is resolved from
a candidate list rather than a single hard-coded path.
"""

from __future__ import annotations

import configparser
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
PROJECT_GODOT = REPO_ROOT / "project.godot"
MENU_AUTOLOAD = REPO_ROOT / "autoload" / "Menu.gd"
CREDITS_MD = REPO_ROOT / "CREDITS.md"

MAIN_SCENE_RES_PATH = "res://scenes/MainMenu.tscn"
EXPECTED_BUTTON_LABELS = ("New Game", "Load", "Settings", "Credits")

# The scene/script may be assembled under scenes/ or at the repo root.
MAIN_MENU_SCENE_CANDIDATES = (
    REPO_ROOT / "scenes" / "MainMenu.tscn",
    REPO_ROOT / "MainMenu.tscn",
)


def _wrap_godot_root_section(text: str) -> str:
    """Godot may place key=value pairs before the first [section]; ConfigParser requires a section."""
    stripped = text.lstrip("\ufeff")
    if not stripped.lstrip().startswith("["):
        return "[__godot_root__]\n" + text
    return text


def _unquote_godot_value(raw: str) -> str:
    s = raw.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        return s[1:-1]
    return s


def _load_project_godot() -> configparser.ConfigParser:
    if not PROJECT_GODOT.is_file():
        pytest.fail(f"Missing required file: {PROJECT_GODOT}")
    text = _wrap_godot_root_section(PROJECT_GODOT.read_text(encoding="utf-8"))
    cp = configparser.ConfigParser(interpolation=None)
    cp.optionxform = str  # preserve key case (e.g. the "Menu" autoload name)
    cp.read_string(text)
    return cp


def _resolve_main_menu_scene() -> Path:
    for candidate in MAIN_MENU_SCENE_CANDIDATES:
        if candidate.is_file():
            return candidate
    pytest.fail(
        "MainMenu.tscn not found in any expected location: "
        + ", ".join(str(c) for c in MAIN_MENU_SCENE_CANDIDATES)
    )


def test_project_godot_exists() -> None:
    assert PROJECT_GODOT.is_file()


def test_project_registers_menu_autoload() -> None:
    cp = _load_project_godot()
    assert cp.has_section("autoload"), "project.godot has no [autoload] section"
    assert "Menu" in cp.options("autoload"), "Menu autoload not registered"
    value = _unquote_godot_value(cp.get("autoload", "Menu"))
    # Leading '*' marks the autoload as a singleton Node in Godot 4.
    assert value.lstrip("*") == "res://autoload/Menu.gd"


def test_project_main_scene_is_main_menu() -> None:
    cp = _load_project_godot()
    main_scene = _unquote_godot_value(cp.get("application", "run/main_scene"))
    assert main_scene == MAIN_SCENE_RES_PATH


def test_main_menu_scene_exists() -> None:
    assert _resolve_main_menu_scene().is_file()


def test_main_menu_scene_references_script() -> None:
    tscn = _resolve_main_menu_scene().read_text(encoding="utf-8")
    assert "MainMenu.gd" in tscn, "MainMenu.tscn does not reference MainMenu.gd"


def test_main_menu_scene_has_four_button_labels() -> None:
    tscn = _resolve_main_menu_scene().read_text(encoding="utf-8")
    assert tscn.count('type="Button"') >= 4, "expected at least four Button nodes"
    for label in EXPECTED_BUTTON_LABELS:
        assert f'text = "{label}"' in tscn, f"missing button label: {label}"


def test_menu_autoload_script_exists() -> None:
    assert MENU_AUTOLOAD.is_file()


def test_menu_autoload_script_signature() -> None:
    src = MENU_AUTOLOAD.read_text(encoding="utf-8")
    assert "extends Node" in src, "Menu autoload must extend Node"
    # The four request entry points the menu buttons route through.
    for func in (
        "request_new_game",
        "request_load_game",
        "request_settings",
        "request_credits",
    ):
        assert f"func {func}" in src, f"Menu autoload missing func {func}"


def test_credits_md_exists() -> None:
    assert CREDITS_MD.is_file()
