#!/usr/bin/env python3
"""
Pure-Python structural validation for the Telvar Godot 4.x project.

No Godot runtime: checks file presence, JSON shape/ids, .tscn text markers,
and required GDScript API strings. Exits 0 on full pass, 1 with printed FAIL lines.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any


def _fail(errors: list[str], message: str) -> None:
    errors.append(message)


def _require_file(errors: list[str], root: Path, rel: str) -> Path | None:
    path = root / rel
    if not path.is_file():
        _fail(errors, f"Missing required file: {rel}")
        return None
    return path


def _read_text(errors: list[str], path: Path, label: str) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        _fail(errors, f"{label}: cannot read {path}: {exc}")
        return None


def _load_json(errors: list[str], path: Path, label: str) -> Any | None:
    raw = _read_text(errors, path, label)
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        _fail(errors, f"{label}: invalid JSON ({exc})")
        return None


def _check_sabatha_dialogue(errors: list[str], data: Any, path: Path) -> None:
    label = f"sabatha.json ({path})"
    if not isinstance(data, list) or not data:
        _fail(errors, f"{label}: must be a non-empty JSON array")
        return
    blob = json.dumps(data, ensure_ascii=False)
    if "Sabatha" not in blob:
        _fail(errors, f"{label}: must contain speaker/name 'Sabatha'")
    if "We always knew you had the gift" not in blob:
        _fail(errors, f"{label}: must contain gift line substring")
    for i, entry in enumerate(data):
        if not isinstance(entry, dict):
            _fail(errors, f"{label}: entry {i} must be an object")
            continue
        for key in ("id", "text", "speaker", "next"):
            if key not in entry:
                _fail(errors, f"{label}: entry {i} missing key {key!r}")
        if "next" in entry and entry["next"] is not None and not isinstance(entry["next"], str):
            _fail(errors, f"{label}: entry {i} 'next' must be string or null")


def _check_quest_json(errors: list[str], data: Any, path: Path, expected_id: str) -> None:
    label = f"{path.name} ({path})"
    if not isinstance(data, dict):
        _fail(errors, f"{label}: root must be a JSON object")
        return
    if data.get("id") != expected_id:
        _fail(errors, f"{label}: top-level 'id' must be {expected_id!r} exactly")
    objectives = data.get("objectives")
    if not isinstance(objectives, list) or not objectives:
        _fail(errors, f"{label}: 'objectives' must be a non-empty array")
        return
    for i, obj in enumerate(objectives):
        if not isinstance(obj, dict):
            _fail(errors, f"{label}: objectives[{i}] must be an object")
            continue
        if "id" not in obj or "desc" not in obj:
            _fail(errors, f"{label}: objectives[{i}] must include 'id' and 'desc'")


def _check_tscn_substrings(errors: list[str], rel: str, text: str, needles: tuple[str, ...]) -> None:
    for needle in needles:
        if needle not in text:
            _fail(errors, f"{rel}: expected .tscn to contain substring {needle!r}")


def _check_gdscript_substrings(errors: list[str], rel: str, text: str, needles: tuple[tuple[str, str], ...]) -> None:
    for needle, msg in needles:
        if needle not in text:
            _fail(errors, f"{rel}: {msg}")


def main() -> int:
    errors: list[str] = []
    root = Path(__file__).resolve().parent

    required_rel_paths = (
        "project.godot",
        "export_presets.cfg",
        "assets/dialogue/sabatha.json",
        "assets/quests/merchants_delivery.json",
        "assets/quests/the_assessment.json",
        "scenes/emporium/act1_conclusion_trigger.tscn",
        "scenes/ui/dialogue_box.tscn",
        "scenes/ui/veneficturis_letter.tscn",
        "scripts/act1_conclusion.gd",
        "scripts/dialogue_manager.gd",
        "scripts/quest_manager.gd",
    )

    paths: dict[str, Path] = {}
    for rel in required_rel_paths:
        p = _require_file(errors, root, rel)
        if p is not None:
            paths[rel] = p

    # JSON assets (three)
    sabatha_path = paths.get("assets/dialogue/sabatha.json")
    if sabatha_path is not None:
        sabatha_data = _load_json(errors, sabatha_path, "sabatha.json")
        if sabatha_data is not None:
            _check_sabatha_dialogue(errors, sabatha_data, sabatha_path)

    md_path = paths.get("assets/quests/merchants_delivery.json")
    if md_path is not None:
        md_data = _load_json(errors, md_path, "merchants_delivery.json")
        if md_data is not None:
            _check_quest_json(errors, md_data, md_path, "merchants_delivery")

    ta_path = paths.get("assets/quests/the_assessment.json")
    if ta_path is not None:
        ta_data = _load_json(errors, ta_path, "the_assessment.json")
        if ta_data is not None:
            _check_quest_json(errors, ta_data, ta_path, "the_assessment")

    # project.godot autoload markers (text-level; no full INI parse needed here)
    pg = paths.get("project.godot")
    if pg is not None:
        pg_text = _read_text(errors, pg, "project.godot")
        if pg_text is not None:
            if "QuestManager=" not in pg_text or "scripts/quest_manager.gd" not in pg_text:
                _fail(errors, "project.godot: must autoload QuestManager to scripts/quest_manager.gd")
            if "DialogueManager=" not in pg_text or "scripts/dialogue_manager.gd" not in pg_text:
                _fail(errors, "project.godot: must autoload DialogueManager to scripts/dialogue_manager.gd")

    # Scenes
    trigger = paths.get("scenes/emporium/act1_conclusion_trigger.tscn")
    if trigger is not None:
        t = _read_text(errors, trigger, "act1_conclusion_trigger.tscn")
        if t is not None:
            _check_tscn_substrings(errors, "scenes/emporium/act1_conclusion_trigger.tscn", t, ("Area2D", "CollisionShape2D"))

    dialogue_box = paths.get("scenes/ui/dialogue_box.tscn")
    if dialogue_box is not None:
        t = _read_text(errors, dialogue_box, "dialogue_box.tscn")
        if t is not None:
            _check_tscn_substrings(
                errors,
                "scenes/ui/dialogue_box.tscn",
                t,
                (
                    'type="Control"',
                    'type="VBoxContainer"',
                    "NameLabel",
                    "TextLabel",
                    "ChoicesContainer",
                ),
            )

    letter = paths.get("scenes/ui/veneficturis_letter.tscn")
    if letter is not None:
        t = _read_text(errors, letter, "veneficturis_letter.tscn")
        if t is not None:
            _check_tscn_substrings(
                errors,
                "scenes/ui/veneficturis_letter.tscn",
                t,
                (
                    'type="Control"',
                    'type="Panel"',
                    'type="RichTextLabel"',
                    'type="Button"',
                    "DismissButton",
                    "StyleBoxFlat",
                ),
            )

    # GDScript API strings
    dm = paths.get("scripts/dialogue_manager.gd")
    if dm is not None:
        g = _read_text(errors, dm, "dialogue_manager.gd")
        if g is not None:
            _check_gdscript_substrings(
                errors,
                "scripts/dialogue_manager.gd",
                g,
                (
                    ("func show_dialogue", "must define show_dialogue"),
                    ("func set_flag", "must define set_flag"),
                    ("func get_flag", "must define get_flag"),
                ),
            )

    qm = paths.get("scripts/quest_manager.gd")
    if qm is not None:
        g = _read_text(errors, qm, "quest_manager.gd")
        if g is not None:
            _check_gdscript_substrings(
                errors,
                "scripts/quest_manager.gd",
                g,
                (
                    ("signal quest_updated", "must declare quest_updated signal"),
                    ("signal objective_completed", "must declare objective_completed signal"),
                    ("var quests:", "must declare quests dictionary"),
                    ("func start_quest", "must define start_quest"),
                    ("func complete_objective", "must define complete_objective"),
                    ("func is_complete", "must define is_complete"),
                ),
            )

    act1 = paths.get("scripts/act1_conclusion.gd")
    if act1 is not None:
        g = _read_text(errors, act1, "act1_conclusion.gd")
        if g is not None:
            if "act1_complete" not in g:
                _fail(errors, "scripts/act1_conclusion.gd: must reference act1_complete flag")
            _check_gdscript_substrings(
                errors,
                "scripts/act1_conclusion.gd",
                g,
                (
                    ("DialogueManager.show_dialogue", "must call DialogueManager.show_dialogue"),
                    ("QuestManager.complete_objective", "must call QuestManager.complete_objective"),
                    ("'merchants_delivery'", "must reference merchants_delivery quest id"),
                    ("QuestManager.start_quest", "must call QuestManager.start_quest"),
                    ("'the_assessment'", "must reference the_assessment quest id"),
                    ("DialogueManager.set_flag", "must call DialogueManager.set_flag"),
                    ("body_entered.connect", "must connect body_entered in _ready"),
                    ("_triggered", "must use a one-shot guard"),
                    ("preload(\"res://scenes/ui/veneficturis_letter.tscn\")", "must preload veneficturis letter scene"),
                ),
            )

    if errors:
        for e in errors:
            print("FAIL:", e, file=sys.stderr)
        return 1

    print("validate.py: all structural checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
