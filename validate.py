#!/usr/bin/env python3
"""TELVAR-RPG structural validation (file layout, key strings, GDScript markers).

Uses path and text checks only — no Godot binary, no database.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent

# Substrings that suggest Godot 3-era APIs — must not appear in scanned GDScript.
KNOWN_BAD_GDSCRIPT_MARKERS: tuple[str, ...] = (
    "yield(",
    "KinematicBody2D",
    "KinematicBody3D",
    "onready var",
    "extends KinematicBody2D",
    "extends KinematicBody3D",
)

errors: list[str] = []


def _fail(check_id: str, message: str) -> None:
    errors.append(f"{check_id}: {message}")


def _must_exist_path(check_id: str, path: Path, kind: str) -> bool:
    if not path.exists():
        _fail(check_id, f"missing {kind}: {path.relative_to(REPO_ROOT)}")
        return False
    return True


def _must_be_dir(check_id: str, path: Path) -> bool:
    if not path.is_dir():
        _fail(check_id, f"not a directory: {path.relative_to(REPO_ROOT)}")
        return False
    return True


def _must_be_file(check_id: str, path: Path) -> bool:
    if not path.is_file():
        _fail(check_id, f"not a file: {path.relative_to(REPO_ROOT)}")
        return False
    return True


def _file_must_contain(check_id: str, path: Path, needle: str) -> None:
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    if needle not in text:
        _fail(check_id, f"{path.relative_to(REPO_ROOT)} must contain {needle!r}")


def _scan_gdscript_for_known_bad(check_id: str, path: Path) -> None:
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    for bad in KNOWN_BAD_GDSCRIPT_MARKERS:
        if bad in text:
            _fail(
                check_id,
                f"{path.relative_to(REPO_ROOT)} contains forbidden marker {bad!r}",
            )


def check_dialogue_quest_scripts_and_scene_exist() -> None:
    """Phase 2537 — core dialogue/quest script and scene paths."""
    cid = "dialogue_quest_core_paths"
    qm = REPO_ROOT / "scripts" / "quest_manager.gd"
    dm = REPO_ROOT / "scripts" / "dialogue_manager.gd"
    db = REPO_ROOT / "scripts" / "dialogue_box.gd"
    tscn = REPO_ROOT / "scenes" / "DialogueBox.tscn"
    for p in (qm, dm, db):
        if _must_exist_path(cid, p, "file") and _must_be_file(cid, p):
            pass
    if _must_exist_path(cid, tscn, "file"):
        _must_be_file(cid, tscn)


def check_dialogue_and_quest_asset_dirs_exist() -> None:
    """Phase 2537 — dialogue JSON and quest JSON directories."""
    cid = "dialogue_quest_asset_dirs"
    ddir = REPO_ROOT / "assets" / "dialogue"
    qdir = REPO_ROOT / "assets" / "quests"
    if _must_exist_path(cid, ddir, "directory") and _must_be_dir(cid, ddir):
        pass
    if _must_exist_path(cid, qdir, "directory") and _must_be_dir(cid, qdir):
        pass


def check_quest_manager_defines_start_quest() -> None:
    """Phase 2537 — QuestManager API surface for journal integration."""
    cid = "quest_manager_start_quest_signature"
    path = REPO_ROOT / "scripts" / "quest_manager.gd"
    _file_must_contain(cid, path, "func start_quest(")


def check_dialogue_manager_defines_show_dialogue() -> None:
    """Phase 2537 — DialogueManager entry point for UI."""
    cid = "dialogue_manager_show_dialogue_signature"
    path = REPO_ROOT / "scripts" / "dialogue_manager.gd"
    _file_must_contain(cid, path, "func show_dialogue(")


def check_dialogue_box_scene_has_choices_container() -> None:
    """Phase 2537 — DialogueBox scene wires choice UI."""
    cid = "dialogue_box_scene_choices_container"
    path = REPO_ROOT / "scenes" / "DialogueBox.tscn"
    _file_must_contain(cid, path, 'name="ChoicesContainer"')


def check_project_autoloads_quest_and_dialogue_managers() -> None:
    """Phase 2537 — singletons registered for cross-system calls."""
    cid = "project_autoload_quest_dialogue"
    path = REPO_ROOT / "project.godot"
    if not path.is_file():
        _fail(cid, "project.godot missing")
        return
    text = path.read_text(encoding="utf-8")
    if "[autoload]" not in text:
        _fail(cid, "project.godot missing [autoload] section")
        return
    tail = text.split("[autoload]", 1)[1]
    block = tail.split("[", 1)[0] if "[" in tail else tail
    if "QuestManager=" not in block:
        _fail(cid, "QuestManager autoload not found under [autoload]")
    if "DialogueManager=" not in block:
        _fail(cid, "DialogueManager autoload not found under [autoload]")


def check_dialogue_flags_gdunit_suite_contract() -> None:
    """Phase 2537 — GdUnit suite for QuestManager / DialogueManager behaviour."""
    cid = "dialogue_flags_gdunit_suite"
    path = REPO_ROOT / "test" / "test_dialogue_flags.gd"
    if not (_must_exist_path(cid, path, "file") and _must_be_file(cid, path)):
        return
    src = path.read_text(encoding="utf-8")
    if "extends GdUnitTestSuite" not in src:
        _fail(cid, "test_dialogue_flags.gd must extend GdUnitTestSuite")
    test_funcs = re.findall(r"^\s*func\s+(test_\w+)\s*\(", src, flags=re.MULTILINE)
    if len(test_funcs) < 5:
        _fail(
            cid,
            f"expected at least 5 test_ functions, found {len(test_funcs)}: {test_funcs!r}",
        )


def check_dialogue_flags_gdscript_known_bad_clean() -> None:
    """Phase 2537 — dialogue flag tests avoid legacy Godot 3 patterns."""
    cid = "dialogue_flags_gdscript_known_bad"
    path = REPO_ROOT / "test" / "test_dialogue_flags.gd"
    _scan_gdscript_for_known_bad(cid, path)


DIALOGUE_QUEST_CHECKS: tuple[str, ...] = (
    "dialogue_quest_core_paths",
    "dialogue_quest_asset_dirs",
    "quest_manager_start_quest_signature",
    "dialogue_manager_show_dialogue_signature",
    "dialogue_box_scene_choices_container",
    "project_autoload_quest_dialogue",
    "dialogue_flags_gdunit_suite",
    "dialogue_flags_gdscript_known_bad",
)


def main() -> int:
    # Phase 2537 — dialogue / quest structural validation (8+ named checks)
    check_dialogue_quest_scripts_and_scene_exist()
    check_dialogue_and_quest_asset_dirs_exist()
    check_quest_manager_defines_start_quest()
    check_dialogue_manager_defines_show_dialogue()
    check_dialogue_box_scene_has_choices_container()
    check_project_autoloads_quest_and_dialogue_managers()
    check_dialogue_flags_gdunit_suite_contract()
    check_dialogue_flags_gdscript_known_bad_clean()

    if errors:
        print("validate.py: FAILED", file=sys.stderr)
        for e in errors:
            print("FAIL:", e, file=sys.stderr)
        return 1

    print("validate.py: OK (%d dialogue/quest checks)" % len(DIALOGUE_QUEST_CHECKS))
    for name in DIALOGUE_QUEST_CHECKS:
        print("  -", name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
