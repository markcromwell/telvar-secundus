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


def _wrap_godot_root_section(text: str) -> str:
    """Godot may place key=value pairs before the first [section]; ConfigParser requires a section."""
    stripped = text.lstrip("\ufeff")
    if not stripped.lstrip().startswith("["):
        return "[__godot_root__]\n" + text
    return text


def _strip_godot_input_section(text: str) -> str:
    """Remove [input] map blocks; nested []/braces break ConfigParser."""
    lines = text.splitlines(True)
    out: list[str] = []
    i = 0
    while i < len(lines):
        if lines[i].strip() == "[input]":
            i += 1
            while i < len(lines):
                s = lines[i].strip()
                if s.startswith("[") and s != "[input]":
                    break
                i += 1
            continue
        out.append(lines[i])
        i += 1
    return "".join(out)


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
        text = _strip_godot_input_section(text)
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


def test_dialogue_manager_autoload_line() -> None:
    text = PROJECT_GODOT.read_text(encoding="utf-8")
    assert 'DialogueManager="*res://scripts/DialogueManager.gd"' in text


def test_interact_input_physical_keycode_e() -> None:
    """E key: physical_keycode 69 (read raw file; [input] values are not INI-friendly)."""
    text = PROJECT_GODOT.read_text(encoding="utf-8")
    assert "[input]" in text
    assert "interact=" in text
    assert 'physical_keycode":69' in text or "physical_keycode=69" in text


def test_dialogue_manager_script_exists() -> None:
    path = REPO_ROOT / "scripts" / "DialogueManager.gd"
    assert path.is_file()


def test_dialogue_box_scene_exists() -> None:
    path = REPO_ROOT / "scenes" / "DialogueBox.tscn"
    assert path.is_file()
    body = path.read_text(encoding="utf-8")
    assert 'name="NameLabel"' in body
    assert 'name="TextLabel"' in body
    assert 'name="ChoicesContainer"' in body
    assert 'name="PortraitTexture"' in body


def test_npc_script_markers() -> None:
    path = REPO_ROOT / "scripts" / "NPC.gd"
    assert path.is_file()
    body = path.read_text(encoding="utf-8")
    assert "@export var npc_id" in body
    assert 'Input.is_action_just_pressed("interact")' in body
    assert "func _load_dialogue(" in body


def test_npc_scene_structure() -> None:
    path = REPO_ROOT / "scenes" / "NPC.tscn"
    assert path.is_file()
    body = path.read_text(encoding="utf-8")
    assert 'type="Area2D"' in body
    assert "res://scripts/NPC.gd" in body
    assert "CircleShape2D" in body
    assert 'type="Sprite2D"' in body


def test_player_script_movement_lock_guard() -> None:
    path = REPO_ROOT / "scripts" / "Player.gd"
    assert path.is_file()
    body = path.read_text(encoding="utf-8")
    assert "var can_move" in body
    assert "if not can_move:" in body
