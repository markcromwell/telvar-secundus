"""Phase 2563: HUD lore-unlock toast (CanvasLayer + Timer)."""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
HUD_SCENE = REPO_ROOT / "scenes" / "hud.tscn"
HUD_SCRIPT = REPO_ROOT / "scripts" / "hud.gd"


def test_hud_scene_and_script_exist() -> None:
    assert HUD_SCENE.is_file()
    assert HUD_SCRIPT.is_file()


def test_hud_scene_structure() -> None:
    raw = HUD_SCENE.read_text(encoding="utf-8")
    assert 'type="CanvasLayer"' in raw
    assert 'type="PanelContainer"' in raw
    assert 'parent="ToastPanel"' in raw and 'type="Label"' in raw
    assert "wait_time = 3.0" in raw
    assert "one_shot = true" in raw
    assert 'type="Timer"' in raw


def test_hud_script_contract() -> None:
    text = HUD_SCRIPT.read_text(encoding="utf-8")
    assert "LoreManager.lore_unlocked.connect" in text
    assert "_toast_timer.timeout.connect" in text
    assert "_toast_timer.start()" in text
    assert "_toast_panel.visible = false" in text
