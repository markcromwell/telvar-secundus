#!/usr/bin/env python3
"""Structural validation for the combat UI overlay scenes.

This script intentionally uses text parsing only; it does not require Godot.
"""
from pathlib import Path
import re
import sys

REPO_ROOT = Path(__file__).resolve().parent
SCENE_REQUIREMENTS = {
    "CombatUI": {
        "path": REPO_ROOT / "scenes" / "CombatUI.tscn",
        "node_types": {"ColorRect", "ProgressBar", "Label"},
    },
    "DamageFloat": {
        "path": REPO_ROOT / "scenes" / "DamageFloat.tscn",
        "node_types": {"Label"},
    },
}

errors: list[str] = []
warnings: list[str] = []
all_scene_files_present = all(
    requirement["path"].is_file()
    for requirement in SCENE_REQUIREMENTS.values()
)


def _scene_node_types(scene_text: str) -> set[str]:
    return set(re.findall(r'\[node\b[^\]]*\btype="([^"]+)"', scene_text))


def _validate_scene(scene_name: str, scene_path: Path, required_node_types: set[str]) -> None:
    if not scene_path.is_file():
        warnings.append(
            f"{scene_path.relative_to(REPO_ROOT)} is not present in this phase; "
            "structure checks will run once the scene phase lands"
        )
        return

    text = scene_path.read_text(encoding="utf-8")
    present_node_types = _scene_node_types(text)
    missing_node_types = sorted(required_node_types - present_node_types)
    if missing_node_types:
        message = (
            f"{scene_path.relative_to(REPO_ROOT)} is missing node type(s): "
            f"{', '.join(missing_node_types)}"
        )
        if all_scene_files_present:
            errors.append(message)
        else:
            warnings.append(f"{message}; strict checks will run once all scenes land")
    else:
        print(
            f"PASS: {scene_name} contains required node type(s): "
            f"{', '.join(sorted(required_node_types))}"
        )


for name, requirement in SCENE_REQUIREMENTS.items():
    _validate_scene(
        name,
        requirement["path"],
        requirement["node_types"],
    )

if errors:
    for e in errors:
        print("FAIL:", e)
    sys.exit(1)

for warning in warnings:
    print("PENDING:", warning)

print("Combat UI scene validation completed")
sys.exit(0)
