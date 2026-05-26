#!/usr/bin/env python3
"""
Structural validation for the Telvar Secundus Godot project (no Godot binary).

Checks file presence, autoload registration, audio bus layout, AudioManager and
Player scene wiring (Godot 4.x text format). Exit 0 on success, 1 on failure.
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
PLAYER_SCENE = REPO_ROOT / "Player.tscn"
# District ambient: either LPC-style WAV placeholders or district-named OGG loops (HTML5-friendly).
REQUIRED_WAVS = (
    REPO_ROOT / "assets/audio/ambient_merchant_medieval.wav",
    REPO_ROOT / "assets/audio/ambient_veneficturis_dark.wav",
    REPO_ROOT / "assets/audio/ambient_rookery_tension.wav",
)
REQUIRED_OGGS = (
    REPO_ROOT / "assets/audio/merchant_district.ogg",
    REPO_ROOT / "assets/audio/veneficturis.ogg",
    REPO_ROOT / "assets/audio/rookery.ogg",
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


_RE_AUDIO_STREAM_PLAYER = re.compile(
    r'^\[node name="([^"]+)" type="AudioStreamPlayer"[^\]]*\]\s*\n\s*bus = &"([^"]+)"',
    re.MULTILINE,
)


def _audio_stream_player_nodes(scene_text: str) -> list[tuple[str, str]]:
    """Return (node_name, bus_name) for each AudioStreamPlayer block with bus on the next line."""
    return [(m.group(1), m.group(2)) for m in _RE_AUDIO_STREAM_PLAYER.finditer(scene_text)]


def _scene_has_music_children(scene_text: str) -> bool:
    nodes = dict(_audio_stream_player_nodes(scene_text))
    expected = {"MusicA": "Music", "MusicB": "Music", "SFXPlayer": "SFX"}
    return all(nodes.get(name) == bus for name, bus in expected.items())


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
            errors.append(
                "AudioManager.tscn: need MusicA, MusicB, SFXPlayer as AudioStreamPlayer nodes "
                'with bus = &"Music" / &"Music" / &"SFX" on the line after each node header'
            )

    wav_ok = all(p.is_file() for p in REQUIRED_WAVS)
    ogg_ok = all(p.is_file() for p in REQUIRED_OGGS)
    if not wav_ok and not ogg_ok:
        missing_wav = [p for p in REQUIRED_WAVS if not p.is_file()]
        missing_ogg = [p for p in REQUIRED_OGGS if not p.is_file()]
        errors.append(
            "assets/audio: need a complete district ambient set — either all WAV placeholders ("
            + ", ".join(p.name for p in REQUIRED_WAVS)
            + ") or all OGG loops ("
            + ", ".join(p.name for p in REQUIRED_OGGS)
            + "). Missing WAV: "
            + (", ".join(p.relative_to(REPO_ROOT).as_posix() for p in missing_wav) or "none")
            + "; missing OGG: "
            + (", ".join(p.relative_to(REPO_ROOT).as_posix() for p in missing_ogg) or "none")
        )

    if not PLAYER_SCENE.is_file():
        errors.append("Missing Player.tscn")
    else:
        pt = _read_text(PLAYER_SCENE)
        if 'path="res://scripts/Player.gd"' not in pt:
            errors.append('Player.tscn: must reference script path="res://scripts/Player.gd"')
        cam = '[node name="Camera2D" type="Camera2D" parent="."]'
        if cam not in pt:
            errors.append(f"Player.tscn: missing child node {cam!r}")
        else:
            for needle in ("current = true", "position_smoothing_enabled = true", "position_smoothing_speed = 10.0"):
                if needle not in pt:
                    errors.append(f"Player.tscn: Camera2D expected {needle!r}")

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
