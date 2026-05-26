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
trigger_tscn = os.path.join(root, "scenes", "emporium", "act1_conclusion_trigger.tscn")
act1_gd = os.path.join(root, "scripts", "act1_conclusion.gd")

if not os.path.isfile(trigger_tscn):
    errors.append(f"Missing scene: {trigger_tscn}")
if not os.path.isfile(act1_gd):
    errors.append(f"Missing script: {act1_gd}")

if os.path.isfile(trigger_tscn):
    text = open(trigger_tscn, encoding="utf-8").read()
    if '[node name="Act1ConclusionTrigger" type="Area2D"]' not in text:
        errors.append("act1_conclusion_trigger.tscn: root node must be Area2D named Act1ConclusionTrigger")
    if "CollisionShape2D" not in text:
        errors.append("act1_conclusion_trigger.tscn: must include CollisionShape2D")

if os.path.isfile(act1_gd):
    g = open(act1_gd, encoding="utf-8").read()
    for needle, msg in (
        ("DialogueManager.show_dialogue", "act1_conclusion.gd must call DialogueManager.show_dialogue"),
        ("QuestManager.complete_objective", "act1_conclusion.gd must call QuestManager.complete_objective"),
        ("'merchants_delivery'", "act1_conclusion.gd must reference merchants_delivery"),
        ("QuestManager.start_quest", "act1_conclusion.gd must call QuestManager.start_quest"),
        ("'the_assessment'", "act1_conclusion.gd must reference the_assessment"),
        ("DialogueManager.set_flag", "act1_conclusion.gd must call DialogueManager.set_flag"),
        ("'act1_complete'", "act1_conclusion.gd must set act1_complete flag"),
        ("body_entered.connect", "act1_conclusion.gd must connect body_entered in _ready"),
        ("_triggered", "act1_conclusion.gd must use a one-shot guard"),
    ):
        if needle not in g:
            errors.append(msg)

if errors:
    for e in errors:
        print("FAIL:", e)
    sys.exit(1)

print("Bootstrap checks passed (spec 1246 will add full validation)")
sys.exit(0)
