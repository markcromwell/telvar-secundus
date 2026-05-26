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
OVERWORLD_SCENE = REPO_ROOT / "scenes" / "Overworld.tscn"
LPC_TERRAIN_TILESET = REPO_ROOT / "assets" / "tilesets" / "lpc_terrain.tres"
DISTRICT_ZONE_SCRIPT = REPO_ROOT / "scripts" / "DistrictZone.gd"
BUILDING_ENTRANCE_SCRIPT = REPO_ROOT / "scripts" / "BuildingEntrance.gd"


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


def test_overworld_scene_exists() -> None:
    assert OVERWORLD_SCENE.is_file()


def test_overworld_references_lpc_tileset() -> None:
    text = OVERWORLD_SCENE.read_text(encoding="utf-8")
    assert 'path="res://assets/tilesets/lpc_terrain.tres"' in text
    assert LPC_TERRAIN_TILESET.is_file()


def test_overworld_tilemap_two_layers_and_quadrant() -> None:
    text = OVERWORLD_SCENE.read_text(encoding="utf-8")
    assert '[node name="TileMap" type="TileMap" parent="."]' in text
    assert "layer_0/" in text and "layer_1/" in text
    assert "layer_0/tile_data = PackedInt32Array()" in text
    assert "layer_1/tile_data = PackedInt32Array()" in text
    # Godot 4.2+ renamed cell_quadrant_size -> rendering_quadrant_size; accept either.
    assert ("rendering_quadrant_size = 16" in text) or ("cell_quadrant_size = 16" in text)


def test_overworld_camera_smoothing_spawn_containers() -> None:
    text = OVERWORLD_SCENE.read_text(encoding="utf-8")
    assert '[node name="Camera2D" type="Camera2D" parent="TileMap"]' in text
    assert "position_smoothing_enabled = true" in text
    assert '[node name="SpawnPoint" type="Marker2D" parent="TileMap"]' in text
    assert '[node name="DistrictZones" type="Node2D" parent="."]' in text
    assert '[node name="BuildingEntrances" type="Node2D" parent="."]' in text


def test_district_zone_script_contract() -> None:
    assert DISTRICT_ZONE_SCRIPT.is_file()
    text = DISTRICT_ZONE_SCRIPT.read_text(encoding="utf-8")
    assert "@export var district_name" in text
    assert "@export var hud_label" in text
    assert "extends Area2D" in text
    assert "body_entered.connect" in text
    assert "Timer" in text


def test_building_entrance_script_contract() -> None:
    assert BUILDING_ENTRANCE_SCRIPT.is_file()
    text = BUILDING_ENTRANCE_SCRIPT.read_text(encoding="utf-8")
    assert "@export var building_label" in text
    assert "extends Area2D" in text
    assert "body_entered.connect" in text
    assert "body_exited.connect" in text
    assert "Press E to enter" in text
