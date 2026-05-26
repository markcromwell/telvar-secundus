#!/usr/bin/env python3
"""Structural validation for Telvar Secundus Godot project (no Godot binary).

Exits 0 on success after printing PASS; exits 1 with a descriptive line on failure.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent

REQUIRED_FILES: tuple[Path, ...] = (
    REPO_ROOT / "project.godot",
    REPO_ROOT / "scripts" / "lore_manager.gd",
    REPO_ROOT / "scripts" / "dialogue_manager.gd",
    REPO_ROOT / "scripts" / "lore_notification.gd",
    REPO_ROOT / "scenes" / "hud" / "lore_notification.tscn",
    REPO_ROOT / "scenes" / "ui" / "lore_tab.tscn",
    REPO_ROOT / "assets" / "lore" / "lore_entries.json",
)


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    sys.exit(1)


def main() -> None:
    for path in REQUIRED_FILES:
        if not path.is_file():
            fail(f"FAIL: missing required file: {path.relative_to(REPO_ROOT)}")

    lore_json = REPO_ROOT / "assets" / "lore" / "lore_entries.json"
    try:
        data = json.loads(lore_json.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"FAIL: lore_entries.json is not valid JSON: {exc}")

    if not isinstance(data, list):
        fail("FAIL: lore_entries.json must be a JSON array of objects")

    if len(data) != 10:
        fail(
            f"FAIL: lore_entries.json must contain exactly 10 entries (found {len(data)})"
        )

    seen_ids: set[str] = set()
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            fail(f"FAIL: lore_entries.json entry {i} is not an object")
        for key in ("id", "title", "text"):
            if key not in item:
                fail(f"FAIL: lore_entries.json entry {i} missing key {key!r}")
            val = item[key]
            if not isinstance(val, str) or not val.strip():
                fail(
                    f"FAIL: lore_entries.json entry {i} key {key!r} must be a non-empty string"
                )
        eid = item["id"]
        if eid in seen_ids:
            fail(f"FAIL: duplicate lore id {eid!r} in lore_entries.json")
        seen_ids.add(eid)

    notif_tscn = (REPO_ROOT / "scenes" / "hud" / "lore_notification.tscn").read_text(
        encoding="utf-8"
    )
    if "CanvasLayer" not in notif_tscn:
        fail("FAIL: lore_notification.tscn must contain the string 'CanvasLayer'")
    if "Label" not in notif_tscn:
        fail("FAIL: lore_notification.tscn must contain the string 'Label'")

    lore_tab_tscn = (REPO_ROOT / "scenes" / "ui" / "lore_tab.tscn").read_text(
        encoding="utf-8"
    )
    if "ScrollContainer" not in lore_tab_tscn:
        fail("FAIL: lore_tab.tscn must contain the string 'ScrollContainer'")
    if "VBoxContainer" not in lore_tab_tscn:
        fail("FAIL: lore_tab.tscn must contain the string 'VBoxContainer'")

    lore_mgr = (REPO_ROOT / "scripts" / "lore_manager.gd").read_text(encoding="utf-8")
    if "signal lore_unlocked" not in lore_mgr:
        fail("FAIL: lore_manager.gd must contain 'signal lore_unlocked'")
    if "func unlock" not in lore_mgr:
        fail("FAIL: lore_manager.gd must contain 'func unlock'")
    if "func is_unlocked" not in lore_mgr:
        fail("FAIL: lore_manager.gd must contain 'func is_unlocked'")

    print("PASS")
    sys.exit(0)


if __name__ == "__main__":
    main()
