#!/usr/bin/env python3
"""
TELVAR-RPG validation script (bootstrap stub).
Full validation is implemented in spec #1246.
During early development, this exits 0 to allow the pipeline to proceed.
"""
import sys
from pathlib import Path

# Bootstrap mode: check only what is strictly required at this stage
errors: list[str] = []

REPO_ROOT = Path(__file__).resolve().parent

# Save system (phase 2602): autoload + script must exist for HTML5 builds
_save_script = REPO_ROOT / "save_system.gd"
_project = REPO_ROOT / "project.godot"
if not _save_script.is_file():
    errors.append("Missing save_system.gd (SaveSystem autoload target).")
if _project.is_file():
    project_text = _project.read_text(encoding="utf-8")
    if 'SaveSystem="*res://save_system.gd"' not in project_text:
        errors.append("project.godot must register SaveSystem autoload at res://save_system.gd")
else:
    errors.append("Missing project.godot")

# Only enforce critical structural checks here
# (Full validation in spec 1246)

if errors:
    for e in errors:
        print("FAIL:", e)
    sys.exit(1)

print("Bootstrap checks passed (spec 1246 will add full validation)")
sys.exit(0)
