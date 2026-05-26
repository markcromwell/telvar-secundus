#!/usr/bin/env python3
"""
Text-based structural validation for the Godot project (no Godot runtime).

Checks file presence, JSON shape, required GDScript substrings, and .tscn hints.
Exits 0 on success; on failure prints one or more "FAIL: ..." lines and exits 1.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent

QUEST_JSON = REPO_ROOT / "assets" / "quests" / "merchants_delivery.json"
LORE_JSON = REPO_ROOT / "assets" / "lore" / "lore_entries.json"
QUEST_MANAGER = REPO_ROOT / "scripts" / "quest_manager.gd"
LORE_MANAGER = REPO_ROOT / "scripts" / "lore_manager.gd"
SAVE_MANAGER = REPO_ROOT / "scripts" / "save_manager.gd"
LORE_NOTIFICATION_TSCN = REPO_ROOT / "scenes" / "ui" / "lore_notification.tscn"


def _failures() -> list[str]:
    errors: list[str] = []

    # --- File existence ---
    for path, label in (
        (QUEST_JSON, "assets/quests/merchants_delivery.json"),
        (LORE_JSON, "assets/lore/lore_entries.json"),
        (QUEST_MANAGER, "scripts/quest_manager.gd"),
        (LORE_MANAGER, "scripts/lore_manager.gd"),
        (SAVE_MANAGER, "scripts/save_manager.gd"),
        (LORE_NOTIFICATION_TSCN, "scenes/ui/lore_notification.tscn"),
    ):
        if not path.is_file():
            errors.append(f"missing required file: {label}")

    if errors:
        return errors

    # --- merchants_delivery.json ---
    try:
        quest_raw = json.loads(QUEST_JSON.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"assets/quests/merchants_delivery.json: invalid JSON ({e})"]

    if not isinstance(quest_raw, dict):
        errors.append("assets/quests/merchants_delivery.json: root must be a JSON object")
    else:
        q: dict[str, Any] = quest_raw
        for key in ("id", "title", "objectives"):
            if key not in q:
                errors.append(f"assets/quests/merchants_delivery.json: missing required key {key!r}")
        if "id" in q and not isinstance(q["id"], str):
            errors.append("assets/quests/merchants_delivery.json: 'id' must be a string")
        if "title" in q and not isinstance(q["title"], str):
            errors.append("assets/quests/merchants_delivery.json: 'title' must be a string")
        if "objectives" in q:
            objs = q["objectives"]
            if not isinstance(objs, list):
                errors.append("assets/quests/merchants_delivery.json: 'objectives' must be an array")
            else:
                for i, item in enumerate(objs):
                    if not isinstance(item, dict):
                        errors.append(
                            f"assets/quests/merchants_delivery.json: objectives[{i}] must be an object"
                        )
                        continue
                    if "id" not in item:
                        errors.append(
                            f"assets/quests/merchants_delivery.json: objectives[{i}] missing 'id'"
                        )
                    elif not isinstance(item["id"], str):
                        errors.append(
                            f"assets/quests/merchants_delivery.json: objectives[{i}].id must be a string"
                        )
                    if "desc" not in item:
                        errors.append(
                            f"assets/quests/merchants_delivery.json: objectives[{i}] missing 'desc'"
                        )
                    elif not isinstance(item["desc"], str):
                        errors.append(
                            f"assets/quests/merchants_delivery.json: objectives[{i}].desc must be a string"
                        )

    # --- lore_entries.json ---
    try:
        lore_raw = json.loads(LORE_JSON.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        errors.append(f"assets/lore/lore_entries.json: invalid JSON ({e})")
        return errors

    if not isinstance(lore_raw, list):
        errors.append("assets/lore/lore_entries.json: root must be a JSON array")
    else:
        for i, entry in enumerate(lore_raw):
            if not isinstance(entry, dict):
                errors.append(f"assets/lore/lore_entries.json: entry[{i}] must be an object")
                continue
            for key in ("id", "title", "text"):
                if key not in entry:
                    errors.append(f"assets/lore/lore_entries.json: entry[{i}] missing key {key!r}")
                elif not isinstance(entry[key], str):
                    errors.append(
                        f"assets/lore/lore_entries.json: entry[{i}].{key} must be a string"
                    )

    # --- GDScript substring checks (function names per spec) ---
    quest_src = QUEST_MANAGER.read_text(encoding="utf-8")
    if "start_quest" not in quest_src:
        errors.append("scripts/quest_manager.gd: required substring 'start_quest' not found")

    lore_src = LORE_MANAGER.read_text(encoding="utf-8")
    if "unlock" not in lore_src:
        errors.append("scripts/lore_manager.gd: required substring 'unlock' not found")

    save_src = SAVE_MANAGER.read_text(encoding="utf-8")
    if "save_game" not in save_src:
        errors.append("scripts/save_manager.gd: required substring 'save_game' not found")
    if "load_game" not in save_src:
        errors.append("scripts/save_manager.gd: required substring 'load_game' not found")

    # --- lore_notification.tscn ---
    tscn = LORE_NOTIFICATION_TSCN.read_text(encoding="utf-8")
    if "Label" not in tscn:
        errors.append("scenes/ui/lore_notification.tscn: required substring 'Label' not found")
    if "Timer" not in tscn:
        errors.append("scenes/ui/lore_notification.tscn: required substring 'Timer' not found")

    return errors


def main() -> int:
    failures = _failures()
    if failures:
        for msg in failures:
            print(f"FAIL: {msg}", file=sys.stderr)
        return 1
    print("validate.py: all structural checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
