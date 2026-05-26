#!/usr/bin/env python3
"""
TELVAR-RPG validation script (bootstrap stub).
Full validation is implemented in spec #1246.
During early development, this exits 0 to allow the pipeline to proceed.
"""
import sys, os

# Bootstrap mode: check only what is strictly required at this stage
errors = []

root = os.path.dirname(os.path.abspath(__file__))
_dm = os.path.join(root, "scripts", "detect_magic_passive.gd")
_pg = os.path.join(root, "project.godot")
if not os.path.isfile(_dm):
    errors.append("missing scripts/detect_magic_passive.gd")
elif not os.path.isfile(_pg):
    errors.append("missing project.godot")
else:
    with open(_pg, encoding="utf-8") as f:
        pg = f.read()
    if "DetectMagicPassive=" not in pg or "detect_magic_passive.gd" not in pg:
        errors.append("project.godot must autoload DetectMagicPassive (detect_magic_passive.gd)")

# Only enforce critical structural checks here
# (Full validation in spec 1246)

if errors:
    for e in errors:
        print("FAIL:", e)
    sys.exit(1)

print("Bootstrap checks passed (spec 1246 will add full validation)")
sys.exit(0)
