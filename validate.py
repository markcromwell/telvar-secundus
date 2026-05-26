#!/usr/bin/env python3
"""
TELVAR-RPG validation script: filesystem + static checks (no Godot binary).
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
GODOT = REPO_ROOT / "godot"
DISTRICT_BOUNDS = GODOT / "scripts" / "district_bounds.gd"
POPULATOR = GODOT / "scripts" / "overworld_tile_populator.gd"
BOOTSTRAP = GODOT / "scripts" / "overworld_bootstrap.gd"
PROJECT = GODOT / "project.godot"
OVERWORLD_SCENE = GODOT / "scenes" / "OverworldMap.tscn"

errors: list[str] = []


def _fail(msg: str) -> None:
    errors.append(msg)


def _check_files_exist() -> None:
    for path, label in (
        (DISTRICT_BOUNDS, "district_bounds.gd"),
        (POPULATOR, "overworld_tile_populator.gd"),
        (BOOTSTRAP, "overworld_bootstrap.gd"),
        (PROJECT, "project.godot"),
        (OVERWORLD_SCENE, "OverworldMap.tscn"),
    ):
        if not path.is_file():
            _fail(f"Missing required file ({label}): {path.relative_to(REPO_ROOT)}")


def _check_autoload_and_main_scene() -> None:
    if not PROJECT.is_file():
        return
    text = PROJECT.read_text(encoding="utf-8")
    if "OverworldBootstrap=" not in text:
        _fail("project.godot must autoload OverworldBootstrap for runtime district painting")
    if 'run/main_scene="res://scenes/OverworldMap.tscn"' not in text:
        _fail("project.godot must set run/main_scene to res://scenes/OverworldMap.tscn")


def _check_twelve_districts() -> None:
    if not DISTRICT_BOUNDS.is_file():
        return
    text = DISTRICT_BOUNDS.read_text(encoding="utf-8")
    ids = re.findall(r'"id"\s*:\s*"([^"]+)"', text)
    if len(ids) != 12:
        _fail(f"district_bounds.gd must define exactly 12 district ids, found {len(ids)}")
    if len(set(ids)) != 12:
        _fail("district ids must be unique")
    rects = re.findall(r'"rect"\s*:\s*Rect2i\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)', text)
    if len(rects) != 12:
        _fail(f"expected 12 Rect2i entries in DISTRICTS, found {len(rects)}")
    for x, y, w, h in rects:
        xi, yi, wi, hi = int(x), int(y), int(w), int(h)
        if xi < 0 or yi < 0 or wi < 1 or hi < 1:
            _fail(f"invalid rect dimensions Rect2i({xi}, {yi}, {wi}, {hi})")
        if xi + wi > 160 or yi + hi > 90:
            _fail(f"rect exceeds 160x90 map: Rect2i({xi}, {yi}, {wi}, {hi})")
    if "veneficturis" not in ids or "old_city" not in ids or "severen_river" not in ids:
        _fail("district_bounds.gd must include veneficturis, old_city, and severen_river")
    by_id = dict(zip(ids, rects, strict=True))
    vx, vy, vw, vh = (int(x) for x in by_id["veneficturis"])
    ox, oy, ow, oh = (int(x) for x in by_id["old_city"])
    sx, sy, sw, sh = (int(x) for x in by_id["severen_river"])
    ven_max_y = vy + vh - 1
    old_min_y = oy
    if ven_max_y >= old_min_y:
        _fail("Veneficturis must lie strictly north of Old City (max Ven Y < min Old Y)")
    if sy < 80:
        _fail("Severen River must occupy only southern rows (rect Y must be >= 80)")
    cells: set[tuple[int, int]] = set()
    for x, y, w, h in rects:
        xi, yi, wi, hi = int(x), int(y), int(w), int(h)
        for yy in range(yi, yi + hi):
            for xx in range(xi, xi + wi):
                if (xx, yy) in cells:
                    _fail(f"overlapping district cells at ({xx}, {yy})")
                cells.add((xx, yy))
    if len(cells) != 160 * 90:
        _fail(f"district rects must partition the 160x90 map; covered {len(cells)} cells")


_check_files_exist()
_check_autoload_and_main_scene()
_check_twelve_districts()

if errors:
    for e in errors:
        print("FAIL:", e)
    sys.exit(1)

print("validate.py: structural checks passed")
sys.exit(0)
