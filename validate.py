#!/usr/bin/env python3
"""Structural validation for Telvar Secundus Godot project (no Godot binary)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent


def _fail(msg: str) -> None:
    print("FAIL:", msg, file=sys.stderr)


def main() -> int:
    errors: list[str] = []

    required = [
        REPO_ROOT / "project.godot",
        REPO_ROOT / "assets" / "tilesets" / "lpc_terrain.png",
        REPO_ROOT / "assets" / "tilesets" / "lpc_terrain.tres",
        REPO_ROOT / "assets" / "dialogue" / "myramar.json",
        REPO_ROOT / "scenes" / "council_chamber" / "council_chamber.tscn",
        REPO_ROOT / "scenes" / "council_chamber" / "council_chamber.gd",
        REPO_ROOT / "scenes" / "myramar_office" / "myramar_office.tscn",
        REPO_ROOT / "scenes" / "myramar_office" / "myramar_office.gd",
        REPO_ROOT / "autoload" / "dialogue_manager.gd",
    ]
    for path in required:
        if not path.is_file():
            errors.append(f"Missing required file: {path.relative_to(REPO_ROOT)}")

    pg = REPO_ROOT / "project.godot"
    if pg.is_file():
        text = pg.read_text(encoding="utf-8")
        if "[autoload]" not in text:
            errors.append("project.godot must define an [autoload] section")
        elif "autoload/dialogue_manager.gd" not in text:
            errors.append("project.godot must register DialogueManager autoload script")

    cc = REPO_ROOT / "scenes" / "council_chamber" / "council_chamber.tscn"
    if cc.is_file():
        t = cc.read_text(encoding="utf-8")
        for needle in ("OfficeDoor", "TowerStairsExit", "lpc_terrain.tres"):
            if needle not in t:
                errors.append(f"council_chamber.tscn must contain {needle!r}")

    mo = REPO_ROOT / "scenes" / "myramar_office" / "myramar_office.tscn"
    if mo.is_file():
        t = mo.read_text(encoding="utf-8")
        for needle in ("DeskInspectArea", "MyramarTalkArea", "CouncilReturn", "lpc_terrain.tres"):
            if needle not in t:
                errors.append(f"myramar_office.tscn must contain {needle!r}")

    tres = REPO_ROOT / "assets" / "tilesets" / "lpc_terrain.tres"
    if tres.is_file():
        tt = tres.read_text(encoding="utf-8")
        if "4:0/0 = 0" not in tt or "5:0/0 = 0" not in tt or "6:0/0 = 0" not in tt:
            errors.append("lpc_terrain.tres must define atlas columns 4–6 for office props")

    dial = REPO_ROOT / "assets" / "dialogue" / "myramar.json"
    if dial.is_file():
        try:
            data = json.loads(dial.read_text(encoding="utf-8"))
            if not isinstance(data, list) or not data:
                errors.append("myramar.json must be a non-empty JSON array")
        except json.JSONDecodeError as exc:
            errors.append(f"myramar.json invalid JSON: {exc}")

    if errors:
        for e in errors:
            _fail(e)
        return 1

    print("validate.py: structural checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
