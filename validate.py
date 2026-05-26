#!/usr/bin/env python3
"""Structural validation for Telvar Secundus Godot project (text checks only)."""

from __future__ import annotations

import configparser
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

    if not DIALOGUE_MANAGER.is_file():
        errors.append(f"Missing {DIALOGUE_MANAGER.relative_to(REPO_ROOT)}")
    else:
        dm = DIALOGUE_MANAGER.read_text(encoding="utf-8")
        for needle in ("func show_dialogue(", "func set_flag(", "func get_flag("):
            if needle not in dm:
                errors.append(f"DialogueManager.gd must contain {needle!r}")

    if not FADE_TRANSITION.is_file():
        errors.append(f"Missing {FADE_TRANSITION.relative_to(REPO_ROOT)}")
    else:
        ft = FADE_TRANSITION.read_text(encoding="utf-8")
        if "func fade_to(" not in ft:
            errors.append("FadeTransition.gd must contain 'func fade_to('")
        if "0.3" not in ft:
            errors.append("FadeTransition.gd must reference 0.3 fade duration")

    if not DIALOGUE_BOX.is_file():
        errors.append(f"Missing {DIALOGUE_BOX.relative_to(REPO_ROOT)}")
    else:
        box = DIALOGUE_BOX.read_text(encoding="utf-8")
        for name in ("NameLabel", "TextLabel", "ChoicesContainer"):
            if name not in box:
                errors.append(f"DialogueBox.tscn must contain node name {name!r}")

    if not PROJECT_GODOT.is_file():
        errors.append("Missing project.godot")
    else:
        cp = _load_project_godot()
        if not cp.has_section("autoload"):
            errors.append("project.godot must have [autoload] section")
        else:
            autoload_blob = "\n".join(
                f"{k}={cp.get('autoload', k)}"
                for k in cp.options("autoload")
            )
            if "DialogueManager" not in autoload_blob:
                errors.append("project.godot [autoload] must register DialogueManager")
            if "FadeTransition" not in autoload_blob:
                errors.append("project.godot [autoload] must register FadeTransition")

    if errors:
        for e in errors:
            print("FAIL:", e)
        return 1

    print("validate.py: all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
