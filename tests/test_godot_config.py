"""Filesystem validation for Godot 4.x project.godot and export_presets.cfg.

Uses configparser only — no Godot binary. Leading key=value lines before the
first INI section (e.g. config_version) are wrapped in a synthetic section so
ConfigParser can read Godot's project format.
"""

from __future__ import annotations

import configparser
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
PROJECT_GODOT = REPO_ROOT / "project.godot"
EXPORT_PRESETS = REPO_ROOT / "export_presets.cfg"
ITEM_SCRIPT = REPO_ROOT / "scripts/resources/item.gd"
INVENTORY_SCRIPT = REPO_ROOT / "scripts/inventory/inventory.gd"
WIZARD_BAND_RED = REPO_ROOT / "resources/items/wizard_band_red.tres"
PLAYER_SCENE = REPO_ROOT / "scenes/player/Player.tscn"
PLAYER_SCRIPT = REPO_ROOT / "scripts/player/Player.gd"
WRIST_BAND_TEX = REPO_ROOT / "assets/sprites/wizard_band_red_wrist.png"


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


def test_project_godot_exists() -> None:
    assert PROJECT_GODOT.is_file()


def test_export_presets_exists() -> None:
    assert EXPORT_PRESETS.is_file()


def test_viewport_dimensions_1280x720() -> None:
    cp = _load_ini(PROJECT_GODOT)
    w = cp.get("display", "window/size/viewport_width")
    h = cp.get("display", "window/size/viewport_height")
    assert w == "1280"
    assert h == "720"


def test_renderer_mobile() -> None:
    cp = _load_ini(PROJECT_GODOT)
    method = _unquote_godot_value(cp.get("rendering", "renderer/rendering_method"))
    assert method == "mobile"


def test_pixel_snap_vertices_and_transforms_true_strings() -> None:
    cp = _load_ini(PROJECT_GODOT)
    v = cp.get("rendering", "2d/snap/snap_2d_vertices_to_pixel")
    t = cp.get("rendering", "2d/snap/snap_2d_transforms_to_pixel")
    assert v == "true"
    assert t == "true"


def test_content_scale_factor_2x() -> None:
    cp = _load_ini(PROJECT_GODOT)
    factor = cp.get("display", "window/size/content_scale_factor")
    assert factor == "2"


def test_nearest_neighbor_canvas_texture_filter() -> None:
    """Godot 4: default_texture_filter=0 is nearest (pixel art)."""
    cp = _load_ini(PROJECT_GODOT)
    filt = cp.get("rendering", "textures/canvas_textures/default_texture_filter")
    assert filt == "0"


def test_msaa_disabled_for_crisp_pixels() -> None:
    cp = _load_ini(PROJECT_GODOT)
    assert cp.get("rendering", "anti_aliasing/quality/msaa_2d") == "0"
    assert cp.get("rendering", "anti_aliasing/quality/screen_space_aa") == "0"


def test_export_preset_web_platform() -> None:
    cp = _load_ini(EXPORT_PRESETS)
    assert cp.has_section("preset.0")
    platform = _unquote_godot_value(cp.get("preset.0", "platform"))
    assert platform == "Web"


def test_export_preset_web_runnable() -> None:
    cp = _load_ini(EXPORT_PRESETS)
    runnable = cp.get("preset.0", "runnable")
    assert runnable == "true"


def test_item_resource_script_exists() -> None:
    assert ITEM_SCRIPT.is_file()
    text = ITEM_SCRIPT.read_text(encoding="utf-8")
    assert "class_name Item" in text
    assert "@export var tags" in text


def test_inventory_script_exists() -> None:
    assert INVENTORY_SCRIPT.is_file()
    text = INVENTORY_SCRIPT.read_text(encoding="utf-8")
    assert "class_name Inventory" in text
    assert "func add_item" in text


def test_wizard_band_red_tres_exists_and_magical() -> None:
    assert WIZARD_BAND_RED.is_file()
    text = WIZARD_BAND_RED.read_text(encoding="utf-8")
    assert "wizard_band_red" in text
    assert "magical" in text
    assert "res://scripts/resources/item.gd" in text


def test_player_scene_and_wrist_band_sprite() -> None:
    assert PLAYER_SCENE.is_file()
    assert WRIST_BAND_TEX.is_file()
    scene = PLAYER_SCENE.read_text(encoding="utf-8")
    assert 'name="WristBand"' in scene
    assert "type=\"Sprite2D\"" in scene
    assert "wizard_band_red_wrist.png" in scene


def test_player_script_exposes_wrist_band_visibility() -> None:
    assert PLAYER_SCRIPT.is_file()
    text = PLAYER_SCRIPT.read_text(encoding="utf-8")
    assert "func set_wrist_band_visible" in text
    assert "extends CharacterBody2D" in text
