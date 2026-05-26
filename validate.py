#!/usr/bin/env python3
"""
TELVAR-RPG validation script (bootstrap + structural checks).

Godot scenes are validated as text (no Godot binary).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent

# Bootstrap mode: check only what is strictly required at this stage
errors: list[str] = []

SEALED_WING_TSCN = REPO_ROOT / "scenes" / "doors" / "SealedWingDoor.tscn"
SEALED_WING_GD = REPO_ROOT / "scenes" / "doors" / "SealedWingDoor.gd"
MAIN_HALL_TSCN = REPO_ROOT / "scenes" / "main_hall" / "MainHall.tscn"


def _has_node(
    text: str,
    *,
    name: str | None = None,
    type_: str | None = None,
    parent: str | None = None,
) -> bool:
    parts = [r"\[node"]
    if name is not None:
        parts.append(rf'(?=[^\]]*\bname="{re.escape(name)}")')
    if type_ is not None:
        parts.append(rf'(?=[^\]]*\btype="{re.escape(type_)}")')
    if parent is not None:
        parts.append(rf'(?=[^\]]*\bparent="{re.escape(parent)}")')
    parts.append(r"[^\]]*\]")
    return re.search("".join(parts), text) is not None


def _external_resource_id(text: str, *, type_: str, path: str) -> str | None:
    pattern = (
        rf'\[ext_resource[^\]]*\btype="{re.escape(type_)}"'
        rf'[^\]]*\bpath="{re.escape(path)}"[^\]]*\bid="([^"]+)"[^\]]*\]'
    )
    match = re.search(pattern, text)
    return match.group(1) if match else None


def _check_sealed_wing_door() -> None:
    if not SEALED_WING_TSCN.is_file():
        errors.append(f"Missing Sealed Wing door scene: {SEALED_WING_TSCN}")
        return
    if not SEALED_WING_GD.is_file():
        errors.append(f"Missing Sealed Wing door script: {SEALED_WING_GD}")
        return
    tscn = SEALED_WING_TSCN.read_text(encoding="utf-8")
    script_id = _external_resource_id(
        tscn, type_="Script", path="res://scenes/doors/SealedWingDoor.gd"
    )
    lock_id = _external_resource_id(
        tscn, type_="Texture2D", path="res://assets/ui/lock_icon.png"
    )
    sfx_id = _external_resource_id(
        tscn, type_="AudioStream", path="res://assets/sfx/door_locked.wav"
    )
    if script_id is None:
        errors.append("SealedWingDoor.tscn missing script ext_resource")
    if lock_id is None:
        errors.append("SealedWingDoor.tscn missing lock icon Texture2D ext_resource")
    if sfx_id is None:
        errors.append("SealedWingDoor.tscn missing locked SFX AudioStream ext_resource")
    if not _has_node(tscn, name="SealedWingDoor", type_="Node2D"):
        errors.append('SealedWingDoor.tscn root must be a Node2D named "SealedWingDoor"')
    elif script_id is not None and f'script = ExtResource("{script_id}")' not in tscn:
        errors.append("SealedWingDoor root must attach SealedWingDoor.gd")
    for name, type_, parent in (
        ("StaticBody2D", "StaticBody2D", "."),
        ("CollisionShape2D", "CollisionShape2D", "StaticBody2D"),
        ("Area2D", "Area2D", "."),
        ("CollisionShape2D", "CollisionShape2D", "Area2D"),
        ("LockSprite", "Sprite2D", "."),
        ("AudioStreamPlayer2D", "AudioStreamPlayer2D", "."),
        ("MessagePanel", "PanelContainer", "Overlay"),
        ("MessageLabel", "Label", "Overlay/MessagePanel/MarginContainer"),
        ("HideTimer", "Timer", "Overlay"),
    ):
        if not _has_node(tscn, name=name, type_=type_, parent=parent):
            errors.append(f"SealedWingDoor.tscn missing {type_} node {name!r} under {parent!r}")
    if lock_id is not None and f'texture = ExtResource("{lock_id}")' not in tscn:
        errors.append("SealedWingDoor.tscn LockSprite must use lock_icon.png")
    if sfx_id is not None and f'stream = ExtResource("{sfx_id}")' not in tscn:
        errors.append("SealedWingDoor.tscn AudioStreamPlayer2D must use door_locked.wav")
    gd = SEALED_WING_GD.read_text(encoding="utf-8")
    if "Authorised personnel only" not in gd:
        errors.append("SealedWingDoor.gd must contain the Authorised personnel only string")
    if "MSG_ABYSS_WHISPER" not in gd:
        errors.append("SealedWingDoor.gd must define the abyss whisper message")
    if "act >= 1" not in gd or "act <= 3" not in gd:
        errors.append("SealedWingDoor.gd must gate abyss whisper to Acts 1-3")
    for needle in ("_area.input_event.connect", "_audio.play()", "_message_panel.visible = true"):
        if needle not in gd:
            errors.append(f"SealedWingDoor.gd missing locked interaction behavior: {needle!r}")
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
        door_id = _external_resource_id(
            hall, type_="PackedScene", path="res://scenes/doors/SealedWingDoor.tscn"
        )
        if door_id is None:
            errors.append("MainHall.tscn should declare SealedWingDoor.tscn as a PackedScene")
        else:
            instance_pattern = (
                rf'\[node[^\]]*\bname="SealedWingDoor[^"]*"'
                rf'[^\]]*\bparent="\."[^\]]*\binstance=ExtResource\("{re.escape(door_id)}"\)'
                r"[^\]]*\]"
            )
            instances = re.findall(instance_pattern, hall)
            if len(instances) < 2:
                errors.append("MainHall.tscn should instance SealedWingDoor.tscn doors")


_check_sealed_wing_door()

# Only enforce critical structural checks here
# (Full validation in spec 1246)

if errors:
    for e in errors:
        print("FAIL:", e)
    sys.exit(1)

print("Bootstrap checks passed (spec 1246 will add full validation)")
sys.exit(0)
