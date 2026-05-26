#!/usr/bin/env python3
"""
Structural validation for the Telvar Secundus Godot project (no Godot binary).

Checks file presence, autoload registration, audio bus layout, and AudioManager
scene wiring. Exit 0 on success, 1 on failure.
"""

from __future__ import annotations

import configparser
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
PROJECT_GODOT = REPO_ROOT / "project.godot"
BUS_LAYOUT = REPO_ROOT / "default_bus_layout.tres"
AUDIO_MANAGER_SCENE = REPO_ROOT / "AudioManager.tscn"
AUDIO_MANAGER_SCRIPT = REPO_ROOT / "AudioManager.gd"
REQUIRED_WAVS = (
    REPO_ROOT / "assets/audio/ambient_merchant_medieval.wav",
    REPO_ROOT / "assets/audio/ambient_veneficturis_dark.wav",
    REPO_ROOT / "assets/audio/ambient_rookery_tension.wav",
)


def _wrap_godot_root_section(text: str) -> str:
    stripped = text.lstrip("\ufeff")
    if not stripped.lstrip().startswith("["):
        return "[__godot_root__]\n" + text
    return text


def _load_project_ini() -> configparser.ConfigParser | None:
    if not PROJECT_GODOT.is_file():
        return None
    text = PROJECT_GODOT.read_text(encoding="utf-8")
    text = _wrap_godot_root_section(text)
    cp = configparser.ConfigParser(interpolation=None)
    cp.read_string(text)
    return cp


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _scene_has_music_children(scene_text: str) -> bool:
    return bool(
        re.search(r'\[node name="MusicA" type="AudioStreamPlayer"', scene_text)
        and re.search(r'\[node name="MusicB" type="AudioStreamPlayer"', scene_text)
        and re.search(r'\[node name="SFXPlayer" type="AudioStreamPlayer"', scene_text)
    )


def _bus_layout_has_music_sfx(layout_text: str) -> bool:
    # Resource text uses quoted StringNames: bus/N/name = &"Music"
    has_music = bool(re.search(r'bus/\d+/name\s*=\s*&"Music"', layout_text))
    has_sfx = bool(re.search(r'bus/\d+/name\s*=\s*&"SFX"', layout_text))
    has_master = bool(re.search(r'bus/\d+/name\s*=\s*&"Master"', layout_text))
    return has_music and has_sfx and has_master


def _total_audio_bytes() -> int:
    total = 0
    root = REPO_ROOT / "assets" / "audio"
    if not root.is_dir():
        return 0
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in {".wav", ".ogg", ".mp3"}:
            total += p.stat().st_size
    return total


def main() -> int:
    errors: list[str] = []

    cp = _load_project_ini()
    if cp is None:
        errors.append(f"Missing {PROJECT_GODOT.relative_to(REPO_ROOT)}")
    else:
        if not cp.has_section("autoload") or not cp.has_option("autoload", "AudioManager"):
            errors.append("project.godot: missing [autoload] AudioManager")
        else:
            autoload_val = cp.get("autoload", "AudioManager").strip().strip('"')
            if "AudioManager.tscn" not in autoload_val:
                errors.append(f"project.godot: AudioManager autoload must reference AudioManager.tscn (got {autoload_val!r})")
            if not autoload_val.lstrip().startswith("*"):
                errors.append("project.godot: AudioManager autoload should use singleton prefix '*' (e.g. *res://... )")
        if not cp.has_section("audio"):
            errors.append("project.godot: missing [audio] section")
        else:
            bus_path = cp.get("audio", "buses/default_bus_layout", fallback="").strip().strip('"')
            if bus_path != "res://default_bus_layout.tres":
                errors.append(
                    "project.godot: audio buses/default_bus_layout must be res://default_bus_layout.tres "
                    f"(got {bus_path!r})"
                )

    if not BUS_LAYOUT.is_file():
        errors.append("Missing default_bus_layout.tres")
    else:
        if not _bus_layout_has_music_sfx(_read_text(BUS_LAYOUT)):
            errors.append("default_bus_layout.tres: need Master, Music, and SFX buses")

    if not AUDIO_MANAGER_SCRIPT.is_file():
        errors.append("Missing AudioManager.gd")
    else:
        src = _read_text(AUDIO_MANAGER_SCRIPT)
        for needle in ("set_current_district", "play_music", "play_sfx", "set_volume", "CROSSFADE_SEC", "AMBIENT_LINEAR"):
            if needle not in src:
                errors.append(f"AudioManager.gd: expected symbol {needle!r}")

    if not AUDIO_MANAGER_SCENE.is_file():
        errors.append("Missing AudioManager.tscn")
    else:
        st = _read_text(AUDIO_MANAGER_SCENE)
        if 'path="res://AudioManager.gd"' not in st:
            errors.append("AudioManager.tscn: must reference res://AudioManager.gd")
        if not _scene_has_music_children(st):
            errors.append('AudioManager.tscn: need MusicA, MusicB, SFXPlayer AudioStreamPlayer nodes')

    for wav in REQUIRED_WAVS:
        if not wav.is_file():
            errors.append(f"Missing ambient asset: {wav.relative_to(REPO_ROOT)}")

    max_audio = 5 * 1024 * 1024
    audio_total = _total_audio_bytes()
    if audio_total > max_audio:
        errors.append(f"assets/audio exceeds 5 MiB budget ({audio_total} bytes)")

    if errors:
        for e in errors:
            print("FAIL:", e)
        return 1

    print("validate.py: structural checks passed (audio bytes under budget:", audio_total, ")")
    return 0


if __name__ == "__main__":
    sys.exit(main())
