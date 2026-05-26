#!/usr/bin/env python3
"""
TELVAR-RPG validation script (bootstrap stub).
Full validation is implemented in spec #1246.
During early development, this exits 0 to allow the pipeline to proceed.
"""
import sys, os

# Bootstrap mode: check only what is strictly required at this stage
errors = []

ROOT = os.path.dirname(os.path.abspath(__file__))
combat_gd = os.path.join(ROOT, "scripts", "CombatManager.gd")
if not os.path.isfile(combat_gd):
    errors.append("Missing scripts/CombatManager.gd")
else:
    with open(combat_gd, encoding="utf-8") as f:
        cg = f.read()
    for needle in ("PLAYER_TURN", "ENEMY_TURN", "randi_range(1, 6)"):
        if needle not in cg:
            errors.append(f"CombatManager.gd missing required fragment: {needle!r}")

# Only enforce critical structural checks here
# (Full validation in spec 1246)

if errors:
    for e in errors:
        print("FAIL:", e)
    sys.exit(1)

print("Bootstrap checks passed (spec 1246 will add full validation)")
sys.exit(0)
