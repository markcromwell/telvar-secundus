"""HTML5 export smoke + overworld scene static checks (Godot 4.x).

Uses stdlib (os, re, shutil, subprocess, zipfile, urllib) and pytest only.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import zipfile
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
GODOT_ROOT = REPO_ROOT / "godot"
DISTRICT_BOUNDS = GODOT_ROOT / "scripts" / "district_bounds.gd"
OVERWORLD_SCENE = GODOT_ROOT / "scenes" / "OverworldMap.tscn"
BUILD_DIR = GODOT_ROOT / "build"
INDEX_HTML = BUILD_DIR / "index.html"
INDEX_WASM = BUILD_DIR / "index.wasm"

_GODOT_EXPORT_TEMPLATES_TPZ = (
    "https://github.com/godotengine/godot-builds/releases/download/4.3-stable/"
    "Godot_v4.3-stable_export_templates.tpz"
)
_TEMPLATE_MEMBER = "templates/web_nothreads_release.zip"
_GODOT_TEMPLATE_VERSION = "4.3.stable"
_PYTEST_GODOT_XDG_DEFAULT = Path("/tmp/telvar_godot_pytest_xdg")


def _godot_executable() -> str:
    cand = os.environ.get("GODOT_BIN", "").strip()
    if cand and Path(cand).is_file():
        return str(Path(cand).resolve())
    w = shutil.which("godot")
    if w:
        return w
    pytest.fail(
        "Godot binary not found: install `godot` on PATH or set GODOT_BIN "
        "to the Godot 4.3 editor binary (linux.x86_64)."
    )


def _pytest_godot_xdg_root() -> Path:
    raw = os.environ.get("PYTEST_GODOT_XDG", "").strip()
    return Path(raw) if raw else _PYTEST_GODOT_XDG_DEFAULT


def _godot_subprocess_env() -> dict[str, str]:
    xdg_root = _pytest_godot_xdg_root()
    cfg = xdg_root / "config"
    data = xdg_root / "data"
    cfg.mkdir(parents=True, exist_ok=True)
    data.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["XDG_CONFIG_HOME"] = str(cfg)
    env["XDG_DATA_HOME"] = str(data)
    return env


def _web_release_template_zip(xdg_data: Path) -> Path:
    return xdg_data / "godot" / "export_templates" / _GODOT_TEMPLATE_VERSION / "web_nothreads_release.zip"


def _ensure_web_export_release_template() -> None:
    env = _godot_subprocess_env()
    xdg_data = Path(env["XDG_DATA_HOME"])
    dest = _web_release_template_zip(xdg_data)
    if dest.is_file():
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    tpz_cache = Path(os.environ.get("GODOT_EXPORT_TEMPLATES_TPZ", "/tmp/Godot_export_templates.tpz"))
    if not tpz_cache.is_file():
        try:
            tpz_cache.parent.mkdir(parents=True, exist_ok=True)
            with urlopen(_GODOT_EXPORT_TEMPLATES_TPZ, timeout=600) as resp, tpz_cache.open("wb") as out:
                shutil.copyfileobj(resp, out)
        except URLError as exc:
            pytest.fail(f"could not download export templates tpz ({exc}); place file at {tpz_cache}")
    with zipfile.ZipFile(tpz_cache) as zf:
        if _TEMPLATE_MEMBER not in zf.namelist():
            pytest.fail(f"{tpz_cache} missing {_TEMPLATE_MEMBER}")
        with zf.open(_TEMPLATE_MEMBER) as src, dest.open("wb") as out:
            shutil.copyfileobj(src, out)


def _run_godot_html5_export() -> subprocess.CompletedProcess[str]:
    _ensure_web_export_release_template()
    return subprocess.run(
        [
            _godot_executable(),
            "--headless",
            "--export-release",
            "Web",
            "build/index.html",
            "--path",
            "godot",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
        env=_godot_subprocess_env(),
    )


def _district_display_names() -> list[str]:
    text = DISTRICT_BOUNDS.read_text(encoding="utf-8")
    names = re.findall(r'"display_name"\s*:\s*"([^"]+)"', text)
    if len(names) != 12:
        pytest.fail(f"expected 12 display_name entries in district_bounds.gd, got {len(names)}")
    if len(set(names)) != 12:
        pytest.fail("district display_name values must be unique")
    return names


def _res_paths_from_tscn(scene_text: str) -> list[str]:
    return re.findall(r'\[ext_resource[^\]]*path="(res://[^"]+)"', scene_text)


def _overworld_static_bundle_text() -> str:
    """Text reachable from OverworldMap.tscn via direct ext_resource paths (no Godot runtime)."""
    scene_text = OVERWORLD_SCENE.read_text(encoding="utf-8")
    chunks = [scene_text]
    for res_path in _res_paths_from_tscn(scene_text):
        rel = res_path.removeprefix("res://")
        path = GODOT_ROOT / rel
        if not path.is_file():
            pytest.fail(f"OverworldMap ext_resource missing on disk: {path}")
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".ogg", ".wav"}:
            continue
        chunks.append(path.read_text(encoding="utf-8"))
    return "\n".join(chunks)


def _vector2i_coords_in_tscn(scene_text: str) -> list[tuple[int, int]]:
    pairs: list[tuple[int, int]] = []
    for x_s, y_s in re.findall(r"Vector2i\(\s*(\d+)\s*,\s*(\d+)\s*\)", scene_text):
        pairs.append((int(x_s), int(y_s)))
    return pairs


def test_00_godot_binary_available() -> None:
    _godot_executable()


def test_01_html5_export_release_succeeds() -> None:
    if BUILD_DIR.is_dir():
        shutil.rmtree(BUILD_DIR)
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    proc = _run_godot_html5_export()
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_02_html5_build_artifacts_nonempty() -> None:
    index_js = BUILD_DIR / "index.js"
    assert INDEX_HTML.is_file(), f"missing {INDEX_HTML}"
    assert INDEX_WASM.is_file(), f"missing {INDEX_WASM}"
    assert index_js.is_file(), f"missing {index_js}"
    # Default Godot 4.3 shell HTML is small (~5 KiB); runtime glue lives in index.js.
    assert INDEX_HTML.stat().st_size >= 4 * 1024, "index.html unexpectedly tiny"
    assert INDEX_HTML.stat().st_size + index_js.stat().st_size >= 10 * 1024
    assert INDEX_WASM.stat().st_size >= 1024 * 1024


def test_03_district_display_names_reachable_from_overworld_scene_text() -> None:
    """District catalog lives in district_bounds.gd; markers are duplicated in the TileSet linked from the scene."""
    names = _district_display_names()
    bundle = _overworld_static_bundle_text()
    missing = [n for n in names if n not in bundle]
    assert not missing, f"district display names missing from overworld static bundle: {missing}"


def test_04_overworld_tscn_tile_coords_within_map() -> None:
    text = OVERWORLD_SCENE.read_text(encoding="utf-8")
    for x, y in _vector2i_coords_in_tscn(text):
        assert x <= 159, f"tile/map Vector2i x={x} exceeds 159"
        assert y <= 89, f"tile/map Vector2i y={y} exceeds 89"


def test_05_html5_export_is_deterministic_in_file_sizes() -> None:
    def _export() -> tuple[int, int]:
        proc = _run_godot_html5_export()
        assert proc.returncode == 0, proc.stdout + proc.stderr
        return INDEX_HTML.stat().st_size, INDEX_WASM.stat().st_size

    first = _export()
    second = _export()
    assert first == second, f"export sizes drifted: {first} vs {second}"
