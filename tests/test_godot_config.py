"""Filesystem validation for Godot 4.x project.godot and export_presets.cfg.

Uses configparser only — no Godot binary. Leading key=value lines before the
first INI section (e.g. config_version) are wrapped in a synthetic section so
ConfigParser can read Godot's project format.
"""

from __future__ import annotations

import configparser
import importlib.util
import json
import subprocess
import sys
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


def _load_validate_module():
    path = REPO_ROOT / "validate.py"
    spec = importlib.util.spec_from_file_location("telvar_validate", path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_validate_py_exits_zero_on_repo() -> None:
    proc = subprocess.run(
        [sys.executable, str(REPO_ROOT / "validate.py")],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, (proc.stdout, proc.stderr)


def test_validate_orsson_emporium_structure() -> None:
    mod = _load_validate_module()
    errors = mod.validate(REPO_ROOT)
    assert errors == [], errors


def test_validate_fails_when_scene_missing(tmp_path: Path) -> None:
    mod = _load_validate_module()
    (tmp_path / "assets" / "dialogue").mkdir(parents=True)
    (tmp_path / "assets" / "dialogue" / "sabatha.json").write_text(
        json.dumps([{"id": "a"}, {"id": "b"}]), encoding="utf-8"
    )
    (tmp_path / "assets" / "dialogue" / "orsson.json").write_text(
        json.dumps([{"id": "a"}, {"id": "b"}]), encoding="utf-8"
    )
    errors = mod.validate(tmp_path)
    assert errors, "expected validation errors when interior scene is absent"
    assert any("orsson_emporium.tscn" in e and "absent" in e for e in errors)


def test_validate_fails_when_dialogue_has_fewer_than_two_nodes(tmp_path: Path) -> None:
    mod = _load_validate_module()
    scene = REPO_ROOT / "scenes" / "interiors" / "orsson_emporium.tscn"
    assert scene.is_file()
    (tmp_path / "scenes" / "interiors").mkdir(parents=True)
    (tmp_path / "scenes" / "interiors" / "orsson_emporium.tscn").write_text(scene.read_text(encoding="utf-8"), encoding="utf-8")
    (tmp_path / "assets" / "dialogue").mkdir(parents=True)
    (tmp_path / "assets" / "dialogue" / "sabatha.json").write_text(json.dumps([{"id": "only"}]), encoding="utf-8")
    (tmp_path / "assets" / "dialogue" / "orsson.json").write_text(
        json.dumps([{"id": "a"}, {"id": "b"}]), encoding="utf-8"
    )
    errors = mod.validate(tmp_path)
    assert any("sabatha.json" in e and "at least two dialogue" in e for e in errors)


def test_validate_fails_when_exit_door_marker_absent(tmp_path: Path) -> None:
    mod = _load_validate_module()
    scene_text = (REPO_ROOT / "scenes" / "interiors" / "orsson_emporium.tscn").read_text(encoding="utf-8")
    broken = scene_text.replace("ExitDoor", "FrontExit")
    (tmp_path / "scenes" / "interiors").mkdir(parents=True)
    (tmp_path / "scenes" / "interiors" / "orsson_emporium.tscn").write_text(broken, encoding="utf-8")
    (tmp_path / "assets" / "dialogue").mkdir(parents=True)
    for name in ("sabatha.json", "orsson.json"):
        src = REPO_ROOT / "assets" / "dialogue" / name
        (tmp_path / "assets" / "dialogue" / name).write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    errors = mod.validate(tmp_path)
    assert any("ExitDoor" in e for e in errors)
