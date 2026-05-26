#!/usr/bin/env python3
"""Structural validation for the Telvar Secundus Godot project (no Godot binary).

Exits 0 when all checks pass, 1 otherwise. Intended for CI and worker pipelines.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# Explicit paths required by spec / acceptance criteria
ROOKERY_SCENE = "scenes/RookeryTavern.tscn"
DIALOGUE_MANAGER = "scripts/DialogueManager.gd"
DIALOGUE_BARTENDER = "assets/dialogue/bartender.json"
DIALOGUE_HOODED_1 = "assets/dialogue/hooded_figure_1.json"
DIALOGUE_HOODED_2 = "assets/dialogue/hooded_figure_2.json"
LPC_TERRAIN = "assets/tilesets/lpc_terrain.png"
STONE_FOOTSTEP = "assets/audio/sfx/stone_footstep.wav"

DIALOGUE_JSONS = (
    DIALOGUE_BARTENDER,
    DIALOGUE_HOODED_1,
    DIALOGUE_HOODED_2,
)

# KNOWN_BAD: invalid / typo-prone GDScript shapes (text scan, not a full parser)
KNOWN_BAD_GD_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\bvar\s*="), "dangling var = (missing identifier before =)"),
    (re.compile(r"\bfunc\s*\(\s*\)\s*(?!:)"), "anonymous func() without trailing ':'"),
)

REPO_ROOT = Path(__file__).resolve().parent


def check(label: str, ok: bool, detail: str = "") -> bool:
    if ok:
        print(f"PASS: {label}")
        return True
    msg = f"FAIL: {label}"
    if detail:
        msg += f" — {detail}"
    print(msg)
    return False


def check_file(
    rel_path: str,
    must_contain: tuple[str, ...] = (),
    *,
    is_binary: bool = False,
) -> bool:
    path = REPO_ROOT / rel_path
    if not path.is_file():
        return check(f"file exists: {rel_path}", False, "missing or not a file")
    if is_binary:
        return check(f"file exists: {rel_path}", True)
    text = path.read_text(encoding="utf-8")
    for needle in must_contain:
        if needle not in text:
            return check(f"{rel_path} contains {needle!r}", False, "substring not found")
    return check(f"file exists: {rel_path}", True)


def check_dir(rel_path: str) -> bool:
    path = REPO_ROOT / rel_path
    return check(f"directory exists: {rel_path}", path.is_dir(), "missing or not a directory")


def _autoload_section_has_dialogue_manager(text: str) -> bool:
    in_autoload = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "[autoload]":
            in_autoload = True
            continue
        if in_autoload and stripped.startswith("[") and stripped.endswith("]"):
            break
        if in_autoload and "DialogueManager" in line:
            return True
    return False


def _validate_dialogue_json(rel_path: str) -> bool:
    path = REPO_ROOT / rel_path
    if not path.is_file():
        return check(f"dialogue JSON: {rel_path}", False, "missing file")
    try:
        nodes = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return check(f"dialogue JSON parses: {rel_path}", False, str(exc))

    if not isinstance(nodes, list):
        return check(f"dialogue JSON is a list: {rel_path}", False, f"got {type(nodes).__name__}")
    if len(nodes) < 2:
        return check(f"dialogue JSON len(nodes) >= 2: {rel_path}", False, f"len={len(nodes)}")

    required_keys = ("id", "text", "speaker", "next")
    for i, node in enumerate(nodes):
        if not isinstance(node, dict):
            return check(f"dialogue node {i} is object: {rel_path}", False, f"got {type(node).__name__}")
        missing = [k for k in required_keys if k not in node]
        if missing:
            return check(
                f"dialogue node {i} keys in {rel_path}",
                False,
                f"missing {missing!r}",
            )
    return check(f"dialogue JSON structure: {rel_path}", True)


def _iter_gd_sources() -> list[Path]:
    out: list[Path] = []
    for path in REPO_ROOT.rglob("*.gd"):
        if ".git" in path.parts or ".godot" in path.parts:
            continue
        if "addons" in path.parts:
            continue
        out.append(path)
    out.sort()
    return out


def _scan_known_bad_gdscript() -> bool:
    bad_hits: list[str] = []
    for path in _iter_gd_sources():
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(REPO_ROOT).as_posix()
        for pattern, desc in KNOWN_BAD_GD_PATTERNS:
            if re.search(pattern, text):
                bad_hits.append(f"{rel}: {desc} (pattern {pattern.pattern!r})")
    if bad_hits:
        print("FAIL: GDScript KNOWN_BAD pattern scan")
        for hit in bad_hits:
            print(f"  - {hit}")
        return False
    print("PASS: GDScript KNOWN_BAD pattern scan (no hits)")
    return True


def main() -> int:
    all_ok = True

    all_ok &= check_file("project.godot")
    all_ok &= check_dir("scenes")
    all_ok &= check_dir("scripts")
    all_ok &= check_dir("assets")

    if all_ok:
        pg_text = (REPO_ROOT / "project.godot").read_text(encoding="utf-8")
        all_ok &= check(
            "project.godot [autoload] mentions DialogueManager",
            _autoload_section_has_dialogue_manager(pg_text),
        )

    all_ok &= check_file(
        ROOKERY_SCENE,
        ("TileMap", "ExitDoor", "HoodedFigure1", "HoodedFigure2"),
    )
    all_ok &= check_file(
        DIALOGUE_MANAGER,
        ("show_dialogue", "set_flag", "get_flag"),
    )
    all_ok &= check_file(LPC_TERRAIN, is_binary=True)
    all_ok &= check_file(STONE_FOOTSTEP, is_binary=True)

    for dialogue_rel in DIALOGUE_JSONS:
        all_ok &= _validate_dialogue_json(dialogue_rel)

    all_ok &= _scan_known_bad_gdscript()

    print()
    if all_ok:
        print("Summary: all checks passed.")
        return 0
    print("Summary: one or more checks failed.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
