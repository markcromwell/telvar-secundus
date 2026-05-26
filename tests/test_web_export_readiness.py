"""HTML5 export readiness: resource closure and optional Godot CLI export."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from tests.test_godot_config import (
    EXPORT_PRESETS,
    MAIN_HALL_SCENE,
    MAIN_HALL_TILESET,
    REPO_ROOT,
    _load_ini,
    _unquote_godot_value,
)

_RES_PATH = re.compile(r'path="(res://[^"]+)"')


def _collect_res_paths(path: Path) -> set[Path]:
    text = path.read_text(encoding="utf-8")
    out: set[Path] = set()
    for m in _RES_PATH.finditer(text):
        rel = m.group(1).removeprefix("res://")
        out.add(REPO_ROOT / rel.replace("/", os.sep))
    return out


def test_main_hall_scene_resource_closure_exists_on_disk() -> None:
    missing: list[str] = []
    seen: set[Path] = set()
    queue = [_collect_res_paths(MAIN_HALL_SCENE)]
    while queue:
        batch = queue.pop()
        for p in batch:
            if p in seen:
                continue
            seen.add(p)
            if not p.is_file():
                missing.append(str(p.relative_to(REPO_ROOT)))
                continue
            if p.suffix.lower() in {".tscn", ".tres", ".gdshader", ".gdshaderinc"}:
                queue.append(_collect_res_paths(p))
    assert not missing, f"missing resources: {missing}"


def test_export_preset_web_name_matches_scene_bundle() -> None:
    cp = _load_ini(EXPORT_PRESETS)
    name = _unquote_godot_value(cp.get("preset.0", "name"))
    assert name == "Web"
    filt = _unquote_godot_value(cp.get("preset.0", "export_filter"))
    assert filt == "all_resources"


def test_export_preset_includes_main_hall_tileset_path() -> None:
    """``export_filter=all_resources`` should pack the hall tileset; assert it is present."""
    assert MAIN_HALL_TILESET.is_file()


def _godot_executable() -> str | None:
    env = os.environ.get("GODOT_BIN", "").strip()
    if env and Path(env).is_file():
        return env
    return shutil.which("godot") or shutil.which("godot4")


@pytest.mark.skipif(_godot_executable() is None, reason="Godot binary not available (set GODOT_BIN or install godot)")
def test_html5_export_release_produces_index_html() -> None:
    godot = _godot_executable()
    assert godot is not None
    with tempfile.TemporaryDirectory() as tmp:
        out_html = Path(tmp) / "index.html"
        cmd = [
            godot,
            "--path",
            str(REPO_ROOT),
            "--headless",
            "--export-release",
            "Web",
            str(out_html),
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600, check=False)
        assert proc.returncode == 0, f"godot export failed:\n{proc.stdout}\n{proc.stderr}"
        assert out_html.is_file(), "export did not write index.html"
        # Minimal sanity: Godot HTML5 emits a canvas host page
        html = out_html.read_text(encoding="utf-8", errors="replace")
        assert "canvas" in html.lower()
