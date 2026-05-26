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
_require_file("scenes/overworld/Overworld.tscn")

_hud_tscn = REPO_ROOT / "HUD.tscn"
_hud_gd = REPO_ROOT / "HUD.gd"
_require_text(_hud_tscn, '[node name="DistrictLabel"', "DistrictLabel node")
_require_text(_hud_tscn, '[node name="DistrictHoldTimer"', "DistrictHoldTimer node")
_require_text(_hud_gd, "func show_district_name", "show_district_name function")

_overworld_tscn = REPO_ROOT / "scenes/overworld/Overworld.tscn"
if _overworld_tscn.is_file():
    _ow = _overworld_tscn.read_text(encoding="utf-8")
    _expected_districts = (
        "Golden Bell",
        "Temple District",
        "Old City",
        "Merchant District",
        "Reagent's Hill",
        "Bazaar",
        "Harbor District",
        "Warehouse District",
        "Foreign Quarter",
        "Cemetery",
        "The Rookery",
        "The Iron Works",
    )
    for d in _expected_districts:
        needle = f'district_name = "{d}"'
        if needle not in _ow:
            errors.append(f"{_overworld_tscn.relative_to(REPO_ROOT)}: missing {needle}")
    _conn = _ow.count('signal="district_entered"')
    if _conn != 12:
        errors.append(
            f"{_overworld_tscn.relative_to(REPO_ROOT)}: expected 12 district_entered connections, found {_conn}"
        )
    _to_hud = _ow.count('to="HUD" method="show_district_name"')
    if _to_hud != 12:
        errors.append(
            f"{_overworld_tscn.relative_to(REPO_ROOT)}: expected 12 HUD signal bindings, found {_to_hud}"
        )
    _layer4 = _ow.count("collision_layer = 8")
    if _layer4 != 12:
        errors.append(
            f"{_overworld_tscn.relative_to(REPO_ROOT)}: expected collision_layer=8 on 12 zones, found {_layer4}"
        )

if errors:
    for e in errors:
        print("FAIL:", e)
    sys.exit(1)

print("Structural checks passed.")
sys.exit(0)
