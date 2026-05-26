#!/usr/bin/env python3
"""Structural validation for Telvar Secundus Godot project (text checks only)."""

from __future__ import annotations

import configparser
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
PROJECT_GODOT = REPO_ROOT / "project.godot"
DIALOGUE_MANAGER = REPO_ROOT / "scripts" / "DialogueManager.gd"
FADE_TRANSITION = REPO_ROOT / "scripts" / "FadeTransition.gd"
DIALOGUE_BOX = REPO_ROOT / "scenes" / "DialogueBox.tscn"


def _wrap_godot_root_section(text: str) -> str:
    stripped = text.lstrip("\ufeff")
    if not stripped.lstrip().startswith("["):
        return "[__godot_root__]\n" + text
    return text


def _load_project_godot() -> configparser.ConfigParser:
    text = PROJECT_GODOT.read_text(encoding="utf-8")
    text = _wrap_godot_root_section(text)
    cp = configparser.ConfigParser(interpolation=None)
    cp.read_string(text)
    return cp


def main() -> int:
    errors: list[str] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    if not DIALOGUE_MANAGER.is_file():
        check(False, f"Missing {DIALOGUE_MANAGER.relative_to(REPO_ROOT)}")
    else:
        dm = DIALOGUE_MANAGER.read_text(encoding="utf-8")
        for needle in ("func show_dialogue(", "func set_flag(", "func get_flag("):
            check(needle in dm, f"DialogueManager.gd must contain {needle!r}")

    if not FADE_TRANSITION.is_file():
        check(False, f"Missing {FADE_TRANSITION.relative_to(REPO_ROOT)}")
    else:
        ft = FADE_TRANSITION.read_text(encoding="utf-8")
        check("func fade_to(" in ft, "FadeTransition.gd must contain 'func fade_to('")
        check("0.3" in ft, "FadeTransition.gd must reference 0.3 fade duration")

    if not DIALOGUE_BOX.is_file():
        check(False, f"Missing {DIALOGUE_BOX.relative_to(REPO_ROOT)}")
    else:
        box = DIALOGUE_BOX.read_text(encoding="utf-8")
        for name in ("NameLabel", "TextLabel", "ChoicesContainer"):
            check(name in box, f"DialogueBox.tscn must contain node name {name!r}")

    if not PROJECT_GODOT.is_file():
        check(False, "Missing project.godot")
    else:
        cp = _load_project_godot()
        check(cp.has_section("autoload"), "project.godot must have [autoload] section")
        if cp.has_section("autoload"):
            autoload_blob = "\n".join(
                f"{k}={cp.get('autoload', k)}"
                for k in cp.options("autoload")
            )
            check("DialogueManager" in autoload_blob, "project.godot [autoload] must register DialogueManager")
            check("FadeTransition" in autoload_blob, "project.godot [autoload] must register FadeTransition")

    cathedral_rel = "scenes/CathedralOfAten.tscn"
    cathedral_path = os.path.join(REPO_ROOT, cathedral_rel)
    check(
        (not os.path.isfile(cathedral_path)) or os.path.getsize(cathedral_path) > 0,
        f"{cathedral_rel} must be non-empty when present",
    )
    if os.path.isfile(cathedral_path):
        cathedral_text = Path(cathedral_path).read_text(encoding="utf-8")
        check("Priest1" in cathedral_text, f"{cathedral_rel} must contain node name Priest1")
        check("Priest2" in cathedral_text, f"{cathedral_rel} must contain node name Priest2")
        check("ExitDoor" in cathedral_text, f"{cathedral_rel} must contain node name ExitDoor")
        check("lpc_terrain.png" in cathedral_text, f"{cathedral_rel} must reference lpc_terrain.png")
        check("NPC.gd" in cathedral_text, f"{cathedral_rel} must reference NPC.gd")

        bundle = (
            "scripts/DialogueManager.gd",
            "scripts/FadeTransition.gd",
            "scripts/NPC.gd",
            "assets/tilesets/lpc_terrain.png",
            "assets/portraits/priest_1.png",
            "assets/portraits/priest_2.png",
            "assets/audio/sfx/footstep_stone.wav",
        )
        for rel in bundle:
            p = os.path.join(REPO_ROOT, rel)
            check(os.path.isfile(p), f"Cathedral scene present but missing {rel}")

    audio_manager = os.path.join(REPO_ROOT, "scripts", "AudioManager.gd")
    if os.path.isfile(audio_manager):
        am_text = Path(audio_manager).read_text(encoding="utf-8")
        check("footstep_stone" in am_text, "AudioManager.gd must reference footstep_stone")
        check("func play_footstep_stone()" in am_text, "AudioManager.gd must define func play_footstep_stone()")

    for priest_key in ("priest_1", "priest_2"):
        dialogue_json = os.path.join(REPO_ROOT, "assets", "dialogue", f"{priest_key}.json")
        if os.path.isfile(dialogue_json):
            raw = Path(dialogue_json).read_text(encoding="utf-8")
            try:
                data = json.loads(raw)
            except json.JSONDecodeError as exc:
                check(False, f"{dialogue_json}: invalid JSON ({exc})")
                continue
            check(isinstance(data, list), f"{dialogue_json} must be a JSON array")
            check(len(data) >= 2, f"{dialogue_json} must contain at least 2 dialogue nodes")

    # ── Report ──
    if errors:
        for e in errors:
            print("FAIL:", e)
        return 1

    print("validate.py: all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
