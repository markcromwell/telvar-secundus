"""Filesystem validation for Godot 4.x project.godot and export_presets.cfg.

Uses configparser only — no Godot binary. Leading key=value lines before the
first INI section (e.g. config_version) are wrapped in a synthetic section so
ConfigParser can read Godot's project format.
"""

from __future__ import annotations

import configparser
import struct
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
PROJECT_GODOT = REPO_ROOT / "project.godot"
EXPORT_PRESETS = REPO_ROOT / "export_presets.cfg"
APPRENTICE_ROOM_SCENE = REPO_ROOT / "apprentice_room.tscn"
APPRENTICE_ROOM_SCRIPT = REPO_ROOT / "apprentice_room_floor.gd"
LPC_DARK_STONE_PNG = REPO_ROOT / "assets" / "tilesets" / "lpc_dark_stone.png"
LPC_DARK_STONE_TILESET = REPO_ROOT / "assets" / "tilesets" / "lpc_dark_stone_tileset.tres"


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


def test_apprentice_room_scene_exists() -> None:
    assert APPRENTICE_ROOM_SCENE.is_file()


def test_apprentice_room_scene_tilemap_layer_and_tileset() -> None:
    text = APPRENTICE_ROOM_SCENE.read_text(encoding="utf-8")
    assert 'type="TileMapLayer"' in text
    assert "lpc_dark_stone_tileset.tres" in text
    assert "apprentice_room_floor.gd" in text


def test_apprentice_room_floor_dimensions_8_by_6() -> None:
    script = APPRENTICE_ROOM_SCRIPT.read_text(encoding="utf-8")
    assert "ROOM_WIDTH_TILES := 8" in script
    assert "ROOM_HEIGHT_TILES := 6" in script


def test_lpc_dark_stone_png_is_16_square() -> None:
    data = LPC_DARK_STONE_PNG.read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    ihdr_len = struct.unpack(">I", data[8:12])[0]
    assert ihdr_len == 13
    assert data[12:16] == b"IHDR"
    w, h = struct.unpack(">II", data[16:24])
    assert w == 16
    assert h == 16


def test_lpc_dark_stone_tileset_points_at_png() -> None:
    tres = LPC_DARK_STONE_TILESET.read_text(encoding="utf-8")
    assert "lpc_dark_stone.png" in tres
    assert "Vector2i(16, 16)" in tres
