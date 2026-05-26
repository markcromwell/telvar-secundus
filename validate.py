#!/usr/bin/env python3
"""
TELVAR-RPG structural validation (phase 2606 / spec 1301).

Uses text parsing only — no Godot runtime. Exits 0 when checks pass.
"""
import re
import sys
from pathlib import Path

errors: list[str] = []

REPO_ROOT = Path(__file__).resolve().parent


def _save_menu_slot_button_names(tscn_text: str) -> list[str]:
    """Return Button node names that look like manual save slots (Godot 4 .tscn text format)."""
    names: list[str] = []
    for m in re.finditer(r'^\[node name="([^"]+)" type="Button"', tscn_text, flags=re.MULTILINE):
        name = m.group(1)
        if name.startswith("SaveSlot") or name in ("Slot1", "Slot2", "Slot3"):
            names.append(name)
    return names

# Save system (phase 2602): autoload + script must exist for HTML5 builds
_save_script = REPO_ROOT / "save_system.gd"
_project = REPO_ROOT / "project.godot"
if not _save_script.is_file():
    errors.append("Missing save_system.gd (SaveSystem autoload target).")
else:
    _save_src = _save_script.read_text(encoding="utf-8")
    if "FileAccess.open" not in _save_src:
        errors.append("save_system.gd must call FileAccess.open for save/load I/O.")
    if "FileAccess.WRITE" not in _save_src:
        errors.append("save_system.gd must use FileAccess.WRITE when writing save JSON.")
    if "FileAccess.READ" not in _save_src:
        errors.append("save_system.gd must use FileAccess.READ when reading save JSON.")
    for needle in ("user://save_slot_", '"play_time"', '"game_complete"', '"dark_robe_unlocked"'):
        if needle not in _save_src:
            errors.append(f"save_system.gd missing expected save/completion token: {needle!r}")
if _project.is_file():
    project_text = _project.read_text(encoding="utf-8")
    if 'SaveSystem="*res://save_system.gd"' not in project_text:
        errors.append("project.godot must register SaveSystem autoload at res://save_system.gd")
    if 'SceneTransition="*res://scripts/scene_transition.gd"' not in project_text:
        errors.append(
            "project.godot must register SceneTransition autoload at res://scripts/scene_transition.gd"
        )
else:
    errors.append("Missing project.godot")

_save_menu_scene = REPO_ROOT / "scenes" / "save_menu.tscn"
_save_menu_script = REPO_ROOT / "scripts" / "save_menu.gd"
_scene_transition_script = REPO_ROOT / "scripts" / "scene_transition.gd"
if not _save_menu_scene.is_file():
    errors.append("Missing scenes/save_menu.tscn (SaveMenu UI).")
if not _save_menu_script.is_file():
    errors.append("Missing scripts/save_menu.gd (SaveMenu logic).")
if not _scene_transition_script.is_file():
    errors.append("Missing scripts/scene_transition.gd (scene_changed + autosave hook).")
if _save_menu_scene.is_file():
    _save_menu_txt = _save_menu_scene.read_text(encoding="utf-8")
    _slot_btn_names = _save_menu_slot_button_names(_save_menu_txt)
    if len(_slot_btn_names) < 3:
        errors.append(
            "scenes/save_menu.tscn must define three manual save slot Buttons "
            '(node names starting with "SaveSlot" or legacy Slot1–Slot3).'
        )
    else:
        _has_save_slot = any(n.startswith("SaveSlot") for n in _slot_btn_names)
        _has_legacy = {"Slot1", "Slot2", "Slot3"}.issubset(set(_slot_btn_names))
        if not (_has_save_slot or _has_legacy):
            errors.append(
                "scenes/save_menu.tscn save slot Buttons must be named SaveSlot* (spec) "
                "or include Slot1, Slot2, and Slot3."
            )

_credits_md = REPO_ROOT / "CREDITS.md"
_main_menu = REPO_ROOT / "scenes" / "main_menu.tscn"
_credits_scene = REPO_ROOT / "scenes" / "credits.tscn"
_end_screen = REPO_ROOT / "scenes" / "end_screen.tscn"
_end_screen_gd = REPO_ROOT / "scripts" / "end_screen.gd"
_credits_gd = REPO_ROOT / "scripts" / "credits.gd"
_active_slot = REPO_ROOT / "scripts" / "active_save_slot.gd"
if not _credits_md.is_file():
    errors.append("Missing CREDITS.md")
else:
    _credits_text = _credits_md.read_text(encoding="utf-8")
    _credits_stripped = [ln.strip() for ln in _credits_text.splitlines() if ln.strip()]
    _required_md_headings = ("# Credits", "## Art", "## Code", "## Story")
    for heading in _required_md_headings:
        if heading not in _credits_stripped:
            errors.append(f"CREDITS.md missing required heading line: {heading!r}")
    if _credits_stripped and _credits_stripped[0] != "# Credits":
        errors.append('CREDITS.md must begin with the "# Credits" title heading.')
    for line in (
        "LPC Base Sprites",
        "Godot Engine 4.3",
        "New Paladin Order",
    ):
        if line not in _credits_text:
            errors.append(f"CREDITS.md missing expected attribution line: {line!r}")
if not _main_menu.is_file():
    errors.append("Missing scenes/main_menu.tscn")
if not _credits_scene.is_file():
    errors.append("Missing scenes/credits.tscn")
if not _end_screen.is_file():
    errors.append("Missing scenes/end_screen.tscn")
else:
    _end_txt = _end_screen.read_text(encoding="utf-8")
    if '[node name="PlayTime" type="Label"' not in _end_txt:
        errors.append('scenes/end_screen.tscn must define a Label node named "PlayTime" for elapsed time.')
    if '[node name="ToCredits" type="Button"' not in _end_txt:
        errors.append('scenes/end_screen.tscn must define a Button node named "ToCredits".')
if not _end_screen_gd.is_file():
    errors.append("Missing scripts/end_screen.gd (end screen / play time UI).")
if not _credits_gd.is_file():
    errors.append("Missing scripts/credits.gd")
if not _active_slot.is_file():
    errors.append("Missing scripts/active_save_slot.gd")
if _project.is_file() and 'ActiveSaveSlot="*res://scripts/active_save_slot.gd"' not in _project.read_text(
    encoding="utf-8"
):
    errors.append("project.godot must register ActiveSaveSlot autoload at res://scripts/active_save_slot.gd")
if _main_menu.is_file():
    _mm_txt = _main_menu.read_text(encoding="utf-8")
    if '[node name="Credits" type="Button"' not in _mm_txt:
        errors.append("scenes/main_menu.tscn must include a Credits button.")

if errors:
    for e in errors:
        print("FAIL:", e)
    sys.exit(1)

print("Validation passed (structural checks, phase 2606).")
sys.exit(0)
