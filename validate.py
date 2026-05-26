#!/usr/bin/env python3
"""Structural validation for Telvar Secundus (Godot 4.x).

Runs in CI without the Godot editor. Dialogue and project layout checks print
PASS:/FAIL: lines and exit non-zero on any failure.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _pass(name: str) -> None:
    print(f"PASS: {name}")


def _fail(name: str, detail: str = "") -> str:
    suffix = f" — {detail}" if detail else ""
    print(f"FAIL: {name}{suffix}")
    return name


def _check_dialogue_manager_api(body: str) -> list[str]:
    missing: list[str] = []
    if "func show_dialogue(" not in body:
        missing.append("show_dialogue")
    if "func set_flag(" not in body:
        missing.append("set_flag")
    if "func get_flag(" not in body:
        missing.append("get_flag")
    return missing


def _count_gdunit_tests(script: str) -> int:
    return len(re.findall(r"^\s*func\s+test_\w+\s*\(", script, flags=re.MULTILINE))


def main() -> int:
    failures: list[str] = []

    # --- Dialogue system (phase 2513) ---
    dialogue_dir = REPO_ROOT / "assets" / "dialogue"
    if dialogue_dir.is_dir():
        _pass("dialogue: assets/dialogue directory exists")
    else:
        failures.append(_fail("dialogue: assets/dialogue directory exists", "missing or not a directory"))

    dm_path = REPO_ROOT / "scripts" / "DialogueManager.gd"
    if dm_path.is_file():
        dm_body = _read_text(dm_path)
        missing_api = _check_dialogue_manager_api(dm_body)
        if not missing_api:
            _pass("dialogue: DialogueManager.gd defines show_dialogue, set_flag, get_flag")
        else:
            failures.append(
                _fail(
                    "dialogue: DialogueManager.gd defines show_dialogue, set_flag, get_flag",
                    f"missing: {', '.join(missing_api)}",
                )
            )
    else:
        failures.append(_fail("dialogue: DialogueManager.gd exists", f"not found: {dm_path}"))

    box_path = REPO_ROOT / "scenes" / "DialogueBox.tscn"
    if box_path.is_file():
        _pass("dialogue: scenes/DialogueBox.tscn exists")
    else:
        failures.append(_fail("dialogue: scenes/DialogueBox.tscn exists", f"not found: {box_path}"))

    npc_path = REPO_ROOT / "scripts" / "NPC.gd"
    if npc_path.is_file():
        _pass("dialogue: scripts/NPC.gd exists")
    else:
        failures.append(_fail("dialogue: scripts/NPC.gd exists", f"not found: {npc_path}"))

    project_path = REPO_ROOT / "project.godot"
    if project_path.is_file():
        pg = _read_text(project_path)
        if "[autoload]" in pg and 'DialogueManager="*res://scripts/DialogueManager.gd"' in pg:
            _pass("dialogue: project.godot [autoload] registers DialogueManager")
        else:
            failures.append(
                _fail(
                    "dialogue: project.godot [autoload] registers DialogueManager",
                    "expected DialogueManager autoload line not found",
                )
            )
    else:
        failures.append(_fail("dialogue: project.godot readable for autoload check", f"not found: {project_path}"))

    gdunit_path = REPO_ROOT / "test" / "test_dialogue_manager.gd"
    if gdunit_path.is_file():
        suite = _read_text(gdunit_path)
        if "extends GdUnitTestSuite" in suite and _count_gdunit_tests(suite) >= 5:
            _pass("dialogue: test/test_dialogue_manager.gd is a GdUnit suite with >= 5 test cases")
        else:
            failures.append(
                _fail(
                    "dialogue: test/test_dialogue_manager.gd is a GdUnit suite with >= 5 test cases",
                    "must extend GdUnitTestSuite and declare at least five func test_*() cases",
                )
            )
    else:
        failures.append(_fail("dialogue: test/test_dialogue_manager.gd exists", f"not found: {gdunit_path}"))

    if failures:
        print(f"\nvalidate.py: {len(failures)} check(s) failed.", file=sys.stderr)
        return 1

    print("\nvalidate.py: all dialogue checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
