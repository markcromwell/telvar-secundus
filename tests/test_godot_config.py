"""Filesystem validation for Godot 4.x project.godot and export_presets.cfg.

Uses configparser and json only — no Godot binary. Leading key=value lines before the
first INI section (e.g. config_version) are wrapped in a synthetic section so
ConfigParser can read Godot's project format.
"""

from __future__ import annotations

import configparser
import json
import struct
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
PROJECT_GODOT = REPO_ROOT / "project.godot"
EXPORT_PRESETS = REPO_ROOT / "export_presets.cfg"
APPRENTICE_ROOM_SCENE = REPO_ROOT / "apprentice_room.tscn"
APPRENTICE_ROOM_SCRIPT = REPO_ROOT / "apprentice_room_floor.gd"
APPRENTICE_NPC_SCRIPT = REPO_ROOT / "apprentice_npc.gd"
APPRENTICE_ROOM_FRIENDS_JSON = REPO_ROOT / "data" / "dialogue" / "apprentice_room_friends.json"
GAME_DATA_RESOURCES_JSON = REPO_ROOT / "data" / "game_data_resources.json"
NPC_DARAN_SCENE = REPO_ROOT / "npcs" / "npc_daran.tscn"
NPC_YESSA_SCENE = REPO_ROOT / "npcs" / "npc_yessa.tscn"
NPC_CORVIN_SCENE = REPO_ROOT / "npcs" / "npc_corvin.tscn"
LPC_DARK_STONE_PNG = REPO_ROOT / "assets" / "tilesets" / "lpc_dark_stone.png"
LPC_DARK_STONE_TILESET = REPO_ROOT / "assets" / "tilesets" / "lpc_dark_stone_tileset.tres"
LPC_APPRENTICE_SHEETS = [
    REPO_ROOT / "assets" / "sprites" / "lpc_apprentice" / "daran_sheet.png",
    REPO_ROOT / "assets" / "sprites" / "lpc_apprentice" / "yessa_sheet.png",
    REPO_ROOT / "assets" / "sprites" / "lpc_apprentice" / "corvin_sheet.png",
]


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


def test_apprentice_room_floor_loads_game_data_resources() -> None:
    script = APPRENTICE_ROOM_SCRIPT.read_text(encoding="utf-8")
    assert "game_data_resources.json" in script
    assert "veneficturis_apprentice_room" in script
    assert "_apply_npc_spawns_from_game_data" in script


def _res_to_repo_path(res_path: str) -> Path:
    assert res_path.startswith("res://")
    return REPO_ROOT / res_path.removeprefix("res://")


def test_game_data_resources_registers_apprentice_room_scene() -> None:
    assert GAME_DATA_RESOURCES_JSON.is_file()
    gdr = json.loads(GAME_DATA_RESOURCES_JSON.read_text(encoding="utf-8"))
    locs = gdr["locations"]
    loc = locs["veneficturis_apprentice_room"]
    scene_res = loc["scene_path"]
    assert scene_res == "res://apprentice_room.tscn"
    scene_path = _res_to_repo_path(scene_res)
    assert scene_path.is_file()


def test_game_data_npc_spawns_align_with_dialogue_location() -> None:
    """Registry location id must match dialogue resource so runtime wiring stays consistent."""
    gdr = json.loads(GAME_DATA_RESOURCES_JSON.read_text(encoding="utf-8"))
    dialogue = json.loads(APPRENTICE_ROOM_FRIENDS_JSON.read_text(encoding="utf-8"))
    assert "veneficturis_apprentice_room" in gdr["locations"]
    assert dialogue["location_id"] == "veneficturis_apprentice_room"


def test_game_data_npc_spawns_three_friends_within_room() -> None:
    gdr = json.loads(GAME_DATA_RESOURCES_JSON.read_text(encoding="utf-8"))
    spawns = gdr["locations"]["veneficturis_apprentice_room"]["npc_spawns"]
    for key in ("daran", "yessa", "corvin"):
        assert key in spawns
        tile = spawns[key]["tile"]
        assert len(tile) == 2
        tx, ty = int(tile[0]), int(tile[1])
        assert 0 <= tx < 8
        assert 0 <= ty < 6


def test_dialogue_npcs_ready_for_runtime_init() -> None:
    """Mirrors apprentice_npc.gd expectations: entry_node exists inside nodes."""
    data = json.loads(APPRENTICE_ROOM_FRIENDS_JSON.read_text(encoding="utf-8"))
    for key in ("daran", "yessa", "corvin"):
        block = data["npcs"][key]
        entry = block["entry_node"]
        nodes = block["nodes"]
        assert entry in nodes
        assert block["display_name"]
        assert isinstance(nodes[entry].get("lines"), list)


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


def test_apprentice_npc_script_and_dialogue_path() -> None:
    assert APPRENTICE_NPC_SCRIPT.is_file()
    text = APPRENTICE_NPC_SCRIPT.read_text(encoding="utf-8")
    assert "apprentice_room_friends.json" in text
    assert "walk_down" in text and "walk_up" in text


def test_apprentice_room_friends_json_has_three_npcs() -> None:
    data = json.loads(APPRENTICE_ROOM_FRIENDS_JSON.read_text(encoding="utf-8"))
    npcs = data["npcs"]
    for key in ("daran", "yessa", "corvin"):
        assert key in npcs
        assert "entry_node" in npcs[key]
        assert "nodes" in npcs[key]


def test_npc_scenes_use_apprentice_npc_script() -> None:
    for path in (NPC_DARAN_SCENE, NPC_YESSA_SCENE, NPC_CORVIN_SCENE):
        assert path.is_file()
        tscn = path.read_text(encoding="utf-8")
        assert "apprentice_npc.gd" in tscn
        assert "apprentice_room_friends.json" in tscn


def test_apprentice_room_instances_friend_npcs() -> None:
    text = APPRENTICE_ROOM_SCENE.read_text(encoding="utf-8")
    assert "npc_daran.tscn" in text
    assert "npc_yessa.tscn" in text
    assert "npc_corvin.tscn" in text


def test_lpc_apprentice_sprite_sheets_are_128_square() -> None:
    """32px × 4 frames square sheet; four walk rows for down/left/right/up."""
    for png_path in LPC_APPRENTICE_SHEETS:
        data = png_path.read_bytes()
        assert data[:8] == b"\x89PNG\r\n\x1a\n"
        assert data[12:16] == b"IHDR"
        w, h = struct.unpack(">II", data[16:24])
        assert w == 128
        assert h == 128
