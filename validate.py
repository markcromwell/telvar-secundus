#!/usr/bin/env python3
"""
TELVAR-RPG validation script (bootstrap stub).
Full validation is implemented in spec #1246.
During early development, this exits 0 to allow the pipeline to proceed.
"""
import sys, os

# Bootstrap mode: check only what is strictly required at this stage
errors = []

repo_root = os.path.dirname(os.path.abspath(__file__))
myramar_scene = os.path.join(repo_root, "scenes", "npcs", "myramar.tscn")
myramar_script = os.path.join(repo_root, "scripts", "npcs", "myramar.gd")
for label, path in (
    ("Myramar NPC scene", myramar_scene),
    ("Myramar NPC script", myramar_script),
):
    if not os.path.isfile(path):
        errors.append(f"{label} missing: {path}")

# Only enforce critical structural checks here
# (Full validation in spec 1246)

if errors:
    for e in errors:
        print("FAIL:", e)
    sys.exit(1)

print("Bootstrap checks passed (spec 1246 will add full validation)")
sys.exit(0)
