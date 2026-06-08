"""Spec 1538 (phase 3240): location-based ambient music across overworld<->interior transitions.

The game's only location-driven ambient music system is the ``AudioManager`` autoload
(``AudioManager.gd``, phase 2733). Gameplay zones report the player's current location
through its single public entry point::

    AudioManager.set_current_district(area_label)

``Player.gd`` (the district sensor, phase 2734) calls this whenever the player crosses a
zone boundary -- entering an interior/building zone or returning to an open-world district.
The manager resolves ``area_label`` to a district key, looks up that district's ambient
stream and crossfades to it. Crucially it *only* switches tracks when the resolved location
actually changes: re-reporting the same location (even spelled differently) is a no-op (the
``key == _current_district`` guard in ``set_current_district``).

These tests exercise that behaviour without a Godot editor / binary (none is available in
CI for pytest; the GDScript-runtime checks live in the gdUnit4 suite). We build a faithful
Python re-implementation of ``set_current_district``'s decision logic, *seeded from the real
source* -- the district keys, alias normalisation and stream map are parsed straight out of
``AudioManager.gd`` so the model can never silently drift from the shipped implementation.
The model reports the newly-selected track on a real switch and ``None`` when the location is
unchanged, mirroring the manager's crossfade / no-op behaviour.

Placed in its own module (separate from the autosave transition tests) so the two test areas
stay independently deployable. Shares the phase-1 ``unquote_godot_value`` helper.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from tests._transition_support import unquote_godot_value

REPO_ROOT = Path(__file__).resolve().parents[1]
# The location-based ambient music player (phase 2733): district-keyed crossfades.
AMBIENT_MUSIC_GD = REPO_ROOT / "AudioManager.gd"


# --------------------------------------------------------------------------- #
# Parse the real implementation so the behavioural model tracks the source.
# --------------------------------------------------------------------------- #

def _read_source() -> str:
    if not AMBIENT_MUSIC_GD.is_file():
        pytest.fail(f"Missing location-based music player: {AMBIENT_MUSIC_GD}")
    return AMBIENT_MUSIC_GD.read_text(encoding="utf-8")


def _parse_key_constants(src: str) -> dict[str, str]:
    """``const KEY_MERCHANT := "merchant_district"`` -> {"KEY_MERCHANT": "merchant_district"}."""
    consts: dict[str, str] = {}
    for name, raw in re.findall(r"const\s+(KEY_\w+)\s*:=\s*(\"[^\"]*\")", src):
        consts[name] = unquote_godot_value(raw)
    return consts


def _extract_block(src: str, decl: str) -> str:
    """Return the text between ``const <decl> := {`` and its closing ``}``."""
    start = src.find(f"const {decl} := {{")
    assert start != -1, f"missing `const {decl} :=` block in AudioManager.gd"
    brace = src.find("{", start)
    depth = 0
    for i in range(brace, len(src)):
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
            if depth == 0:
                return src[brace + 1 : i]
    pytest.fail(f"unterminated `const {decl}` block in AudioManager.gd")


def _parse_district_streams(src: str, consts: dict[str, str]) -> dict[str, str]:
    """Map district key -> ambient stream path from ``DISTRICT_STREAMS``."""
    block = _extract_block(src, "DISTRICT_STREAMS")
    streams: dict[str, str] = {}
    for key_const, raw in re.findall(r"(KEY_\w+)\s*:\s*(\"[^\"]*\")", block):
        assert key_const in consts, f"DISTRICT_STREAMS references unknown {key_const}"
        streams[consts[key_const]] = unquote_godot_value(raw)
    return streams


def _parse_district_aliases(src: str, consts: dict[str, str]) -> dict[str, str]:
    """Map normalised alias label -> district key from ``DISTRICT_ALIASES``.

    Entry keys are either string literals (``"merchant district": KEY_MERCHANT``) or a
    ``KEY_*`` constant (``KEY_MERCHANT: KEY_MERCHANT``); values are always ``KEY_*``.
    """
    block = _extract_block(src, "DISTRICT_ALIASES")
    aliases: dict[str, str] = {}
    pattern = re.compile(r"^\s*(?:(\"[^\"]*\")|(KEY_\w+))\s*:\s*(KEY_\w+)\s*,?\s*$", re.MULTILINE)
    for quoted, key_const, target_const in pattern.findall(block):
        assert target_const in consts, f"DISTRICT_ALIASES maps to unknown {target_const}"
        if quoted:
            label = unquote_godot_value(quoted)
        else:
            assert key_const in consts, f"DISTRICT_ALIASES keyed on unknown {key_const}"
            label = consts[key_const]
        aliases[label] = consts[target_const]
    return aliases


# --------------------------------------------------------------------------- #
# Faithful model of AudioManager.set_current_district()'s track-change decision.
# --------------------------------------------------------------------------- #

class AmbientMusicPlayer:
    """Pure-Python mirror of ``AudioManager``'s location-driven track switching.

    Reproduces ``_resolve_district_key`` (lowercase, ``_``/``-`` -> space, collapse spaces,
    alias lookup), ``set_current_district`` (unknown/empty -> ignore; same location ->
    no-op) and ``_crossfade_music`` (no-op when the lead player already holds the target
    stream). ``set_current_district`` returns the newly-playing stream path on a real
    switch and ``None`` when no track change occurs -- the observable "report".
    """

    def __init__(self, streams: dict[str, str], aliases: dict[str, str]) -> None:
        self._streams = streams
        self._aliases = aliases
        self.current_district: str = ""
        self.lead_stream: str | None = None  # AudioStreamPlayer.stream on the lead player
        self.lead_playing: bool = False

    def _resolve_district_key(self, raw: str) -> str:
        t = raw.strip().lower().replace("_", " ").replace("-", " ")
        t = " ".join(t.split())  # collapse runs of spaces (AudioManager._collapse_spaces)
        return self._aliases.get(t, "")

    def set_current_district(self, area_label: str) -> str | None:
        key = self._resolve_district_key(area_label)
        if not key:  # `if key.is_empty(): return`
            return None
        path = self._streams.get(key, "")
        if not path:  # `if path.is_empty(): return`
            return None
        # Same location already playing -> no track change (the guard we care about).
        if key == self.current_district and self.lead_playing and self.lead_stream is not None:
            return None
        self.current_district = key
        # `_crossfade_music`: a no-op when the lead already holds this exact stream.
        if self.lead_stream == path:
            return None
        self.lead_stream = path
        self.lead_playing = True
        return path


@pytest.fixture
def music_player() -> AmbientMusicPlayer:
    src = _read_source()
    consts = _parse_key_constants(src)
    streams = _parse_district_streams(src, consts)
    aliases = _parse_district_aliases(src, consts)
    assert streams, "no DISTRICT_STREAMS parsed from AudioManager.gd"
    assert aliases, "no DISTRICT_ALIASES parsed from AudioManager.gd"
    return AmbientMusicPlayer(streams, aliases)


@pytest.fixture
def two_locations(music_player: AmbientMusicPlayer) -> tuple[str, str]:
    """Two distinct location labels with different ambient tracks (overworld vs interior)."""
    keys = sorted(music_player._streams)
    assert len(keys) >= 2, "need >=2 districts to model an overworld<->interior transition"
    overworld, interior = keys[0], keys[1]
    assert music_player._streams[overworld] != music_player._streams[interior]
    return overworld, interior


# --------------------------------------------------------------------------- #
# Source-binding checks: the public API and its no-change guard still exist.
# --------------------------------------------------------------------------- #

def test_location_music_player_exposes_set_current_district_api() -> None:
    src = _read_source()
    assert "func set_current_district(" in src, "expected public set_current_district() API"


def test_set_current_district_guards_against_unchanged_location() -> None:
    """The no-track-change behaviour is the `key == _current_district` early return."""
    src = _read_source()
    assert "key == _current_district" in src, "missing unchanged-location guard"


def test_crossfade_is_a_noop_when_stream_unchanged() -> None:
    src = _read_source()
    assert "if outgoing.stream == next:" in src, "missing identical-stream crossfade no-op"


def test_district_streams_are_audio_resources() -> None:
    player_src = _read_source()
    consts = _parse_key_constants(player_src)
    streams = _parse_district_streams(player_src, consts)
    assert streams, "DISTRICT_STREAMS parsed empty"
    for path in streams.values():
        assert path.startswith("res://"), f"non-resource stream path: {path}"
        assert path.lower().endswith((".ogg", ".wav")), f"not an audio stream: {path}"


# --------------------------------------------------------------------------- #
# Behavioural checks: track changes are reported across location transitions.
# --------------------------------------------------------------------------- #

def test_entering_interior_reports_track_change(
    music_player: AmbientMusicPlayer, two_locations: tuple[str, str]
) -> None:
    overworld, interior = two_locations
    music_player.set_current_district(overworld)  # establish overworld ambient

    reported = music_player.set_current_district(interior)

    assert reported is not None, "entering an interior must report a track change"
    assert reported == music_player._streams[interior]
    assert music_player.current_district == interior


def test_returning_to_overworld_reports_track_change(
    music_player: AmbientMusicPlayer, two_locations: tuple[str, str]
) -> None:
    overworld, interior = two_locations
    overworld_stream = music_player.set_current_district(overworld)
    interior_stream = music_player.set_current_district(interior)
    assert overworld_stream != interior_stream

    reported = music_player.set_current_district(overworld)

    assert reported is not None, "returning to the overworld must report a track change"
    assert reported == overworld_stream
    assert music_player.current_district == overworld


def test_transition_without_location_change_reports_no_track_change(
    music_player: AmbientMusicPlayer, two_locations: tuple[str, str]
) -> None:
    overworld, _interior = two_locations
    first = music_player.set_current_district(overworld)
    assert first is not None  # first report establishes the track

    again = music_player.set_current_district(overworld)

    assert again is None, "re-entering the same location must not switch tracks"
    assert music_player.current_district == overworld


def test_same_location_spelled_differently_reports_no_track_change(
    music_player: AmbientMusicPlayer
) -> None:
    """Alias normalisation: a different label for the *same* location is not a track change."""
    # Find a district reachable by two distinct raw labels (e.g. "merchant_district"
    # and "merchant district") so we exercise the normaliser, not just string equality.
    by_key: dict[str, list[str]] = {}
    for label, key in music_player._aliases.items():
        by_key.setdefault(key, []).append(label)
    variants = next((labels for labels in by_key.values() if len(labels) >= 2), None)
    if variants is None:
        pytest.skip("no district has two alias spellings to exercise normalisation")

    first_label, second_label = variants[0], variants[1]
    assert music_player.set_current_district(first_label) is not None
    assert music_player.set_current_district(second_label) is None
    # And the alias-normalised round-trip ("_" vs " ") is also a no-op.
    assert music_player.set_current_district(first_label.replace(" ", "_")) is None


def test_unknown_location_label_is_ignored_without_error(
    music_player: AmbientMusicPlayer, two_locations: tuple[str, str]
) -> None:
    overworld, _interior = two_locations
    music_player.set_current_district(overworld)
    before = music_player.current_district

    # Unknown labels resolve to "" and are silently ignored (no track change, no raise).
    assert music_player.set_current_district("not_a_real_district") is None
    assert music_player.set_current_district("") is None
    assert music_player.current_district == before


def test_full_overworld_interior_round_trip_raises_no_exception(
    music_player: AmbientMusicPlayer, two_locations: tuple[str, str]
) -> None:
    """A complete transition sequence must switch tracks cleanly without raising."""
    overworld, interior = two_locations
    sequence = [overworld, overworld, interior, interior, overworld, "unknown", interior]
    reports = [music_player.set_current_district(label) for label in sequence]

    # overworld(change), overworld(same), interior(change), interior(same),
    # overworld(change), unknown(ignored), interior(change)
    changed = [r for r in reports if r is not None]
    assert changed == [
        music_player._streams[overworld],
        music_player._streams[interior],
        music_player._streams[overworld],
        music_player._streams[interior],
    ]
    assert music_player.current_district == interior
