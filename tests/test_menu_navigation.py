"""Structural validation for menu settings/navigation wiring (spec 1541).

Verifies the autoload registration, volume-persistence integration, slider
binding/restore logic, and back-to-main-menu navigation produced by the
sibling phases of this spec. Text/configparser based only — no Godot binary,
matching the style of tests/test_godot_config.py.

The settings screen is resolved across naming conventions (PascalCase
``SettingsMenu`` and snake_case ``settings_menu``) so the test validates the
wiring that the sibling phases actually shipped rather than a fixed filename.
"""

from __future__ import annotations

import configparser
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

PROJECT_GODOT = REPO_ROOT / "project.godot"
MENU_SCRIPT = REPO_ROOT / "Menu.gd"
LOAD_SCRIPT = REPO_ROOT / "LoadScreen.gd"
CREDITS_SCRIPT = REPO_ROOT / "Credits.gd"
MAIN_MENU_SCRIPT = REPO_ROOT / "MainMenu.gd"

# The settings screen has been authored under either naming convention by the
# sibling phase; accept whichever was shipped.
SETTINGS_SCRIPT_CANDIDATES = ("SettingsMenu.gd", "settings_menu.gd")
SETTINGS_SCENE_CANDIDATES = ("SettingsMenu.tscn", "settings_menu.tscn")


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


def _first_existing(candidates: tuple[str, ...]) -> Path:
    for name in candidates:
        candidate = REPO_ROOT / name
        if candidate.is_file():
            return candidate
    pytest.fail(f"None of the expected files exist: {', '.join(candidates)}")


# --- Menu autoload registration --------------------------------------------


def test_menu_autoload_registered() -> None:
    """project.godot must register the Menu autoload pointing at Menu.gd."""
    cp = _load_ini(PROJECT_GODOT)
    assert cp.has_section("autoload"), "project.godot has no [autoload] section"
    value = _unquote_godot_value(cp.get("autoload", "Menu"))
    # The leading '*' marks the autoload as a singleton node in Godot 4.
    assert value == "*res://Menu.gd", value


# --- Menu persistence integration ------------------------------------------


def test_menu_script_exists() -> None:
    assert MENU_SCRIPT.is_file()


def test_menu_references_audio_settings_persistence() -> None:
    """Menu coordinates volume through spec 1311's AudioSettingsPersistence."""
    src = _read(MENU_SCRIPT)
    assert "AudioSettingsPersistence" in src


def test_menu_defines_get_and_set_volume() -> None:
    src = _read(MENU_SCRIPT)
    assert "func get_volume" in src
    assert "func set_volume" in src


def test_menu_set_volume_persists_to_disk() -> None:
    """set_volume must drive AudioSettingsPersistence so values survive gameplay."""
    src = _read(MENU_SCRIPT)
    # Persisting on write is what lets values restore on menu return.
    assert "save_settings_to_disk" in src or "save_settings" in src


# --- SettingsMenu slider binding / restore ---------------------------------


def test_settings_script_exists() -> None:
    _first_existing(SETTINGS_SCRIPT_CANDIDATES)


def test_settings_binds_slider_value_changed_to_set_volume() -> None:
    """Slider movement must route through Menu.set_volume for persistence."""
    src = _read(_first_existing(SETTINGS_SCRIPT_CANDIDATES))
    assert "value_changed" in src
    assert "Menu.set_volume" in src


def test_settings_initializes_sliders_from_get_volume() -> None:
    """On open, sliders must restore from the persisted Menu.get_volume values."""
    src = _read(_first_existing(SETTINGS_SCRIPT_CANDIDATES))
    assert "Menu.get_volume" in src


def test_settings_scene_wires_sliders() -> None:
    """The settings scene exposes HSlider controls the script binds against."""
    src = _read(_first_existing(SETTINGS_SCENE_CANDIDATES))
    assert 'type="HSlider"' in src


# --- Back-to-main-menu navigation ------------------------------------------


def _has_back_handler(src: str) -> bool:
    # A back handler is a function named *_on_back* that emits a back_* signal.
    has_handler = "_on_back" in src and "func " in src
    has_back_signal = "back_requested" in src or "back_pressed" in src
    return has_handler and has_back_signal


def test_settings_has_back_to_menu_handler() -> None:
    src = _read(_first_existing(SETTINGS_SCRIPT_CANDIDATES))
    assert _has_back_handler(src)


def test_load_screen_has_back_to_menu_handler() -> None:
    assert _has_back_handler(_read(LOAD_SCRIPT))


def test_credits_has_back_to_menu_handler() -> None:
    assert _has_back_handler(_read(CREDITS_SCRIPT))


def test_main_menu_instantiates_settings_and_load_scenes() -> None:
    """MainMenu hosts the settings and load screens and instantiates them."""
    src = _read(MAIN_MENU_SCRIPT)
    assert "SettingsMenu.tscn" in src or "settings_menu.tscn" in src
    assert "LoadScreen.tscn" in src or "load_screen.tscn" in src
    assert "instantiate" in src


def test_main_menu_connects_overlay_back_signal() -> None:
    """The overlay back signals must be wired so navigation returns cleanly."""
    src = _read(MAIN_MENU_SCRIPT)
    assert "back_requested" in src or "back_pressed" in src
