#!/usr/bin/env python3
"""
TELVAR-RPG structural validation (no Godot runtime).

Paladin Temple checks (spec #1262 / phase 2541) cover interior layout,
dialogue/lore JSON, and overworld exit wiring.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent

PALADIN_TEMPLE = REPO_ROOT / "scenes/interiors/paladin_temple.tscn"
PALADIN_TEMPLE_PLAYABLE = REPO_ROOT / "scenes/interiors/paladin_temple_playable.tscn"
SIR_VALINS_DIALOGUE = REPO_ROOT / "assets/dialogue/sir_valins.json"
ORDER_LORE = REPO_ROOT / "assets/lore/order_lore.json"
EXIT_DOOR_SCRIPT = REPO_ROOT / "scripts/interior/exit_door_area.gd"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _parse_ext_resources(tscn: str) -> dict[str, str]:
    """Map ExtResource id -> res:// path."""
    out: dict[str, str] = {}
    for block in re.finditer(r"\[ext_resource[^\]]+\]", tscn):
        b = block.group(0)
        pm = re.search(r'path="(res://[^"]+)"', b)
        im = re.search(r'id="([^"]+)"', b)
        if pm and im:
            out[im.group(1)] = pm.group(1)
    return out


def _resolve_res_path(res_path: str) -> Path:
    rel = res_path.removeprefix("res://")
    return REPO_ROOT / rel


def validate_paladin_temple(errors: list[str]) -> None:
    """Phase 2541: Paladin Temple acceptance (text / JSON parsing only)."""
    if not PALADIN_TEMPLE.is_file():
        errors.append(f"PaladinTemple: missing scene {PALADIN_TEMPLE}")
        return

    interior = _read_text(PALADIN_TEMPLE)

    # 1) TileMap exactly 20x30 (regex on resource text per spec).
    tilemap_block = re.search(
        r'\[node name="TileMap"[^\]]*\][^\[]*editor_description = "([^"]*)"',
        interior,
        re.DOTALL,
    )
    if not tilemap_block:
        errors.append('PaladinTemple: TileMap node or editor_description not found')
    else:
        desc = tilemap_block.group(1)
        if not re.search(r"\b20\s*x\s*30\b", desc, re.IGNORECASE):
            errors.append(
                "PaladinTemple: TileMap editor_description must document 20x30 tile extent"
            )

    # 2) Eight pew nodes (four per side).
    sides = ("PewLeft", "PewRight")
    for i in range(1, 5):
        for side in sides:
            needle = f'name="{side}{i}"'
            if needle not in interior:
                errors.append(f"PaladinTemple: missing pew node {side}{i}")

    # Spec: long nave + golden cross altar (structural presence in .tscn text).
    if "nave" not in interior.lower():
        errors.append("PaladinTemple: nave not referenced in interior scene text")
    if not re.search(r'\[node name="AtenAltar"', interior):
        errors.append('PaladinTemple: missing AtenAltar marker (golden cross altar)')
    elif not re.search(r"golden", interior, re.IGNORECASE):
        errors.append("PaladinTemple: golden cross / golden altar not referenced in scene text")

    # 3) Sir Valins dialogue graph.
    if not SIR_VALINS_DIALOGUE.is_file():
        errors.append(f"PaladinTemple: missing dialogue {SIR_VALINS_DIALOGUE}")
    else:
        try:
            data = json.loads(_read_text(SIR_VALINS_DIALOGUE))
        except json.JSONDecodeError as exc:
            errors.append(f"PaladinTemple: sir_valins.json invalid JSON: {exc}")
        else:
            nodes = data.get("nodes")
            if not isinstance(nodes, list) or len(nodes) < 2:
                errors.append(
                    "PaladinTemple: sir_valins.json must have a 'nodes' list with len >= 2"
                )

    # 4) Order lore — at least one entry with non-empty body.
    if not ORDER_LORE.is_file():
        errors.append(f"PaladinTemple: missing lore file {ORDER_LORE}")
    else:
        try:
            lore = json.loads(_read_text(ORDER_LORE))
        except json.JSONDecodeError as exc:
            errors.append(f"PaladinTemple: order_lore.json invalid JSON: {exc}")
        else:
            if not isinstance(lore, list):
                errors.append("PaladinTemple: order_lore.json must be a JSON array")
            elif not any(
                isinstance(item, dict)
                and isinstance(item.get("body"), str)
                and item["body"].strip()
                for item in lore
            ):
                errors.append(
                    "PaladinTemple: order_lore.json needs at least one object with non-empty 'body'"
                )

    # 5) Exit / overworld: prefer literals in interior .tscn; otherwise playable
    #    Area2D ExitDoor + exit_door_area.gd (signal wiring is in GDScript, not [connection]).
    has_interior_targets = (
        "secundus" in interior.lower() and "paladin_temple_exit" in interior
    )
    if has_interior_targets:
        return

    if not PALADIN_TEMPLE_PLAYABLE.is_file():
        errors.append(
            f"PaladinTemple: exit targets not in interior and playable missing: {PALADIN_TEMPLE_PLAYABLE}"
        )
        return

    playable = _read_text(PALADIN_TEMPLE_PLAYABLE)
    if 'name="ExitDoor" type="Area2D"' not in playable:
        errors.append(
            "PaladinTemple: exit Area2D (ExitDoor) not found in paladin_temple_playable.tscn "
            "and overworld targets not present in paladin_temple.tscn"
        )
        return

    ext_by_id = _parse_ext_resources(playable)
    door_hdr = re.search(
        r'\[node name="ExitDoor" type="Area2D"[^\]]*\]',
        playable,
    )
    if not door_hdr:
        errors.append("PaladinTemple: ExitDoor header parse failed")
        return
    tail = playable[door_hdr.end() : door_hdr.end() + 400]
    sm = re.search(r'script = ExtResource\("([^"]+)"\)', tail)
    if not sm:
        errors.append("PaladinTemple: ExitDoor Area2D has no script ExtResource")
        return
    res_path = ext_by_id.get(sm.group(1))
    if not res_path:
        errors.append(f"PaladinTemple: unknown ExtResource id {sm.group(1)!r} on ExitDoor")
        return
    script_path = _resolve_res_path(res_path)
    if not script_path.is_file():
        errors.append(f"PaladinTemple: ExitDoor script missing on disk: {script_path}")
        return
    script_src = _read_text(script_path)
    if "secundus" not in script_src.lower():
        errors.append(
            "PaladinTemple: exit handler must target a Secundus overworld scene path "
            f"(checked {script_path.name})"
        )
    if "paladin_temple_exit" not in script_src:
        errors.append(
            "PaladinTemple: exit handler must use spawn marker paladin_temple_exit "
            f"(checked {script_path.name})"
        )


def main() -> int:
    errors: list[str] = []
    validate_paladin_temple(errors)

    if errors:
        for e in errors:
            print("FAIL:", e)
        return 1

    print("OK: Paladin Temple validation passed (validate.py phase 2541)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
