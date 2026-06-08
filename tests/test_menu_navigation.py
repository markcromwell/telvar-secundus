"""Structural validation for the menu wiring produced by spec 1541 (phases 1-4).

Mirrors the text/configparser style of ``test_godot_config.py`` — no Godot
binary is launched. These checks assert the *wiring contract* between the pieces:

* the Menu autoload is registered in ``project.godot``;
* ``Menu.gd`` bridges to spec 1311's AudioSettingsPersistence and exposes the
  ``get_volume`` / ``set_volume`` accessors screens use;
* the settings screen binds its sliders to ``Menu.set_volume`` and restores them
  from ``Menu.get_volume`` (so values survive a gameplay round-trip);
* the settings, load, and credits screens each expose a back-to-main-menu
  handler, and the main menu instantiates the settings and load scenes.

The settings screen script/scene is resolved from a few candidate filenames
(``SettingsMenu.gd`` / ``settings_menu.gd``) so the test tracks whichever casing
the sibling phases landed instead of hard-coding one.
"""

from __future__ import annotations

import configparser
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

PROJECT_GODOT = REPO_ROOT / "project.godot"
MENU_SCRIPT = REPO_ROOT / "Menu.gd"
MAIN_MENU_SCRIPT = REPO_ROOT / "MainMenu.gd"
LOAD_SCREEN_SCRIPT = REPO_ROOT / "LoadScreen.gd"
CREDITS_SCRIPT = REPO_ROOT / "Credits.gd"

# The settings screen was authored by a sibling phase; accept either casing.
SETTINGS_SCRIPT_CANDIDATES = ("SettingsMenu.gd", "settings_menu.gd")


def _wrap_godot_root_section(text: str) -> str:
    """Godot may place key=value pairs before the first [section]; ConfigParser requires a section."""
    stripped = text.lstrip("﻿")
    if not stripped.lstrip().startswith("["):
        return "[__godot_root__]\n" + text
    return text


def _unquote_godot_value(raw: str) -> str:
    s = raw.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        return s[1:-1]
    return s


def _load_ini(path: Path) -> configparser.ConfigParser:
    if not path.is_file():
        pytest.fail(f"Missing required file: {path}")
    text = path.read_text(encoding="utf-8")
    if path.name == "project.godot":
        text = _wrap_godot_root_section(text)
    cp = configparser.ConfigParser(interpolation=None)
    cp.read_string(text)
    return cp


def _read(path: Path) -> str:
    if not path.is_file():
        pytest.fail(f"Missing required file: {path}")
    return path.read_text(encoding="utf-8")


def _resolve(*names: str) -> Path:
    """Return the first existing repo-root file from the candidate names."""
    for name in names:
        candidate = REPO_ROOT / name
        if candidate.is_file():
            return candidate
    pytest.fail(f"None of the candidate files exist: {', '.join(names)}")


def _settings_script() -> Path:
    return _resolve(*SETTINGS_SCRIPT_CANDIDATES)


# --- Autoload registration ------------------------------------------------


def test_menu_autoload_registered() -> None:
    """project.godot must register the Menu autoload pointing at Menu.gd."""
    cp = _load_ini(PROJECT_GODOT)
    assert cp.has_section("autoload"), "project.godot has no [autoload] section"
    value = _unquote_godot_value(cp.get("autoload", "Menu"))
    # Autoloads enabled as singletons are prefixed with '*'.
    assert value == "*res://Menu.gd", f"unexpected Menu autoload value: {value!r}"


def test_menu_script_exists() -> None:
    assert MENU_SCRIPT.is_file()


# --- Menu.gd persistence integration -------------------------------------


def test_menu_references_audio_settings_persistence() -> None:
    """Menu coordinates with spec 1311's AudioSettingsPersistence rather than a parallel system."""
    src = _read(MENU_SCRIPT)
    assert "AudioSettingsPersistence" in src


def test_menu_defines_get_and_set_volume() -> None:
    src = _read(MENU_SCRIPT)
    assert "func get_volume" in src
    assert "func set_volume" in src


# --- Settings slider binding / restore -----------------------------------


def test_settings_binds_sliders_to_menu_set_volume() -> None:
    """Slider value_changed must drive Menu.set_volume so changes persist."""
    src = _read(_settings_script())
    assert "value_changed" in src, "settings screen does not connect slider value_changed"
    assert "Menu.set_volume" in src, "settings screen does not route changes to Menu.set_volume"


def test_settings_initializes_sliders_from_menu_get_volume() -> None:
    """On open, sliders are seeded from Menu.get_volume so restored values show."""
    src = _read(_settings_script())
    assert "Menu.get_volume" in src, "settings screen does not read Menu.get_volume"
    # A read is only useful if it is assigned back onto a slider's value.
    assert ".value" in src, "settings screen never assigns a restored value to a slider"


# --- Back-to-main-menu navigation ----------------------------------------

# Screens authored by different phases expose one of these back signals.
_BACK_SIGNALS = ("back_requested", "back_pressed")


def _has_back_handler(src: str) -> bool:
    """A back-to-main-menu handler: a back-named handler plus a back signal."""
    has_handler = "_on_back" in src or "_request_back" in src
    has_signal = any(sig in src for sig in _BACK_SIGNALS)
    return has_handler and has_signal


def test_settings_has_back_handler() -> None:
    assert _has_back_handler(_read(_settings_script()))


def test_load_screen_has_back_handler() -> None:
    assert _has_back_handler(_read(LOAD_SCREEN_SCRIPT))


def test_credits_has_back_handler() -> None:
    assert _has_back_handler(_read(CREDITS_SCRIPT))


def test_main_menu_instantiates_settings_and_load_scenes() -> None:
    """MainMenu must reference both the settings and load scenes to open them."""
    src = _read(MAIN_MENU_SCRIPT)
    assert "res://LoadScreen.tscn" in src, "MainMenu does not reference the load scene"
    settings_refs = ("res://SettingsMenu.tscn", "res://settings_menu.tscn")
    assert any(ref in src for ref in settings_refs), (
        "MainMenu does not reference a settings scene"
    )
