#!/usr/bin/env python3
"""
Structural validation for the Godot project (text parsing only, no Godot binary).

Exits 0 on success, 1 on failure. Each failure line is prefixed with "FAIL:".
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent

REQUIRED_DIRS = (
    "scenes",
    "scripts",
    "assets/tilesets",
)

REQUIRED_FILES = (
    "project.godot",
    "scenes/Overworld.tscn",
    "scripts/OverworldMap.gd",
    "assets/tilesets/lpc_terrain.tres",
)

# Godot 4.x / GDScript 2 patterns that should not appear in project scripts.
BAD_GDSCRIPT_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\byield\s*\("), "Godot 3-style yield() is invalid in GDScript 2"),
    (re.compile(r"\bKinematicBody2D\b"), "KinematicBody2D was removed in Godot 4"),
    (re.compile(r"^\s*tool\s*$", re.MULTILINE), "Use @tool instead of bare tool in Godot 4"),
)


def _fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)


def _check_paths_exist(errors: list[str]) -> None:
    for rel in REQUIRED_DIRS:
        p = REPO_ROOT / rel
        if not p.is_dir():
            errors.append(f"missing_required_directory: {rel}")

    for rel in REQUIRED_FILES:
        p = REPO_ROOT / rel
        if not p.is_file():
            errors.append(f"missing_required_file: {rel}")


def _check_overworld_tscn(errors: list[str]) -> None:
    path = REPO_ROOT / "scenes" / "Overworld.tscn"
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")

    if 'type="TileMap"' not in text:
        errors.append("overworld_missing_tilemap_node: scenes/Overworld.tscn has no TileMap node type")

    if "lpc_terrain.tres" not in text:
        errors.append(
            "overworld_missing_lpc_tileset_extresource: scenes/Overworld.tscn "
            "must reference assets/tilesets/lpc_terrain.tres"
        )

    if not re.search(r"y_sort_enabled\s*=\s*false", text):
        errors.append(
            "overworld_missing_y_sort_disabled: scenes/Overworld.tscn must set y_sort_enabled = false "
            "(z-fighting guard)"
        )


def _check_overworld_map_gd(errors: list[str]) -> None:
    path = REPO_ROOT / "scripts" / "OverworldMap.gd"
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    if "set_cell(" not in text:
        errors.append("overworld_map_missing_set_cell: scripts/OverworldMap.gd must call TileMap.set_cell(")


def _scan_gdscripts(errors: list[str]) -> None:
    for gd_path in sorted(REPO_ROOT.rglob("*.gd")):
        # Skip hidden directories
        if any(part.startswith(".") for part in gd_path.relative_to(REPO_ROOT).parts):
            continue
        try:
            content = gd_path.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"gdscript_unreadable: {gd_path.relative_to(REPO_ROOT)} ({exc})")
            continue
        rel = str(gd_path.relative_to(REPO_ROOT))
        for pattern, explanation in BAD_GDSCRIPT_PATTERNS:
            if pattern.search(content):
                errors.append(f"gdscript_forbidden_pattern: {rel} — {explanation}")


def main() -> int:
    errors: list[str] = []
    _check_paths_exist(errors)
    _check_overworld_tscn(errors)
    _check_overworld_map_gd(errors)
    _scan_gdscripts(errors)

    if errors:
        for e in errors:
            _fail(e)
        return 1

    print("validate.py: all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
