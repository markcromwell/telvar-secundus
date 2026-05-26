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

combat_ui_tscn = os.path.join(ROOT, "scenes", "CombatUI.tscn")
if not os.path.isfile(combat_ui_tscn):
    errors.append("Missing scenes/CombatUI.tscn")
else:
    with open(combat_ui_tscn, encoding="utf-8") as f:
        cu = f.read()
    for needle in (
        'type="CanvasLayer"',
        "InitiativeLabel",
        "TurnIndicator",
        "PlayerHpBar",
        "EnemyHpBar",
        "VBoxContainer",
        "AttackButton",
        "CastSpellButton",
        "FleeButton",
        "CombatUI.gd",
    ):
        if needle not in cu:
            errors.append(f"CombatUI.tscn missing required fragment: {needle!r}")

encounter_gd = os.path.join(ROOT, "scripts", "EnemyEncounterZone.gd")
if not os.path.isfile(encounter_gd):
    errors.append("Missing scripts/EnemyEncounterZone.gd")
else:
    with open(encounter_gd, encoding="utf-8") as f:
        eg = f.read()
    for needle in ("body_entered", "CombatManager.start_combat", 'is_in_group("player")'):
        if needle not in eg:
            errors.append(f"EnemyEncounterZone.gd missing required fragment: {needle!r}")

world_demo_ctrl = os.path.join(ROOT, "scripts", "WorldDemoController.gd")
if not os.path.isfile(world_demo_ctrl):
    errors.append("Missing scripts/WorldDemoController.gd")
else:
    with open(world_demo_ctrl, encoding="utf-8") as f:
        wdc = f.read()
    for needle in (
        "roll_action_damage",
        "maxi(1, attacker_attack - defender_defense + randi_range(-2, 2))",
        "cast_spell",
        "FLEE_SUCCESS_CHANCE",
    ):
        if needle not in wdc:
            errors.append(f"WorldDemoController.gd missing required fragment: {needle!r}")

world_tscn = os.path.join(ROOT, "scenes", "WorldDemo.tscn")
if not os.path.isfile(world_tscn):
    errors.append("Missing scenes/WorldDemo.tscn")
else:
    with open(world_tscn, encoding="utf-8") as f:
        w = f.read()
    for needle in (
        'type="Area2D"',
        "EnemyEncounterZone.gd",
        "TelvarController.gd",
        "CombatUI.tscn",
        "WorldDemoController.gd",
    ):
        if needle not in w:
            errors.append(f"WorldDemo.tscn missing required fragment: {needle!r}")

# Only enforce critical structural checks here
# (Full validation in spec 1246)

if errors:
    for e in errors:
        print("FAIL:", e)
    sys.exit(1)

print("Bootstrap checks passed (spec 1246 will add full validation)")
sys.exit(0)
