#!/usr/bin/env python3
"""
TELVAR-RPG structural validation (no Godot binary).

Phase 2743: AudioManager scene graph, CombatManager → AudioManager calls,
and lightweight HTML5 / asset-size guards for CI.
"""

from __future__ import annotations

import os
import sys

# Web export guidance: total shipped resources under this budget (bytes).
_MAX_SHIPPED_ASSET_BYTES = 5 * 1024 * 1024


def _repo_root() -> str:
    return os.path.dirname(os.path.abspath(__file__))


def _read_text(path: str) -> str:
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def _sum_dir_bytes(root: str) -> int:
    total = 0
    for dirpath, _dirnames, filenames in os.walk(root):
        for name in filenames:
            fp = os.path.join(dirpath, name)
            try:
                total += os.path.getsize(fp)
            except OSError:
                continue
    return total


def _autoload_key_order(project_text: str) -> list[str]:
    """Return autoload keys in file order (AudioManager before CombatManager, etc.)."""
    order: list[str] = []
    in_autoload = False
    for line in project_text.splitlines():
        s = line.strip()
        if s == "[autoload]":
            in_autoload = True
            continue
        if in_autoload:
            if s.startswith("[") and s.endswith("]"):
                break
            if "=" in s and not s.startswith(";"):
                order.append(s.split("=", 1)[0].strip())
    return order


def main() -> int:
    errors: list[str] = []
    root = _repo_root()

    audio_gd = os.path.join(root, "autoload", "AudioManager.gd")
    audio_tscn = os.path.join(root, "autoload", "AudioManager.tscn")
    combat_gd = os.path.join(root, "autoload", "CombatManager.gd")
    project = os.path.join(root, "project.godot")
    export_presets = os.path.join(root, "export_presets.cfg")

    if not os.path.isfile(audio_gd):
        errors.append("missing autoload/AudioManager.gd")
    if not os.path.isfile(audio_tscn):
        errors.append("missing autoload/AudioManager.tscn")
    if not os.path.isfile(combat_gd):
        errors.append("missing autoload/CombatManager.gd")

    if os.path.isfile(project):
        pg = _read_text(project)
        if "[autoload]" not in pg or "AudioManager" not in pg:
            errors.append("project.godot must register AudioManager in [autoload]")
        if "res://autoload/AudioManager.tscn" not in pg:
            errors.append("AudioManager autoload path must be res://autoload/AudioManager.tscn")
        if "CombatManager" not in pg:
            errors.append("project.godot must register CombatManager in [autoload]")
        if "res://autoload/CombatManager.tscn" not in pg:
            errors.append("CombatManager autoload path must be res://autoload/CombatManager.tscn")
        order = _autoload_key_order(pg)
        if "AudioManager" in order and "CombatManager" in order:
            if order.index("AudioManager") >= order.index("CombatManager"):
                errors.append("AudioManager must be declared before CombatManager in [autoload]")
    else:
        errors.append("missing project.godot")

    # --- AudioManager.tscn: dedicated stream players (no Godot runtime) ---
    if os.path.isfile(audio_tscn):
        tscn = _read_text(audio_tscn)
        if 'type="AudioStreamPlayer"' not in tscn:
            errors.append('AudioManager.tscn must define AudioStreamPlayer nodes (type="AudioStreamPlayer")')
        for needle in (
            '[node name="AmbientPlayer"',
            '[node name="CombatPlayer"',
            '[node name="VictoryStingPlayer"',
        ):
            if needle not in tscn:
                errors.append(f"AudioManager.tscn must contain node line {needle!r}")
        player_lines = [ln for ln in tscn.splitlines() if 'type="AudioStreamPlayer"' in ln]
        if len(player_lines) < 3:
            errors.append(
                f"AudioManager.tscn must define at least 3 AudioStreamPlayer nodes (found {len(player_lines)})"
            )

    # --- CombatManager.gd → AudioManager API wiring ---
    if os.path.isfile(combat_gd):
        csrc = _read_text(combat_gd)
        for call in (
            "AudioManager.enter_combat",
            "AudioManager.play_victory_sting",
            "AudioManager.exit_combat_resume_ambient_only",
        ):
            if call not in csrc:
                errors.append(f"CombatManager.gd must call {call}")

    # --- HTML5 / web-safe structural checks (no DB, no Godot) ---
    if not os.path.isfile(export_presets):
        errors.append("missing export_presets.cfg (Web export preset required)")
    else:
        ep = _read_text(export_presets)
        if "[preset.0]" not in ep:
            errors.append("export_presets.cfg must define [preset.0] for HTML5 export")
        if 'platform="Web"' not in ep:
            errors.append('export_presets.cfg preset.0 must set platform="Web"')
        if "runnable=true" not in ep:
            errors.append("export_presets.cfg Web preset should be runnable=true")

    shipped = 0
    for rel in ("assets", "autoload"):
        d = os.path.join(root, rel)
        if os.path.isdir(d):
            shipped += _sum_dir_bytes(d)
    if shipped > _MAX_SHIPPED_ASSET_BYTES:
        mb = shipped / (1024 * 1024)
        errors.append(
            f"shipped asset budget exceeded: assets/+autoload/ total {mb:.2f} MiB "
            f"(max {_MAX_SHIPPED_ASSET_BYTES // (1024 * 1024)} MiB for HTML5)"
        )

    if errors:
        for e in errors:
            print("FAIL:", e)
        return 1

    print("Validation passed (AudioManager scene, CombatManager audio hooks, Web export, asset budget).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
