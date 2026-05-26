#!/usr/bin/env python3
"""
Structural validation for Telvar Secundus dialogue assets and DialogueBox UI.

Uses UTF-8 text parsing only — no Godot binary or database.
Exit 0 on success; non-zero with FAIL lines on error.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
DIALOGUE_DIR = REPO_ROOT / "assets" / "dialogue"
REQUIRED_FILES = ("myramar.json", "shopkeeper.json")
MAX_FILE_BYTES = 5 * 1024 * 1024


def _fail(errors: list[str], msg: str) -> None:
    errors.append(msg)


def check(errors: list[str], condition: bool, message: str) -> None:
    """Record a validation failure when condition is false (Dialogue System section)."""
    if not condition:
        errors.append(message)


def _check_entry_keys(errors: list[str], entry: object, *, label: str) -> None:
    if not isinstance(entry, dict):
        _fail(errors, f"{label}: entry must be a JSON object, got {type(entry).__name__}")
        return
    required = ("id", "text", "speaker", "next")
    for key in required:
        if key not in entry:
            _fail(errors, f"{label}: missing required key {key!r}")
            return
    for key in required:
        val = entry[key]
        if not isinstance(val, str):
            _fail(errors, f"{label}: {key!r} must be a string, got {type(val).__name__}")


def _check_choices(errors: list[str], choices: object, *, label: str) -> bool:
    """Return True if choices are structurally valid (2–4 items with text, next)."""
    if not isinstance(choices, list):
        _fail(errors, f"{label}: choices must be a JSON array")
        return False
    if not (2 <= len(choices) <= 4):
        _fail(errors, f"{label}: choices must have 2–4 items, got {len(choices)}")
        return False
    ok = True
    for i, ch in enumerate(choices):
        clabel = f"{label} choices[{i}]"
        if not isinstance(ch, dict):
            _fail(errors, f"{clabel}: must be an object")
            ok = False
            continue
        for key in ("text", "next"):
            if key not in ch:
                _fail(errors, f"{clabel}: missing {key!r}")
                ok = False
            elif not isinstance(ch[key], str):
                _fail(errors, f"{clabel}: {key!r} must be a string")
                ok = False
    return ok


def validate_dialogue_assets() -> list[str]:
    """Run all checks; return a list of error messages (empty if valid)."""
    errors: list[str] = []

    if not DIALOGUE_DIR.is_dir():
        _fail(errors, f"Missing dialogue directory: {DIALOGUE_DIR.relative_to(REPO_ROOT)}")
        return errors

    found_valid_choices = False

    for name in REQUIRED_FILES:
        path = DIALOGUE_DIR / name
        label = path.relative_to(REPO_ROOT).as_posix()

        if not path.is_file():
            _fail(errors, f"Missing required file: {label}")
            continue

        size = path.stat().st_size
        if size > MAX_FILE_BYTES:
            _fail(errors, f"{label}: file exceeds 5 MB ({size} bytes)")
            continue

        try:
            raw = path.read_text(encoding="utf-8")
        except OSError as exc:
            _fail(errors, f"{label}: cannot read file ({exc})")
            continue

        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            _fail(errors, f"{label}: invalid JSON ({exc})")
            continue

        if not isinstance(data, list):
            _fail(errors, f"{label}: root must be a JSON array")
            continue

        for i, entry in enumerate(data):
            elabel = f"{label}[{i}]"
            _check_entry_keys(errors, entry, label=elabel)
            if not isinstance(entry, dict):
                continue
            if "choices" in entry:
                if _check_choices(errors, entry["choices"], label=elabel):
                    found_valid_choices = True

    if not found_valid_choices:
        _fail(
            errors,
            "No dialogue entry with a valid choices array (2–4 items with text, next) "
            f"found across {', '.join(REQUIRED_FILES)}",
        )

    return errors


def validate_dialogue_system(project_godot: Path) -> list[str]:
    """Dialogue System structural checks (Godot project present): dirs, files, API strings, scene wiring."""
    errors: list[str] = []
    dialogue_dir = REPO_ROOT / "assets" / "dialogue"
    check(
        errors,
        dialogue_dir.is_dir(),
        f"Missing dialogue directory: {dialogue_dir.relative_to(REPO_ROOT).as_posix()}",
    )

    dbox_scene = REPO_ROOT / "scenes" / "DialogueBox.tscn"
    check(
        errors,
        dbox_scene.is_file(),
        f"Missing scene: {dbox_scene.relative_to(REPO_ROOT).as_posix()}",
    )

    dbox_script = REPO_ROOT / "scripts" / "DialogueBox.gd"
    check(
        errors,
        dbox_script.is_file(),
        f"Missing script: {dbox_script.relative_to(REPO_ROOT).as_posix()}",
    )

    dm_script = REPO_ROOT / "scripts" / "DialogueManager.gd"
    check(
        errors,
        dm_script.is_file(),
        f"Missing script: {dm_script.relative_to(REPO_ROOT).as_posix()}",
    )

    dm_src = dm_script.read_text(encoding="utf-8") if dm_script.is_file() else ""
    check(
        errors,
        "func show_dialogue(" in dm_src,
        "scripts/DialogueManager.gd: missing required snippet 'func show_dialogue('",
    )
    check(
        errors,
        "func set_flag(" in dm_src,
        "scripts/DialogueManager.gd: missing required snippet 'func set_flag('",
    )
    check(
        errors,
        "func get_flag(" in dm_src,
        "scripts/DialogueManager.gd: missing required snippet 'func get_flag('",
    )

    try:
        pg_text = project_godot.read_text(encoding="utf-8")
    except OSError as exc:
        check(errors, False, f"project.godot: cannot read file ({exc})")
        pg_text = ""
    check(
        errors,
        "DialogueManager=" in pg_text,
        "project.godot: missing DialogueManager autoload entry (expected 'DialogueManager=')",
    )

    tscn_text = dbox_scene.read_text(encoding="utf-8") if dbox_scene.is_file() else ""
    check(
        errors,
        'name="NameLabel"' in tscn_text,
        "scenes/DialogueBox.tscn: missing NameLabel node (expected name=\"NameLabel\")",
    )

    return errors


def _validate_gdscript_surface(label: str, src: str) -> list[str]:
    """Very light GDScript hygiene checks (text-only; not a full parser)."""
    errors: list[str] = []
    for i, line in enumerate(src.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("="):
            errors.append(f"{label}: line {i} looks like a dangling assignment")
    return errors


def validate_dialogue_box() -> list[str]:
    """Check DialogueBox scene/script presence and required symbols."""
    errors: list[str] = []
    scene = REPO_ROOT / "scenes" / "DialogueBox.tscn"
    script = REPO_ROOT / "scripts" / "DialogueBox.gd"

    if not scene.is_file():
        errors.append(f"Missing scene: {scene.relative_to(REPO_ROOT).as_posix()}")
    else:
        raw = scene.read_text(encoding="utf-8")
        if "format=3" not in raw:
            errors.append("scenes/DialogueBox.tscn must declare format=3")
        for name in ("PortraitRect", "NameLabel", "TextLabel", "ChoicesContainer"):
            if f'name="{name}"' not in raw:
                errors.append(f"scenes/DialogueBox.tscn: missing node {name!r}")

    if not script.is_file():
        errors.append(f"Missing script: {script.relative_to(REPO_ROOT).as_posix()}")
    else:
        src = script.read_text(encoding="utf-8")
        needles = (
            "func show_dialogue(",
            "func hide_dialogue(",
            "signal choice_selected",
            "func _unhandled_input(",
        )
        for needle in needles:
            if needle not in src:
                errors.append(f"scripts/DialogueBox.gd: missing required snippet {needle!r}")
        if not re.search(r"CHARS_PER_SEC(?:\s*:\s*\w+)?\s*=\s*30\.0", src):
            errors.append("scripts/DialogueBox.gd: expected CHARS_PER_SEC assignment to 30.0")
        rel = script.relative_to(REPO_ROOT).as_posix()
        errors.extend(_validate_gdscript_surface(rel, src))

    return errors


def run_all_validations() -> list[str]:
    errors: list[str] = []
    errors.extend(validate_dialogue_assets())
    project_godot = REPO_ROOT / "project.godot"
    if project_godot.is_file():
        errors.extend(validate_dialogue_system(project_godot))
    errors.extend(validate_dialogue_box())
    return errors


def main() -> int:
    errors = run_all_validations()
    if errors:
        for e in errors:
            print("FAIL:", e)
        return 1
    print("OK: validation passed (dialogue JSON + Dialogue System + DialogueBox structure)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
