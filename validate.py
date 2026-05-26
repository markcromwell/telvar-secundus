#!/usr/bin/env python3
"""Structural validation for Telvar Secundus (Godot 4.x) — no third-party deps."""

from __future__ import annotations

import json
import re
import sys
from collections.abc import Callable
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent

CHECKS: list[tuple[str, Callable[[], str | None]]] = []


def check(name: str):
    def deco(fn: Callable[[], str | None]):
        CHECKS.append((name, fn))
        return fn

    return deco


@check("bedroom_gd")
def _bedroom_gd() -> str | None:
    p = REPO_ROOT / "scenes/bedroom/Bedroom.gd"
    if not p.is_file():
        return f"missing {p.relative_to(REPO_ROOT)}"
    return None


@check("bedroom_gd_extends_ready")
def _bedroom_gd_extends_ready() -> str | None:
    t = (REPO_ROOT / "scenes/bedroom/Bedroom.gd").read_text(encoding="utf-8")
    if "extends Node2D" not in t:
        return "Bedroom.gd must extend Node2D"
    if "func _ready" not in t:
        return "Bedroom.gd must define _ready"
    return None


@check("bedroom_gd_spawn_can_move")
def _bedroom_gd_spawn_can_move() -> str | None:
    t = (REPO_ROOT / "scenes/bedroom/Bedroom.gd").read_text(encoding="utf-8")
    if "$SpawnPoint" not in t and "$\"SpawnPoint\"" not in t:
        return "Bedroom.gd must reference SpawnPoint"
    if "can_move" not in t:
        return "Bedroom.gd must reference can_move"
    return None


@check("bedroom_tscn_file")
def _bedroom_tscn_file() -> str | None:
    p = REPO_ROOT / "scenes/bedroom/Bedroom.tscn"
    if not p.is_file():
        return "missing Bedroom.tscn"
    return None


@check("bedroom_tilemap")
def _bedroom_tilemap() -> str | None:
    t = (REPO_ROOT / "scenes/bedroom/Bedroom.tscn").read_text(encoding="utf-8")
    if "[node name=\"TileMap\"" not in t:
        return "TileMap node not found in Bedroom.tscn"
    return None


@check("bedroom_spawnpoint")
def _bedroom_spawnpoint() -> str | None:
    t = (REPO_ROOT / "scenes/bedroom/Bedroom.tscn").read_text(encoding="utf-8")
    if "[node name=\"SpawnPoint\"" not in t:
        return "SpawnPoint node not found in Bedroom.tscn"
    return None


@check("bedroom_script_ext")
def _bedroom_script_ext() -> str | None:
    t = (REPO_ROOT / "scenes/bedroom/Bedroom.tscn").read_text(encoding="utf-8")
    if "script = ExtResource(" not in t:
        return "Bedroom root must set script = ExtResource(...)"
    if "[node name=\"Bedroom\"" not in t:
        return "Bedroom node block missing"
    # Ensure script appears in Bedroom node section (first node block named Bedroom)
    m = re.search(
        r'\[node name="Bedroom"[^\]]*\][^\[]*script = ExtResource\(',
        t,
        re.DOTALL,
    )
    if not m:
        return "Bedroom node must have script = ExtResource(...) near its header"
    return None


@check("player_character_body")
def _player_character_body() -> str | None:
    p = REPO_ROOT / "scenes/player/Player.tscn"
    if not p.is_file():
        return "missing Player.tscn"
    return None


@check("player_character_body2d")
def _player_character_body2d() -> str | None:
    t = (REPO_ROOT / "scenes/player/Player.tscn").read_text(encoding="utf-8")
    if "type=\"CharacterBody2D\"" not in t:
        return "Player.tscn must use CharacterBody2D root"
    return None


@check("player_gd_movement")
def _player_gd_movement() -> str | None:
    p = REPO_ROOT / "scripts/player/Player.gd"
    if not p.is_file():
        return "missing Player.gd"
    t = p.read_text(encoding="utf-8")
    if "can_move" not in t or "move_and_slide" not in t:
        return "Player.gd must implement can_move and move_and_slide"
    return None


@check("sabatha_dialogue_file")
def _sabatha_dialogue_file() -> str | None:
    p = REPO_ROOT / "assets/dialogue/sabatha.json"
    if not p.is_file():
        return "missing sabatha.json"
    blob = p.read_text(encoding="utf-8")
    if '"id": "start"' not in blob and '"id":"start"' not in blob:
        return 'sabatha.json must contain an entry with id "start"'
    try:
        data = json.loads(blob)
    except json.JSONDecodeError as e:
        return f"invalid JSON: {e}"
    if not isinstance(data, list) or not data:
        return "sabatha.json must be a non-empty array"
    return None


@check("project_godot")
def _project_godot() -> str | None:
    p = REPO_ROOT / "project.godot"
    if not p.is_file():
        return "missing project.godot"
    return None


@check("project_autoload_dialogue")
def _project_autoload_dialogue() -> str | None:
    t = (REPO_ROOT / "project.godot").read_text(encoding="utf-8")
    if "DialogueManager=" not in t:
        return "project.godot must autoload DialogueManager"
    if "scripts/dialogue/DialogueManager.gd" not in t:
        return "DialogueManager autoload must point to DialogueManager.gd"
    return None


@check("intro_overlay_tscn")
def _intro_overlay_tscn() -> str | None:
    p = REPO_ROOT / "scenes/ui/IntroOverlay.tscn"
    if not p.is_file():
        return "missing IntroOverlay.tscn"
    return None


@check("dialogue_manager_gd")
def _dialogue_manager_gd() -> str | None:
    p = REPO_ROOT / "scripts/dialogue/DialogueManager.gd"
    if not p.is_file():
        return "missing DialogueManager.gd"
    return None


@check("dialogue_manager_show_dialogue")
def _dialogue_manager_show_dialogue() -> str | None:
    t = (REPO_ROOT / "scripts/dialogue/DialogueManager.gd").read_text(encoding="utf-8")
    if "func show_dialogue" not in t:
        return "DialogueManager.gd must define show_dialogue"
    return None


def main() -> int:
    if len(CHECKS) < 8:
        print("FAIL: internal error — fewer than 8 checks registered")
        return 1

    failed = 0
    for name, fn in CHECKS:
        err: str | None
        try:
            err = fn()
        except OSError as e:
            err = str(e)
        if err:
            print(f"[{name}] FAIL ({err})")
            failed += 1
        else:
            rel = ""
            if name == "bedroom_gd":
                rel = f" ({REPO_ROOT / 'scenes/bedroom/Bedroom.gd'})"
            elif name == "player_character_body":
                rel = f" ({REPO_ROOT / 'scenes/player/Player.tscn'})"
            elif name == "project_godot":
                rel = f" ({REPO_ROOT / 'project.godot'})"
            elif name == "intro_overlay_tscn":
                rel = f" ({REPO_ROOT / 'scenes/ui/IntroOverlay.tscn'})"
            elif name == "dialogue_manager_gd":
                rel = f" ({REPO_ROOT / 'scripts/dialogue/DialogueManager.gd'})"
            print(f"[{name}] PASS{rel}")

    if failed:
        print(f"\nvalidate: {failed} check(s) failed")
        return 1
    print("\nvalidate: all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
