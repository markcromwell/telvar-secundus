#!/usr/bin/env python3
"""
TELVAR-RPG validation script (bootstrap + phase checks).
Full validation is implemented in spec #1246.
"""

from __future__ import annotations

import configparser
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
PROJECT_GODOT = REPO_ROOT / "project.godot"
DIALOGUE_MANAGER_GD = REPO_ROOT / "scripts" / "DialogueManager.gd"

errors: list[str] = []


def _wrap_godot_root_section(text: str) -> str:
    """Godot may place key=value pairs before the first [section]; ConfigParser requires a section."""
    stripped = text.lstrip("\ufeff")
    if not stripped.lstrip().startswith("["):
        return "[__godot_root__]\n" + text
    return text


def _unquote_godot_value(raw: str) -> str:
    s = raw.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        return s[1:-1]
    return s


def _load_ini(path: Path) -> configparser.ConfigParser:
    text = path.read_text(encoding="utf-8")
    if path.name == "project.godot":
        text = _wrap_godot_root_section(text)
    cp = configparser.ConfigParser(interpolation=None)
    cp.read_string(text)
    return cp


def _check_dialogue_manager_gd() -> None:
    """Lightweight text checks (no Godot binary). Catches missing API and common gate failures."""
    if not DIALOGUE_MANAGER_GD.is_file():
        errors.append("Missing scripts/DialogueManager.gd")
        return

    text = DIALOGUE_MANAGER_GD.read_text(encoding="utf-8")

    if "extends Node" not in text:
        errors.append("DialogueManager.gd: expected 'extends Node'")

    required = (
        "func show_dialogue(",
        "func set_flag(",
        "func get_flag(",
    )
    for fragment in required:
        if fragment not in text:
            errors.append(f"DialogueManager.gd: missing {fragment!r}")

    # Anonymous func assignments break simple text-based GDScript gates.
    if re.search(r"=\s*func\s*\(", text):
        errors.append("DialogueManager.gd: anonymous func assignments are not allowed")

    for lineno, line in enumerate(text.splitlines(), 1):
        if line.strip() == "=":
            errors.append(f"DialogueManager.gd:{lineno}: dangling '=' assignment")


def _check_autoload() -> None:
    if not PROJECT_GODOT.is_file():
        errors.append("Missing project.godot")
        return

    cp = _load_ini(PROJECT_GODOT)
    if not cp.has_section("autoload"):
        errors.append("project.godot: missing [autoload] section")
        return

    if not cp.has_option("autoload", "DialogueManager"):
        errors.append("project.godot: missing DialogueManager autoload entry")
        return

    got = _unquote_godot_value(cp.get("autoload", "DialogueManager"))
    expected = "*res://scripts/DialogueManager.gd"
    if got != expected:
        errors.append(
            f"project.godot: DialogueManager autoload must be {expected!r}, got {got!r}"
        )


_check_dialogue_manager_gd()
_check_autoload()

if errors:
    for e in errors:
        print("FAIL:", e)
    sys.exit(1)

print("Validation passed (DialogueManager + autoload checks)")
sys.exit(0)
