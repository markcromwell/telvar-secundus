#!/usr/bin/env python3
"""Structural validation for the Act 5 Myramar office meeting."""

from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent

MYRAMAR_DIALOGUE = REPO_ROOT / "assets" / "dialogue" / "myramar.json"
MYRAMAR_PORTRAIT = REPO_ROOT / "assets" / "portraits" / "myramar.png"
MYRAMAR_NPC_SCENE = REPO_ROOT / "scenes" / "npcs" / "myramar.tscn"
MYRAMAR_NPC_SCRIPT = REPO_ROOT / "scripts" / "npcs" / "myramar.gd"
MYRAMAR_OFFICE_SCENE = REPO_ROOT / "scenes" / "myramar_office.tscn"

EXPECTED_QUOTE = (
    "You are ready now, Telvar. Take the Sealed Wing Key and meet what waits "
    "beyond the academy doors."
)

errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def require_file(label: str, path: Path) -> bool:
    if not path.is_file():
        fail(f"{label} missing: {path.relative_to(REPO_ROOT)}")
        return False
    return True


def read_text(label: str, path: Path) -> str:
    if not require_file(label, path):
        return ""
    return path.read_text(encoding="utf-8")


def validate_dialogue() -> None:
    if not require_file("Myramar dialogue", MYRAMAR_DIALOGUE):
        return

    try:
        dialogue = json.loads(MYRAMAR_DIALOGUE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"Myramar dialogue is not valid JSON: {exc}")
        return

    if not isinstance(dialogue, list):
        fail("Myramar dialogue must be a JSON array")
        return

    by_id = {}
    for index, node in enumerate(dialogue):
        if not isinstance(node, dict):
            fail(f"Myramar dialogue node {index} must be an object")
            continue
        node_id = node.get("id")
        if not isinstance(node_id, str) or not node_id:
            fail(f"Myramar dialogue node {index} must have a non-empty id")
            continue
        by_id[node_id] = node
        for key in ("speaker", "text"):
            if not isinstance(node.get(key), str) or not node[key]:
                fail(f"Myramar dialogue node {node_id!r} must have {key}")

    start = by_id.get("start")
    if not start:
        fail("Myramar dialogue must include a start node")
        return

    if start.get("speaker") != "Myramar":
        fail('Myramar start dialogue speaker must be "Myramar"')
    if start.get("text") != EXPECTED_QUOTE:
        fail("Myramar start dialogue does not contain the exact readiness quote")
    if start.get("next") != "award_sealed_wing_key":
        fail("Myramar start dialogue must advance to award_sealed_wing_key")

    award = by_id.get("award_sealed_wing_key")
    if not award:
        fail("Myramar dialogue must include award_sealed_wing_key node")
    elif "Sealed Wing Key" not in award.get("text", ""):
        fail("Myramar award node must mention Sealed Wing Key")


def validate_npc_scene() -> None:
    text = read_text("Myramar NPC scene", MYRAMAR_NPC_SCENE)
    if not text:
        return

    expected_snippets = (
        '[gd_scene',
        '[ext_resource type="Script" path="res://scripts/npcs/myramar.gd"',
        '[ext_resource type="Texture2D" path="res://assets/portraits/myramar.png"',
        '[node name="Myramar" type="CharacterBody2D"]',
        'script = ExtResource("1_script")',
        '[node name="AnimatedSprite2D" type="AnimatedSprite2D" parent="."]',
        '[node name="InteractionZone" type="Area2D" parent="."]',
        '[node name="CollisionShape2D" type="CollisionShape2D" parent="InteractionZone"]',
    )
    for snippet in expected_snippets:
        if snippet not in text:
            fail(f"Myramar NPC scene missing expected structure: {snippet}")


def validate_office_scene() -> None:
    text = read_text("Myramar office scene", MYRAMAR_OFFICE_SCENE)
    if not text:
        return

    expected_snippets = (
        '[gd_scene',
        '[node name="MyramarOffice" type="Node2D"]',
        '[ext_resource type="PackedScene" path="res://scenes/npcs/myramar.tscn"',
        '[ext_resource type="Texture2D" path="res://assets/tilesets/lpc_terrain.png"',
        '[node name="TileMap" type="TileMap" parent="."]',
        'texture_region_size = Vector2i(16, 16)',
        'tile_size = Vector2i(16, 16)',
        'scale = Vector2(2, 2)',
        'texture_filter = 0',
        '[node name="Myramar" parent="." instance=ExtResource("1_npc")]',
    )
    for snippet in expected_snippets:
        if snippet not in text:
            fail(f"Myramar office scene missing expected structure: {snippet}")


def validate_trigger_script() -> None:
    text = read_text("Myramar NPC script", MYRAMAR_NPC_SCRIPT)
    if not text:
        return

    expected_snippets = (
        'const ACT3_COMPLETE_FLAG := "act_3_complete"',
        'const DIALOGUE_NPC_ID := "myramar"',
        'const DIALOGUE_JSON_PATH := "res://assets/dialogue/myramar.json"',
        "DialogueManager.get_flag(ACT3_COMPLETE_FLAG, false)",
        "DialogueManager.show_dialogue(DIALOGUE_NPC_ID, _dialogue)",
        "dialogue_finished.connect(_on_dialogue_finished)",
    )
    for snippet in expected_snippets:
        if snippet not in text:
            fail(f"Myramar trigger script missing expected wiring: {snippet}")

    for forbidden_flag in ("act_1_complete", "act_2_complete", "act_4_complete"):
        if forbidden_flag in text:
            fail(f"Myramar trigger script must not depend on {forbidden_flag}")


def main() -> int:
    require_file("Myramar portrait", MYRAMAR_PORTRAIT)
    validate_dialogue()
    validate_npc_scene()
    validate_office_scene()
    validate_trigger_script()

    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1

    print("Act 5 Myramar validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
