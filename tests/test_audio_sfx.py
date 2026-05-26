"""Presence and import metadata for res://audio/sfx (Kenney-derived CC0 SFX)."""

from __future__ import annotations

import configparser
import re
from pathlib import Path

import pytest

from tests.test_godot_config import _unquote_godot_value

REPO_ROOT = Path(__file__).resolve().parents[1]
SFX_DIR = REPO_ROOT / "audio" / "sfx"

EXPECTED_OGGS = (
    "sfx_ui_click_primary.ogg",
    "sfx_ui_click_secondary.ogg",
    "sfx_ui_click_tertiary.ogg",
    "sfx_ui_mouse_click.ogg",
    "sfx_ui_mouse_release.ogg",
    "sfx_ui_rollover.ogg",
    "sfx_ui_switch_light.ogg",
    "sfx_ui_switch_heavy.ogg",
)


def test_audio_sfx_directory_has_eight_ogg_streams() -> None:
    oggs = sorted(p.name for p in SFX_DIR.glob("*.ogg"))
    assert oggs == sorted(EXPECTED_OGGS)


def test_each_sfx_has_import_sidecar() -> None:
    for name in EXPECTED_OGGS:
        imp = SFX_DIR / f"{name}.import"
        assert imp.is_file(), f"missing .import for {name}"


def test_sfx_imports_disable_looping() -> None:
    """Ogg Vorbis import params: one-shots must not loop."""
    loop_re = re.compile(r"^loop=(true|false)$", re.MULTILINE)
    for name in EXPECTED_OGGS:
        text = (SFX_DIR / f"{name}.import").read_text(encoding="utf-8")
        m = loop_re.search(text)
        assert m is not None, f"no loop= line in {name}.import"
        assert m.group(1) == "false", f"{name} must have loop=false"


def test_sfx_import_files_reference_matching_source() -> None:
    for name in EXPECTED_OGGS:
        cp = configparser.ConfigParser(interpolation=None)
        cp.read(SFX_DIR / f"{name}.import", encoding="utf-8")
        assert cp.has_section("deps")
        src = _unquote_godot_value(cp.get("deps", "source_file"))
        assert src == f"res://audio/sfx/{name}"
        assert _unquote_godot_value(cp.get("remap", "importer")) == "oggvorbisstr"
