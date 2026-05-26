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
ENTRANCE_TOOLTIP_SCENE = REPO_ROOT / "scenes/ui/EntranceTooltip.tscn"
ENTRANCE_TOOLTIP_SCRIPT = REPO_ROOT / "scripts/ui/entrance_tooltip.gd"
BUILDING_ENTRANCE_SCENE = REPO_ROOT / "scenes/world/BuildingEntrance.tscn"
BUILDING_ENTRANCE_SCRIPT = REPO_ROOT / "scripts/world/building_entrance.gd"


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


def test_entrance_tooltip_scene_exists() -> None:
    assert ENTRANCE_TOOLTIP_SCENE.is_file()


def test_entrance_tooltip_script_exists() -> None:
    assert ENTRANCE_TOOLTIP_SCRIPT.is_file()


def test_entrance_tooltip_label_text() -> None:
    body = ENTRANCE_TOOLTIP_SCENE.read_text(encoding="utf-8")
    assert 'text = "Press E to enter"' in body


def test_entrance_tooltip_scene_node_tree() -> None:
    """CanvasLayer root with PanelContainer child and Label grandchild (Phase 2482)."""
    body = ENTRANCE_TOOLTIP_SCENE.read_text(encoding="utf-8")
    assert 'type="CanvasLayer"' in body
    assert '[node name="PanelContainer" type="PanelContainer" parent="."]' in body
    assert '[node name="Label" type="Label" parent="PanelContainer"]' in body


def test_entrance_tooltip_script_html5_safe() -> None:
    src = ENTRANCE_TOOLTIP_SCRIPT.read_text(encoding="utf-8")
    assert "OS.get_name" not in src
    assert "OS.get_model_name" not in src


def test_entrance_tooltip_show_hide_toggle_panel() -> None:
    src = ENTRANCE_TOOLTIP_SCRIPT.read_text(encoding="utf-8")
    assert "$PanelContainer" in src
    assert "func show()" in src
    assert "func hide()" in src
    assert "_panel.visible = true" in src
    assert "_panel.visible = false" in src


def test_entrance_tooltip_scene_ext_resource_script() -> None:
    body = ENTRANCE_TOOLTIP_SCENE.read_text(encoding="utf-8")
    assert 'path="res://scripts/ui/entrance_tooltip.gd"' in body


def test_building_entrance_scene_exists() -> None:
    assert BUILDING_ENTRANCE_SCENE.is_file()


def test_building_entrance_script_exists() -> None:
    assert BUILDING_ENTRANCE_SCRIPT.is_file()


def test_building_entrance_scene_structure() -> None:
    """Area2D root, collision, 1-tile RectangleShape2D, instanced EntranceTooltip (Phase 2483)."""
    body = BUILDING_ENTRANCE_SCENE.read_text(encoding="utf-8")
    assert 'type="Area2D"' in body
    assert 'path="res://scripts/world/building_entrance.gd"' in body
    assert '[node name="CollisionShape2D" type="CollisionShape2D" parent="."]' in body
    assert "RectangleShape2D" in body
    assert 'size = Vector2(32, 32)' in body
    assert 'path="res://scenes/ui/EntranceTooltip.tscn"' in body
    assert "instance=ExtResource(" in body


def test_building_entrance_script_contract() -> None:
    src = BUILDING_ENTRANCE_SCRIPT.read_text(encoding="utf-8")
    assert "@export var building_name: String" in src
    assert "@export var entrance_id: String" in src
    assert "var player_in_range: bool = false" in src
    assert "signal entered(" in src
    assert "body_entered.connect" in src
    assert "body_exited.connect" in src
    assert "_tooltip.show()" in src
    assert "_tooltip.hide()" in src
    assert "func _unhandled_input" in src
    assert 'event.is_action_pressed("ui_accept")' in src
    assert "entered.emit(" in src
    assert "func _on_enter()" in src
    assert "print(building_name)" in src
    assert "get_viewport().set_input_as_handled()" in src
    assert "is_in_group(\"player\")" in src
    assert "OS.get_name" not in src
