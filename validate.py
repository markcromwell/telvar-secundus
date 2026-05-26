#!/usr/bin/env python3
"""Structural validation for the Myramar assessment scene and rewards."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def _read_text(path: str, errors: list[str]) -> str:
    full_path = ROOT / path
    if not full_path.is_file():
        errors.append(f"Missing required file: {path}")
        return ""
    return full_path.read_text(encoding="utf-8")


def _read_json(path: str, errors: list[str]):
    text = _read_text(path, errors)
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        errors.append(f"{path} is not valid JSON: {exc}")
        return None


def _require_text(path: str, text: str, needle: str, errors: list[str]) -> None:
    if needle not in text:
        errors.append(f"{path} must contain {needle!r}")


def _validate_myramar_dialogue(errors: list[str]) -> None:
    path = "assets/dialogue/myramar.json"
    dialogue = _read_json(path, errors)
    if not isinstance(dialogue, list):
        errors.append(f"{path} root must be a JSON array")
        return

    nodes = {node.get("id"): node for node in dialogue if isinstance(node, dict)}
    for node_id in ("start", "assessment", "success"):
        if node_id not in nodes:
            errors.append(f"{path} must include dialogue id {node_id!r}")

    choices = nodes.get("assessment", {}).get("choices")
    if not isinstance(choices, list) or len(choices) != 3:
        errors.append(f"{path} assessment node must show exactly three choices")
    elif not any(choice.get("next") == "success" for choice in choices if isinstance(choice, dict)):
        errors.append(f"{path} one assessment choice must route to success")

    success = nodes.get("success", {})
    flag = success.get("set_flag", {}) if isinstance(success, dict) else {}
    if flag.get("myramar_assessment_complete") is not True:
        errors.append(f"{path} success node must set myramar_assessment_complete")
    if "wizard_ranks" not in success.get("unlock_lore", []):
        errors.append(f"{path} success node must unlock wizard_ranks lore")
    if "rutilus_band" not in success.get("add_inventory", []):
        errors.append(f"{path} success node must award rutilus_band")
    if not success.get("show_ceremony_card"):
        errors.append(f"{path} success node must request the ceremony card")


def _validate_ceremony_card(errors: list[str]) -> None:
    path = "scenes/ceremony_card.tscn"
    text = _read_text(path, errors)
    if not text:
        return

    _require_text(path, text, '[node name="CeremonyCard" type="Control"]', errors)
    _require_text(path, text, 'type="PanelContainer"', errors)
    _require_text(path, text, "Ceremony of the Band", errors)
    _require_text(path, text, "Veneficturis", errors)


def _validate_myramar_script(errors: list[str]) -> None:
    path = "scripts/myramar.gd"
    text = _read_text(path, errors)
    if not text:
        return

    for required in (
        'const NPC_ID := "myramar"',
        'const DIALOGUE_PATH := "res://assets/dialogue/myramar.json"',
        'const SUCCESS_FLAG := "myramar_assessment_complete"',
        'const LORE_ON_SUCCESS := "wizard_ranks"',
        'const BAND_ITEM_ID := "rutilus_band"',
        'preload("res://scenes/ceremony_card.tscn")',
        "DialogueManager.show_dialogue",
        "DialogueManager.get_flag",
        "LoreManager.unlock",
        "InventoryManager.add_item",
    ):
        _require_text(path, text, required, errors)

    if not re.search(r"func\s+_update_sprite_for_band\s*\([^)]*\).*?sprite\.texture\s*=", text, re.S):
        errors.append(f"{path} must update the Myramar/Telvar sprite texture after band award")
    if not re.search(r"func\s+_spawn_ceremony_card\s*\([^)]*\).*?instantiate\s*\(", text, re.S):
        errors.append(f"{path} must instantiate the ceremony card on success")


def _validate_lore_entries(errors: list[str]) -> None:
    path = "assets/lore/lore_entries.json"
    text = _read_text(path, errors)
    if not text:
        return

    for required in ("wizard_ranks", "Wizard Ranks", "Red", "Rutilus", "Veneficturis"):
        _require_text(path, text, required, errors)

    lore = _read_json(path, errors)
    if not isinstance(lore, list):
        errors.append(f"{path} root must be a JSON array")
        return

    wizard_ranks = [entry for entry in lore if isinstance(entry, dict) and entry.get("id") == "wizard_ranks"]
    if not wizard_ranks:
        errors.append(f"{path} must include wizard_ranks entry")
        return
    entry = wizard_ranks[0]
    if not entry.get("title"):
        errors.append(f"{path} wizard_ranks entry must include a title")
    if "Rutilus" not in entry.get("text", ""):
        errors.append(f"{path} wizard_ranks text must describe Rutilus")


def main() -> int:
    errors: list[str] = []
    _validate_myramar_dialogue(errors)
    _validate_ceremony_card(errors)
    _validate_myramar_script(errors)
    _validate_lore_entries(errors)

    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1

    print("Myramar assessment validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
