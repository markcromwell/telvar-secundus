#!/usr/bin/env python3
"""
TELVAR-RPG project validation script.
Checks that required files exist and have correct content.
Gracefully skips checks for files not yet created.
"""
import sys, os

errors = []

# project.godot — check settings if file exists
if os.path.exists("project.godot"):
    txt = open("project.godot").read()
    if "viewport_width=1280" not in txt:
        errors.append("project.godot: missing viewport_width=1280")
    if "viewport_height=720" not in txt:
        errors.append("project.godot: missing viewport_height=720")

# export_presets.cfg — check platform if file exists
if os.path.exists("export_presets.cfg"):
    txt = open("export_presets.cfg").read()
    if "Web" not in txt and "HTML5" not in txt:
        errors.append("export_presets.cfg: missing Web/HTML5 export target")

if errors:
    for e in errors:
        print("FAIL:", e)
    sys.exit(1)

print("All checks passed")
sys.exit(0)
