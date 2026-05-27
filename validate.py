#!/usr/bin/env python3
"""
TELVAR-RPG validation script (bootstrap stub).
Full validation is implemented in spec #1246.
During early development, this exits 0 to allow the pipeline to proceed.
"""
import os
import sys


ROOT = os.path.dirname(os.path.abspath(__file__))


def read_text(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def first_existing(*relative_paths):
    for relative_path in relative_paths:
        path = os.path.join(ROOT, relative_path)
        if os.path.isfile(path):
            return path
    return None

# Bootstrap mode: check only what is strictly required at this stage
errors = []

_credits = os.path.join(ROOT, "CREDITS.md")
if not os.path.isfile(_credits):
    errors.append("Missing CREDITS.md at repository root")
else:
    _ct = read_text(_credits)
    if "# Credits" not in _ct:
        errors.append("CREDITS.md must contain a '# Credits' heading")
    for _heading in ("## Art", "## Code", "## Story", "## Audio"):
        if _heading not in _ct:
            errors.append(f"CREDITS.md must contain section {_heading}")

_credits_scene = first_existing("scenes/ui/Credits.tscn", "Credits.tscn")
if _credits_scene is None:
    errors.append("Missing Credits scene (expected scenes/ui/Credits.tscn or Credits.tscn)")
else:
    _scene = read_text(_credits_scene)
    if 'type="Control"' not in _scene:
        errors.append("Credits scene must have a Control root")
    if 'type="ScrollContainer"' not in _scene:
        errors.append("Credits scene must include a ScrollContainer")
    if 'type="RichTextLabel"' not in _scene:
        errors.append("Credits scene must include a RichTextLabel")

_main_menu_scene = first_existing("scenes/ui/MainMenu.tscn", "MainMenu.tscn")
if _main_menu_scene is None:
    errors.append("Missing MainMenu scene (expected scenes/ui/MainMenu.tscn or MainMenu.tscn)")
else:
    _menu = read_text(_main_menu_scene)
    if 'name="CreditsButton"' not in _menu:
        errors.append("MainMenu scene must include a CreditsButton node")
    if 'type="Button"' not in _menu:
        errors.append("MainMenu CreditsButton must be a Button node")
    if 'text = "Credits"' not in _menu and 'text="Credits"' not in _menu:
        errors.append('MainMenu CreditsButton must display text "Credits"')

_export_presets = os.path.join(ROOT, "export_presets.cfg")
if os.path.isfile(_export_presets):
    _export = read_text(_export_presets)
    if 'platform="Web"' in _export and "*.md" not in _export:
        errors.append("Web export preset must include markdown files so CREDITS.md is packaged")

# Only enforce critical structural checks here
# (Full validation in spec 1246)

if errors:
    for e in errors:
        print("FAIL:", e)
    sys.exit(1)

print("Bootstrap checks passed (spec 1246 will add full validation)")
sys.exit(0)
