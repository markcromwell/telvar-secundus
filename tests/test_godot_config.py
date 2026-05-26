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


def test_autoload_includes_quest_and_dialogue_managers() -> None:
    cp = _load_ini(PROJECT_GODOT)
    assert cp.has_section("autoload")
    assert cp.has_option("autoload", "QuestManager")
    assert cp.has_option("autoload", "DialogueManager")
    qm = _unquote_godot_value(cp.get("autoload", "QuestManager"))
    dm = _unquote_godot_value(cp.get("autoload", "DialogueManager"))
    assert qm == "*res://scripts/quest_manager.gd"
    assert dm == "*res://scripts/dialogue_manager.gd"


def test_dialogue_manager_script_contract() -> None:
    path = REPO_ROOT / "scripts" / "dialogue_manager.gd"
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    for needle in (
        "func show_dialogue(",
        "func set_flag(",
        "func get_flag(",
        "var _flags: Dictionary",
    ):
        assert needle in text


def test_myramar_dialogue_json_seed() -> None:
    path = REPO_ROOT / "assets" / "dialogue" / "myramar.json"
    assert path.is_file()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    assert "quest_give" in path.read_text(encoding="utf-8")


def test_dialogue_box_scene_exists_with_named_nodes() -> None:
    path = REPO_ROOT / "scenes" / "DialogueBox.tscn"
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    assert 'name="NameLabel"' in text
    assert 'name="TextLabel"' in text
    assert 'name="ChoicesContainer"' in text
    assert 'type="VBoxContainer"' in text
    assert "res://scripts/dialogue_box.gd" in text


def test_dialogue_box_script_flag_dispatch_contract() -> None:
    path = REPO_ROOT / "scripts" / "dialogue_box.gd"
    assert path.is_file()
    src = path.read_text(encoding="utf-8")
    assert "func _process_flags(" in src
    assert "QuestManager.start_quest(" in src
    assert 'DialogueManager.set_flag("shop_open", true)' in src
    assert 'DialogueManager.set_flag("lore_unlock"' in src
    assert "QuestManager.complete_objective(" in src
