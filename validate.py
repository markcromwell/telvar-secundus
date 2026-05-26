#!/usr/bin/env python3
"""
TELVAR-RPG validation script (structural checks, no Godot runtime).
Uses filesystem + text parsing only.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
errors: list[str] = []


def check(cond: bool, msg: str) -> None:
    if not cond:
        errors.append(msg)


def check_file(rel_path: str) -> None:
    path = REPO_ROOT / rel_path
    check(path.is_file(), f"missing file: {rel_path}")


def check_contains(rel_path: str, substring: str, description: str) -> None:
    path = REPO_ROOT / rel_path
    if not path.is_file():
        errors.append(f"missing file: {rel_path} ({description})")
        return
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"cannot read {rel_path}: {exc}")
        return
    check(substring in text, f"{rel_path} missing {description}: expected substring {substring!r}")


# --- Phase 2496: minimap + location marker artifacts ---
check_file("scripts/LocationMarker.gd")
check_file("scenes/Minimap.tscn")
check_file("scripts/Minimap.gd")

check_contains("scripts/GameManager.gd", "KEY_LOCATIONS", "GameManager.KEY_LOCATIONS constant")

_minimap_path = REPO_ROOT / "scripts" / "Minimap.gd"
if _minimap_path.is_file():
    _minimap_text = _minimap_path.read_text(encoding="utf-8")
    for _token in ("Emporium", "Temple", "Cathedral", "Keep", "Veneficturis"):
        check(_token in _minimap_text, f"scripts/Minimap.gd missing location token {_token!r}")

check_contains("scenes/Minimap.tscn", "SubViewport", "SubViewport node")

check_contains("scripts/LevelBase.gd", "_add_location_markers", "LevelBase._add_location_markers")

if errors:
    for e in errors:
        print("FAIL:", e)
    sys.exit(1)

print("Validation passed.")
sys.exit(0)
