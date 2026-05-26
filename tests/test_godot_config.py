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
MAIN_HALL_SCENE = REPO_ROOT / "scenes" / "veneficturis_main_hall.tscn"
MAIN_HALL_SCRIPT = REPO_ROOT / "scripts" / "veneficturis_main_hall.gd"
DARK_STONE_ATLAS = REPO_ROOT / "assets" / "tiles" / "dark_stone_lpc.png"
MAIN_HALL_TILESET = REPO_ROOT / "tilesets" / "dark_stone_lpc.tres"
PLAYER_VENEFICTURIS_SCRIPT = REPO_ROOT / "scripts" / "player_veneficturis.gd"


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


def test_main_scene_is_veneficturis_main_hall() -> None:
    cp = _load_ini(PROJECT_GODOT)
    main_scene = _unquote_godot_value(cp.get("application", "run/main_scene"))
    assert main_scene == "res://scenes/veneficturis_main_hall.tscn"


def test_main_hall_scene_bundle_exists() -> None:
    assert MAIN_HALL_SCENE.is_file()
    assert MAIN_HALL_SCRIPT.is_file()
    assert PLAYER_VENEFICTURIS_SCRIPT.is_file()
    assert DARK_STONE_ATLAS.is_file()
    assert MAIN_HALL_TILESET.is_file()


def test_main_hall_script_declares_20x15_map() -> None:
    text = MAIN_HALL_SCRIPT.read_text(encoding="utf-8")
    assert "const MAP_SIZE := Vector2i(20, 15)" in text


def test_main_hall_scene_wires_tilemap_layers() -> None:
    text = MAIN_HALL_SCENE.read_text(encoding="utf-8")
    assert 'type="TileMap"' in text
    assert 'type="TileMapLayer"' in text
    assert 'parent="HallTileMap"' in text
    assert 'name="Floor"' in text
    assert 'name="CeilingDecor"' in text


def test_main_hall_scene_has_player_reception_and_dialogue_ui() -> None:
    text = MAIN_HALL_SCENE.read_text(encoding="utf-8")
    assert 'name="Player"' in text
    assert 'type="CharacterBody2D"' in text
    assert 'name="ReceptionNPC"' in text
    assert 'type="Area2D"' in text
    assert 'name="DialogueLabel"' in text
    assert "player_veneficturis.gd" in text


def test_main_hall_script_wires_letter_presentation() -> None:
    text = MAIN_HALL_SCRIPT.read_text(encoding="utf-8")
    assert "try_present_admission_letter" in text
    assert "$ReceptionNPC" in text
    assert "player_has_admission_letter" in text


def test_dark_stone_atlas_is_64x16_rgba_png() -> None:
    data = DARK_STONE_ATLAS.read_bytes()
    assert data.startswith(b"\x89PNG\r\n\x1a\n")
    assert data[12:16] == b"IHDR"
    width, height = struct.unpack(">II", data[16:24])
    assert width == 64
    assert height == 16
    depth = data[24]
    color_type = data[25]
    assert depth == 8
    assert color_type == 6  # RGBA
