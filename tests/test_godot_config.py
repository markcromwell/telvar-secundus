"""Filesystem validation for Godot 4.x project.godot and export_presets.cfg.

Uses configparser only — no Godot binary. Leading key=value lines before the
first INI section (e.g. config_version) are wrapped in a synthetic section so
ConfigParser can read Godot's project format.
"""

from __future__ import annotations

import configparser
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
PROJECT_GODOT = REPO_ROOT / "project.godot"
EXPORT_PRESETS = REPO_ROOT / "export_presets.cfg"

# Phase 2521: canonical Sabatha opening line (must match assets/dialogue/sabatha.json id "start").
SABATHA_CANONICAL_OPENING = (
    "So you've come to Secundus—twelve districts, one old city, "
    "and a thousand stories drowning in the gutters."
)

DIALOGUE_NPC_FILES = (
    "sabatha",
    "orrson",
    "market_trader",
    "city_guard",
    "beggar_child",
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


def _load_dialogue(npc: str) -> list:
    path = REPO_ROOT / "assets" / "dialogue" / f"{npc}.json"
    assert path.is_file(), f"Missing dialogue file: {path}"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, list), f"{path} must be a JSON array"
    return data


def _png_pixel_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", f"{path} is not a PNG"
    assert data[12:16] == b"IHDR", f"{path} missing IHDR"
    w = int.from_bytes(data[16:20], "big")
    h = int.from_bytes(data[20:24], "big")
    return w, h


def test_dialogue_json_files_parse() -> None:
    for npc in DIALOGUE_NPC_FILES:
        _load_dialogue(npc)


def test_sabatha_start_line_and_branches() -> None:
    nodes = _load_dialogue("sabatha")
    by_id = {str(n["id"]): n for n in nodes if isinstance(n, dict) and "id" in n}
    assert "start" in by_id
    start = by_id["start"]
    assert start.get("text") == SABATHA_CANONICAL_OPENING
    choices = start.get("choices")
    assert isinstance(choices, list) and len(choices) >= 3
    next_ids: list[str] = []
    for ch in choices:
        assert isinstance(ch, dict)
        assert "next" in ch
        next_ids.append(str(ch["next"]))
    assert len(set(next_ids)) >= 3
    for nid in set(next_ids):
        assert nid in by_id, f"choice next {nid!r} missing as node id"


def test_sabatha_flag_node() -> None:
    nodes = _load_dialogue("sabatha")
    found = False
    for n in nodes:
        if not isinstance(n, dict) or "flag" not in n:
            continue
        flag = n["flag"]
        if isinstance(flag, dict) and flag.get("key") is not None and "value" in flag:
            found = True
            break
    assert found, "sabatha.json must contain a node with flag.key and flag.value"


def test_non_sabatha_dialogue_minimum_nodes() -> None:
    for npc in ("orrson", "market_trader", "city_guard", "beggar_child"):
        nodes = _load_dialogue(npc)
        assert len(nodes) >= 3


def test_npc_portraits_exist_48x48() -> None:
    for npc in DIALOGUE_NPC_FILES:
        path = REPO_ROOT / "assets" / "portraits" / f"{npc}.png"
        assert path.is_file(), f"Missing portrait: {path}"
        assert path.stat().st_size < 5 * 1024 * 1024
        w, h = _png_pixel_size(path)
        assert (w, h) == (48, 48), f"{path} expected 48x48, got {w}x{h}"
