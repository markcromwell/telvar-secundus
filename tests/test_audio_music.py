"""Presence and import metadata for res://audio/music (looping OGG streams)."""

from __future__ import annotations

import configparser
import re
from pathlib import Path

import pytest

from tests.test_godot_config import _unquote_godot_value

REPO_ROOT = Path(__file__).resolve().parents[1]
MUSIC_DIR = REPO_ROOT / "audio" / "music"

EXPECTED_OGGS = (
    "music_loop_physics_platformer.ogg",
    "music_loop_the_comeback.ogg",
    "music_loop_maldita.ogg",
    "music_loop_spinning_monkeys.ogg",
    "music_loop_item_spawn.ogg",
)


def test_audio_music_directory_has_five_ogg_streams() -> None:
    oggs = sorted(p.name for p in MUSIC_DIR.glob("*.ogg"))
    assert oggs == sorted(EXPECTED_OGGS)


def test_each_music_track_has_import_sidecar() -> None:
    for name in EXPECTED_OGGS:
        imp = MUSIC_DIR / f"{name}.import"
        assert imp.is_file(), f"missing .import for {name}"


def test_music_imports_enable_looping() -> None:
    """Ogg Vorbis import params: background music must loop."""
    loop_re = re.compile(r"^loop=(true|false)$", re.MULTILINE)
    for name in EXPECTED_OGGS:
        text = (MUSIC_DIR / f"{name}.import").read_text(encoding="utf-8")
        m = loop_re.search(text)
        assert m is not None, f"no loop= line in {name}.import"
        assert m.group(1) == "true", f"{name} must have loop=true"


def test_music_import_files_reference_matching_source() -> None:
    for name in EXPECTED_OGGS:
        cp = configparser.ConfigParser(interpolation=None)
        cp.read(MUSIC_DIR / f"{name}.import", encoding="utf-8")
        assert cp.has_section("deps")
        src = _unquote_godot_value(cp.get("deps", "source_file"))
        assert src == f"res://audio/music/{name}"
        assert _unquote_godot_value(cp.get("remap", "importer")) == "oggvorbisstr"
