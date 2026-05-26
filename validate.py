#!/usr/bin/env python3
"""
TELVAR-RPG validation script (bootstrap + phase checks).
Full validation is implemented in spec #1246.
"""

from __future__ import annotations

import configparser
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
PROJECT_GODOT = REPO_ROOT / "project.godot"
DIALOGUE_MANAGER_GD = REPO_ROOT / "scripts" / "DialogueManager.gd"
DIALOGUE_BOX_GD = REPO_ROOT / "scripts" / "DialogueBox.gd"
DIALOGUE_BOX_TSCN = REPO_ROOT / "scenes" / "DialogueBox.tscn"

DIALOGUE_NPC_FILES = (
    "sabatha",
    "orrson",
    "market_trader",
    "city_guard",
    "beggar_child",
)

NPC_SCENES: dict[str, str] = {
    "sabatha": "Sabatha.tscn",
    "orrson": "Orrson.tscn",
    "market_trader": "MarketTrader.tscn",
    "city_guard": "CityGuard.tscn",
    "beggar_child": "BeggarChild.tscn",
}

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


def _function_body_lines(lines: list[str], func_line_prefix: str) -> list[str] | None:
    """Return body lines for a top-level GDScript function (until the next top-level `func `)."""
    for idx, line in enumerate(lines):
        if line.startswith(func_line_prefix):
            body: list[str] = []
            for j in range(idx + 1, len(lines)):
                nxt = lines[j]
                if nxt.startswith("func "):
                    break
                body.append(nxt)
            return body
    return None


def _check_gdscript_gates(label: str, text: str) -> None:
    """Lightweight text checks (no Godot binary). Catches common gate failures."""
    # Anonymous func assignments break simple text-based GDScript gates.
    if re.search(r"=\s*func\s*\(", text):
        errors.append(f"{label}: anonymous func assignments are not allowed")

    for lineno, line in enumerate(text.splitlines(), 1):
        if line.strip() == "=":
            errors.append(f"{label}:{lineno}: dangling '=' assignment")

    # Heuristic: flag obvious Python/C-style mistakes that indicate corrupt GDScript.
    for lineno, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("def "):
            errors.append(f"{label}:{lineno}: Python 'def' is not valid GDScript")


def _check_dialogue_manager_gd() -> None:
    """DialogueManager API, DialogueBox wiring (AC4), and GDScript gates."""
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

    _check_gdscript_gates("DialogueManager.gd", text)

    lines = text.splitlines()
    body = _function_body_lines(lines, "func show_dialogue(")
    if body is None:
        errors.append("DialogueManager.gd: could not parse show_dialogue() body")
        return

    body_text = "\n".join(body)
    needle = "res://scenes/DialogueBox.tscn"
    if needle not in body_text:
        errors.append(
            "DialogueManager.gd: show_dialogue() must reference "
            f"{needle!r} (instantiate the DialogueBox scene)"
        )


def _check_dialogue_box_gd() -> None:
    """AC2–AC3: DialogueBox script attached via scene ext_resource; populate() API."""
    if not DIALOGUE_BOX_GD.is_file():
        errors.append("Missing scripts/DialogueBox.gd")
        return

    text = DIALOGUE_BOX_GD.read_text(encoding="utf-8")

    if "extends Control" not in text:
        errors.append("DialogueBox.gd: expected 'extends Control'")

    if not re.search(r"func\s+populate\s*\(\s*speaker\s*:", text):
        errors.append(
            "DialogueBox.gd: expected func populate(speaker: ... with typed speaker parameter"
        )

    if "NameLabel" not in text or "TextLabel" not in text or "ChoicesContainer" not in text:
        errors.append(
            "DialogueBox.gd: expected @onready paths containing NameLabel, TextLabel, "
            "and ChoicesContainer"
        )

    _check_gdscript_gates("DialogueBox.gd", text)


def _check_dialogue_box_tscn() -> None:
    """AC1: scene hierarchy Control > VBoxContainer > NameLabel, TextLabel, ChoicesContainer."""
    if not DIALOGUE_BOX_TSCN.is_file():
        errors.append("Missing scenes/DialogueBox.tscn")
        return

    text = DIALOGUE_BOX_TSCN.read_text(encoding="utf-8")

    if 'path="res://scripts/DialogueBox.gd"' not in text and "path='res://scripts/DialogueBox.gd'" not in text:
        errors.append(
            "DialogueBox.tscn: missing ext_resource Script path res://scripts/DialogueBox.gd"
        )

    if "script = ExtResource(" not in text:
        errors.append("DialogueBox.tscn: root node must assign script = ExtResource(...)")

    for name in ("NameLabel", "TextLabel", "ChoicesContainer"):
        if f'name="{name}"' not in text:
            errors.append(f'DialogueBox.tscn: missing node name="{name}"')

    if 'name="VBoxContainer"' not in text:
        errors.append('DialogueBox.tscn: missing VBoxContainer')


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


def _check_dialogue_json_files() -> None:
    """NPC dialogue JSON: exists, valid JSON array; Sabatha length + flag marker."""
    for npc in DIALOGUE_NPC_FILES:
        rel = f"assets/dialogue/{npc}.json"
        path = REPO_ROOT / rel
        if not path.is_file():
            errors.append(f"Missing {rel}")
            continue

        raw = path.read_text(encoding="utf-8")
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            errors.append(f"{rel}: invalid JSON ({exc})")
            continue

        if not isinstance(data, list):
            errors.append(f"{rel}: expected top-level JSON array")
            continue

        if npc == "sabatha":
            if len(data) < 4:
                errors.append(
                    f"{rel}: expected at least 4 array elements (start + 3 branches), "
                    f"got {len(data)}"
                )
            if '"flag"' not in raw:
                errors.append(f'{rel}: expected raw file text to contain the JSON key snippet \'"flag"\'')


def _check_npc_portraits() -> None:
    for npc in DIALOGUE_NPC_FILES:
        rel = f"assets/portraits/{npc}.png"
        path = REPO_ROOT / rel
        if not path.is_file():
            errors.append(f"Missing {rel}")


def _check_npc_scenes() -> None:
    for npc, fname in NPC_SCENES.items():
        rel = f"scenes/{fname}"
        path = REPO_ROOT / rel
        if not path.is_file():
            errors.append(f"Missing {rel} (NPC {npc})")


_check_dialogue_box_tscn()
_check_dialogue_box_gd()
_check_dialogue_manager_gd()
_check_autoload()
_check_dialogue_json_files()
_check_npc_portraits()
_check_npc_scenes()

if errors:
    for e in errors:
        print("FAIL:", e)
    sys.exit(1)

print(
    "Validation passed (DialogueBox + DialogueManager + autoload + "
    "dialogue JSON + portraits + NPC scenes)"
)
sys.exit(0)
