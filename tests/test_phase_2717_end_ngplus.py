"""Phase 2717 — end screen copy, main menu transition, NG+ slot persistence (text-level)."""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
INVENTORY = REPO_ROOT / "scripts" / "inventory.gd"
EPILOGUE_GD = REPO_ROOT / "scripts" / "final_cutscene_epilogue.gd"
EPILOGUE_TSCN = REPO_ROOT / "cutscenes" / "final_epilogue.tscn"


def test_inventory_slot_ng_plus_api() -> None:
    text = INVENTORY.read_text(encoding="utf-8")
    assert "unlock_ng_plus_for_active_slot" in text
    assert "is_ng_plus_unlocked" in text
    assert "get_active_slot" in text
    assert "set_active_slot" in text
    assert "SAVE_SLOT_COUNT" in text


def test_epilogue_persists_ng_plus_before_flagging_complete() -> None:
    text = EPILOGUE_GD.read_text(encoding="utf-8")
    assert "unlock_ng_plus_for_active_slot" in text
    assert text.index("unlock_ng_plus_for_active_slot") < text.index("_epilogue_complete = true")


def test_phase_2717_marker_in_sources() -> None:
    assert "2717" in INVENTORY.read_text(encoding="utf-8")
    assert "2717" in EPILOGUE_GD.read_text(encoding="utf-8")


def test_end_screen_nodes_wired_in_scene() -> None:
    tscn = EPILOGUE_TSCN.read_text(encoding="utf-8")
    assert "EndScreen" in tscn
    assert "MainMenuButton" in tscn
    assert '[connection signal="pressed"' in tscn
    assert "method=\"_on_main_menu_pressed\"" in tscn


def test_main_menu_scene_target_exists() -> None:
    assert "res://scenes/main_menu.tscn" in EPILOGUE_GD.read_text(encoding="utf-8")
    assert (REPO_ROOT / "scenes" / "main_menu.tscn").is_file()
