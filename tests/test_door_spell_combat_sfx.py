"""Structural checks for door / spell / combat SFX (phase 2739, no Godot runtime)."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOOR_GD = REPO_ROOT / "Door.gd"
SPELL_GD = REPO_ROOT / "Spell.gd"
HITBOX_GD = REPO_ROOT / "HitBox.gd"
CREAK_WAV = REPO_ROOT / "assets" / "audio" / "door_creak.wav"
SHIMMER_WAV = REPO_ROOT / "assets" / "audio" / "spell_shimmer.wav"
WHOOSH_WAV = REPO_ROOT / "assets" / "audio" / "spell_whoosh.wav"
HIT_WAV = REPO_ROOT / "assets" / "audio" / "combat_hit.wav"


def test_door_spell_hitbox_scripts_exist() -> None:
    assert DOOR_GD.is_file()
    assert SPELL_GD.is_file()
    assert HITBOX_GD.is_file()


def test_transition_sfx_audio_assets_exist() -> None:
    assert CREAK_WAV.is_file()
    assert SHIMMER_WAV.is_file()
    assert WHOOSH_WAV.is_file()
    assert HIT_WAV.is_file()


def test_door_gd_creak_via_sfx_manager() -> None:
    text = DOOR_GD.read_text(encoding="utf-8")
    assert "SFXManager.play" in text
    assert "creak_sound" in text
    assert "func on_transition" in text


def test_spell_gd_shimmer_whoosh_via_sfx_manager() -> None:
    text = SPELL_GD.read_text(encoding="utf-8")
    assert "SFXManager.play" in text
    assert "shimmer_sound" in text
    assert "whoosh_sound" in text
    assert "func play_cast_sfx" in text


def test_hitbox_gd_hit_via_sfx_manager() -> None:
    text = HITBOX_GD.read_text(encoding="utf-8")
    assert "SFXManager.play" in text
    assert "hit_sound" in text
    assert "func apply_damage" in text
