#!/usr/bin/env python3
"""
TELVAR-RPG validation script (bootstrap stub).
Full validation is implemented in spec #1246.
During early development, this exits 0 to allow the pipeline to proceed.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent

# Bootstrap mode: check only what is strictly required at this stage
errors = []

# Only enforce critical structural checks here
# (Full validation in spec 1246)

REQUIRED_FILES = [
    REPO_ROOT / "scripts" / "spell.gd",
    REPO_ROOT / "scripts" / "mana_component.gd",
    REPO_ROOT / "scripts" / "spell_book.gd",
    REPO_ROOT / "resources" / "spells" / "ember.tres",
    REPO_ROOT / "resources" / "spells" / "shield_light.tres",
    REPO_ROOT / "resources" / "spells" / "reveal.tres",
]

for path in REQUIRED_FILES:
    if not path.is_file():
        errors.append(f"Missing required file: {path.relative_to(REPO_ROOT)}")

_project_godot = REPO_ROOT / "project.godot"
if _project_godot.is_file():
    text = _project_godot.read_text(encoding="utf-8")
    if "SpellBook=" not in text or "scripts/spell_book.gd" not in text:
        errors.append("project.godot must register SpellBook autoload to scripts/spell_book.gd")
else:
    errors.append("Missing required file: project.godot")

if errors:
    for e in errors:
        print("FAIL:", e)
    sys.exit(1)

print("Bootstrap checks passed (spec 1246 will add full validation)")
sys.exit(0)
