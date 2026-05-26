#!/usr/bin/env python3
"""
TELVAR-RPG validation script (bootstrap + structural checks).

Godot scenes are validated as text (no Godot binary).
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent

# Bootstrap mode: check only what is strictly required at this stage
errors: list[str] = []

SEALED_WING_TSCN = REPO_ROOT / "scenes" / "doors" / "SealedWingDoor.tscn"
SEALED_WING_GD = REPO_ROOT / "scenes" / "doors" / "SealedWingDoor.gd"
MAIN_HALL_TSCN = REPO_ROOT / "scenes" / "main_hall" / "MainHall.tscn"


def _check_sealed_wing_door() -> None:
    if not SEALED_WING_TSCN.is_file():
        errors.append(f"Missing Sealed Wing door scene: {SEALED_WING_TSCN}")
        return
    if not SEALED_WING_GD.is_file():
        errors.append(f"Missing Sealed Wing door script: {SEALED_WING_GD}")
        return
    tscn = SEALED_WING_TSCN.read_text(encoding="utf-8")
    for needle in ('type="StaticBody2D"', 'type="Area2D"', "res://scenes/doors/SealedWingDoor.gd"):
        if needle not in tscn:
            errors.append(f"SealedWingDoor.tscn missing required fragment: {needle!r}")
    for path in ("res://assets/ui/lock_icon.png", "res://assets/sfx/door_locked.wav"):
        if path not in tscn:
            errors.append(f"SealedWingDoor.tscn missing asset ref: {path!r}")
    gd = SEALED_WING_GD.read_text(encoding="utf-8")
    if "Authorised personnel only" not in gd:
        errors.append("SealedWingDoor.gd must contain the Authorised personnel only string")
    if "MSG_ABYSS_WHISPER" not in gd or "act" not in gd:
        errors.append("SealedWingDoor.gd must define abyss whisper and act handling")
    lock_png = REPO_ROOT / "assets" / "ui" / "lock_icon.png"
    sfx_wav = REPO_ROOT / "assets" / "sfx" / "door_locked.wav"
    if not lock_png.is_file():
        errors.append(f"Missing lock icon texture: {lock_png}")
    if not sfx_wav.is_file():
        errors.append(f"Missing locked door SFX: {sfx_wav}")
    if not MAIN_HALL_TSCN.is_file():
        errors.append(f"Missing Main Hall scene: {MAIN_HALL_TSCN}")
    else:
        hall = MAIN_HALL_TSCN.read_text(encoding="utf-8")
        if "SealedWingDoor.tscn" not in hall:
            errors.append("MainHall.tscn should instance SealedWingDoor.tscn")


_check_sealed_wing_door()

# Only enforce critical structural checks here
# (Full validation in spec 1246)

if errors:
    for e in errors:
        print("FAIL:", e)
    sys.exit(1)

print("Bootstrap checks passed (spec 1246 will add full validation)")
sys.exit(0)
