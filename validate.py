#!/usr/bin/env python3
"""
Telvar Secundus structural validation (no Godot runtime).

Checks project audio bus wiring, SFXManager autoload, script/scene references to
res:// audio assets, and that those asset files exist on disk.
"""

from __future__ import annotations

import configparser
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent

# Godot resource paths referenced from .gd / .tscn text.
_RES_AUDIO_RE = re.compile(
    r'res://[a-zA-Z0-9_./-]+\.(?:wav|ogg|mp3)',
    re.IGNORECASE,
)


def _err(errors: list[str], msg: str) -> None:
    errors.append(msg)


def _wrap_godot_root_section(text: str) -> str:
    stripped = text.lstrip("\ufeff")
    if not stripped.lstrip().startswith("["):
        return "[__godot_root__]\n" + text
    return text


def _unquote_godot_value(raw: str) -> str:
    s = raw.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        return s[1:-1]
    return s


def _load_project_godot(errors: list[str]) -> configparser.ConfigParser | None:
    path = REPO_ROOT / "project.godot"
    if not path.is_file():
        _err(errors, f"Missing project.godot at {path}")
        return None
    text = _wrap_godot_root_section(path.read_text(encoding="utf-8"))
    cp = configparser.ConfigParser(interpolation=None)
    try:
        cp.read_string(text)
    except configparser.Error as e:
        _err(errors, f"Could not parse project.godot: {e}")
        return None
    return cp


def _resolve_res_path(res_uri: str) -> Path:
    assert res_uri.startswith("res://")
    rel = res_uri[len("res://") :].lstrip("/")
    return REPO_ROOT / rel


def _validate_project_godot_audio_and_autoload(
    errors: list[str], cp: configparser.ConfigParser
) -> None:
    if not cp.has_section("audio"):
        _err(errors, "project.godot: missing [audio] section")
        return
    if not cp.has_option("audio", "buses/default_bus_layout"):
        _err(errors, "project.godot: missing audio buses/default_bus_layout")
        return
    layout = _unquote_godot_value(cp.get("audio", "buses/default_bus_layout"))
    if layout != "res://default_bus_layout.tres":
        _err(
            errors,
            f"project.godot: buses/default_bus_layout must be "
            f'res://default_bus_layout.tres (got {layout!r})',
        )
    layout_path = _resolve_res_path(layout)
    if not layout_path.is_file():
        _err(errors, f"Audio bus layout file missing: {layout_path}")

    if not cp.has_section("autoload"):
        _err(errors, "project.godot: missing [autoload] section")
        return
    if not cp.has_option("autoload", "SFXManager"):
        _err(errors, "project.godot: missing autoload entry SFXManager")
        return
    raw_auto = cp.get("autoload", "SFXManager")
    auto = _unquote_godot_value(raw_auto)
    # Godot: *res://... marks a singleton autoload; strip leading * for filesystem path.
    if auto.startswith("*"):
        auto = auto[1:]
    if auto != "res://SFXManager.tscn":
        _err(
            errors,
            f"project.godot: SFXManager autoload must be *res://SFXManager.tscn (got {raw_auto!r})",
        )
    sfx_scene = _resolve_res_path("res://SFXManager.tscn")
    if not sfx_scene.is_file():
        _err(errors, f"SFXManager autoload scene missing: {sfx_scene}")


def _validate_default_bus_layout_sfx(errors: list[str]) -> None:
    path = REPO_ROOT / "default_bus_layout.tres"
    if not path.is_file():
        _err(errors, f"Missing default_bus_layout.tres at {path}")
        return
    text = path.read_text(encoding="utf-8")
    if 'bus/1/name = &"SFX"' not in text:
        _err(errors, 'default_bus_layout.tres: expected dedicated bus bus/1/name = &"SFX"')
    if 'bus/1/send = &"Master"' not in text:
        _err(errors, "default_bus_layout.tres: SFX bus must send to Master")


def _validate_sfx_manager_scene_and_script(errors: list[str]) -> None:
    tscn = REPO_ROOT / "SFXManager.tscn"
    script = REPO_ROOT / "SFXManager.gd"
    if not script.is_file():
        _err(errors, f"Missing SFXManager.gd at {script}")
    else:
        gd = script.read_text(encoding="utf-8")
        if 'const BUS_SFX := "SFX"' not in gd and 'const BUS_SFX = "SFX"' not in gd:
            _err(errors, "SFXManager.gd: expected const BUS_SFX bound to \"SFX\"")
        if "player.bus = BUS_SFX" not in gd:
            _err(errors, "SFXManager.gd: AudioStreamPlayer must assign bus = BUS_SFX")

    if not tscn.is_file():
        _err(errors, f"Missing SFXManager.tscn at {tscn}")
        return
    ttext = tscn.read_text(encoding="utf-8")
    if "[node name=\"SFXManager\"" not in ttext and "[node name='SFXManager'" not in ttext:
        _err(errors, "SFXManager.tscn: expected root node named SFXManager")
    if 'path="res://SFXManager.gd"' not in ttext:
        _err(errors, "SFXManager.tscn: ext_resource must reference res://SFXManager.gd")


def _collect_res_audio_uris_from_gd_tscn(errors: list[str]) -> set[str]:
    found: set[str] = set()
    for pattern in ("*.gd", "*.tscn"):
        for path in REPO_ROOT.rglob(pattern):
            if ".git" in path.parts:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except OSError as e:
                _err(errors, f"Could not read {path}: {e}")
                continue
            for m in _RES_AUDIO_RE.finditer(text):
                found.add(m.group(0))
    return found


def _validate_audio_assets_exist(errors: list[str], uris: set[str]) -> None:
    for uri in sorted(uris):
        p = _resolve_res_path(uri)
        if not p.is_file():
            _err(errors, f"Referenced audio file missing on disk: {uri} -> {p}")


def _validate_core_gd_sfx_usage(errors: list[str]) -> None:
    """Ensure primary gameplay scripts still route one-shots / UI through the SFX bus."""
    expectations: list[tuple[str, Path, list[str]]] = [
        ("Player.gd", REPO_ROOT / "Player.gd", ["SFXManager.play"]),
        ("Door.gd", REPO_ROOT / "Door.gd", ["SFXManager.play", "creak_sound"]),
        ("Spell.gd", REPO_ROOT / "Spell.gd", ["SFXManager.play", "shimmer_sound", "whoosh_sound"]),
        ("HitBox.gd", REPO_ROOT / "HitBox.gd", ["SFXManager.play", "hit_sound"]),
        (
            "DialogueManager.gd",
            REPO_ROOT / "DialogueManager.gd",
            ['const BUS_SFX := "SFX"', "bus = BUS_SFX", "func play_ui_click"],
        ),
        (
            "DialogueBox.gd",
            REPO_ROOT / "DialogueBox.gd",
            ["play_ui_click", "advance_dialogue"],
        ),
    ]
    for label, path, needles in expectations:
        if not path.is_file():
            _err(errors, f"Missing {label} at {path}")
            continue
        text = path.read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                _err(errors, f"{label}: expected SFX wiring substring missing: {needle!r}")


def _validate_player_scene_footstep_nodes(errors: list[str]) -> None:
    """Player.tscn should wire exported footstep streams (acceptance: audio nodes)."""
    path = REPO_ROOT / "Player.tscn"
    if not path.is_file():
        _err(errors, f"Missing Player.tscn at {path}")
        return
    text = path.read_text(encoding="utf-8")
    if "type=\"AudioStream\"" not in text and "type='AudioStream'" not in text:
        _err(errors, "Player.tscn: expected AudioStream ext_resource entries for footsteps")
    for chunk in ("footstep_stone.wav", "footstep_wood.wav"):
        if chunk not in text:
            _err(errors, f"Player.tscn: expected footstep reference containing {chunk!r}")
    if "footstep_stone = ExtResource" not in text:
        _err(errors, "Player.tscn: footstep_stone must be assigned from ExtResource")
    if "footstep_wood = ExtResource" not in text:
        _err(errors, "Player.tscn: footstep_wood must be assigned from ExtResource")


def main() -> int:
    errors: list[str] = []

    cp = _load_project_godot(errors)
    if cp is not None:
        _validate_project_godot_audio_and_autoload(errors, cp)

    _validate_default_bus_layout_sfx(errors)
    _validate_sfx_manager_scene_and_script(errors)
    _validate_core_gd_sfx_usage(errors)
    _validate_player_scene_footstep_nodes(errors)

    audio_uris = _collect_res_audio_uris_from_gd_tscn(errors)
    _validate_audio_assets_exist(errors, audio_uris)

    if errors:
        for e in errors:
            print("FAIL:", e, file=sys.stderr)
        return 1

    print(
        "OK: SFX bus + SFXManager autoload, SFXManager wiring, "
        f"Player.tscn footsteps, {len(audio_uris)} res:// audio asset(s) on disk."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
