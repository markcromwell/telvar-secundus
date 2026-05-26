#!/usr/bin/env python3
"""Structural validation for Orsson Emporium interior (Godot .tscn text, dialogue JSON)."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SCENE_REL = Path("scenes/interiors/orsson_emporium.tscn")
DIALOGUE_SABATHA = Path("assets/dialogue/sabatha.json")
DIALOGUE_ORSSON = Path("assets/dialogue/orsson.json")


def _area2d_node_blocks(scene_text: str) -> list[tuple[str, str]]:
    """Return (node_name, block_text) for each Area2D node section in the scene file."""
    parts = re.split(r"(?=\[node )", scene_text)
    out: list[tuple[str, str]] = []
    for part in parts:
        if not part.startswith("[node "):
            continue
        m = re.match(r'\[node name="([^"]+)" type="Area2D"', part)
        if m:
            out.append((m.group(1), part))
    return out


def validate(repo_root: Path) -> list[str]:
    """Return a list of human-readable error strings; empty means success."""
    errors: list[str] = []
    scene_path = repo_root / SCENE_REL

    if not scene_path.is_file():
        errors.append(f"scenes/interiors/orsson_emporium.tscn is absent (expected at {SCENE_REL.as_posix()})")
        return errors

    text = scene_path.read_text(encoding="utf-8")

    if "ExitDoor" not in text:
        errors.append("orsson_emporium.tscn must include the string 'ExitDoor' (exit trigger Area2D)")

    if not re.search(r'\[node name="TileMap" type="TileMap"', text):
        errors.append("orsson_emporium.tscn must contain a TileMap node")

    if not re.search(r'\[node name="Sabatha"', text):
        errors.append('orsson_emporium.tscn must contain a node named Sabatha')

    if not re.search(r'\[node name="Orsson"', text):
        errors.append('orsson_emporium.tscn must contain a node named Orsson')

    for rel in (DIALOGUE_SABATHA, DIALOGUE_ORSSON):
        path = repo_root / rel
        if not path.is_file():
            errors.append(f"Dialogue file missing: {rel.as_posix()}")
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"Invalid JSON in {rel.as_posix()}: {exc}")
            continue
        if not isinstance(data, list) or len(data) < 2:
            errors.append(f"{rel.as_posix()} must define at least two dialogue nodes (JSON array with length >= 2)")

    inspectable_ok = 0
    for name, block in _area2d_node_blocks(text):
        if name == "ExitDoor":
            continue
        if not re.search(r"^\s*inspect_text\s*=", block, re.MULTILINE):
            continue
        shape_header = rf'\[node name="CollisionShape2D" type="CollisionShape2D" parent="{re.escape(name)}"\]'
        if not re.search(shape_header, text):
            errors.append(f'Inspectable Area2D "{name}" must have a CollisionShape2D child (parent="{name}")')
            continue
        inspectable_ok += 1

    if inspectable_ok < 2:
        errors.append(
            "orsson_emporium.tscn must define at least two Area2D inspectables (not ExitDoor) "
            "each with an inspect_text export property"
        )

    return errors


def main() -> None:
    repo_root = Path(__file__).resolve().parent
    errors = validate(repo_root)
    if errors:
        for msg in errors:
            print(f"FAIL: {msg}")
        sys.exit(1)
    print("Validation passed (Orsson Emporium interior structure).")
    sys.exit(0)


if __name__ == "__main__":
    main()
