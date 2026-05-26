#!/usr/bin/env python3
"""TELVAR-RPG structural validation (no Godot binary)."""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent

errors: list[str] = []


def _require_file(rel: str) -> None:
    p = REPO_ROOT / rel
    if not p.is_file():
        errors.append(f"Missing required file: {rel}")


def _require_text(path: Path, needle: str, what: str) -> None:
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    if needle not in text:
        errors.append(f"{path.relative_to(REPO_ROOT)}: expected {what}")


_require_file("HUD.gd")
_require_file("HUD.tscn")

_hud_tscn = REPO_ROOT / "HUD.tscn"
_hud_gd = REPO_ROOT / "HUD.gd"
_require_text(_hud_tscn, '[node name="DistrictLabel"', "DistrictLabel node")
_require_text(_hud_tscn, '[node name="DistrictHoldTimer"', "DistrictHoldTimer node")
_require_text(_hud_gd, "func show_district_name", "show_district_name function")

if errors:
    for e in errors:
        print("FAIL:", e)
    sys.exit(1)

print("Structural checks passed.")
sys.exit(0)
