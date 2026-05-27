"""Text-level checks for final epilogue cutscene (Godot 4.3 GDScript + .tscn)."""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
EPILOGUE_GD = REPO_ROOT / "scripts" / "final_cutscene_epilogue.gd"
EPILOGUE_TSCN = REPO_ROOT / "cutscenes" / "final_epilogue.tscn"
MAIN_MENU = REPO_ROOT / "scenes" / "main_menu.tscn"


def test_epilogue_script_exists() -> None:
    assert EPILOGUE_GD.is_file()


def test_epilogue_scene_exists() -> None:
    assert EPILOGUE_TSCN.is_file()


def test_panel_hold_is_four_seconds() -> None:
    text = EPILOGUE_GD.read_text(encoding="utf-8")
    assert "PANEL_HOLD_SECONDS: float = 4.0" in text


def test_animation_player_sequences_epilogue() -> None:
    text = EPILOGUE_GD.read_text(encoding="utf-8")
    assert "AnimationPlayer" in EPILOGUE_TSCN.read_text(encoding="utf-8")
    assert "AnimationPlayer" in text
    assert "add_track(Animation.TYPE_VALUE)" in text
    assert "final_cut/epilogue" in text


def test_skip_gated_until_animation_finished() -> None:
    text = EPILOGUE_GD.read_text(encoding="utf-8")
    assert "_epilogue_complete" in text
    assert "animation_finished.connect" in text
    assert text.index("_epilogue_complete") < text.index("func _unhandled_input")


def test_end_screen_copy_and_main_menu_scene() -> None:
    tscn = EPILOGUE_TSCN.read_text(encoding="utf-8")
    assert "The End — To be continued in The Paladin's Vow" in tscn
    assert "MainMenuButton" in tscn
    assert MAIN_MENU.is_file()


def test_phase_marker_present() -> None:
    assert "2716" in EPILOGUE_GD.read_text(encoding="utf-8")
