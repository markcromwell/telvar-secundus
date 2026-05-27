"""Static checks for HUD mana bar (scene + script)."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
HUD_TSCN = REPO_ROOT / "HUD.tscn"
HUD_GD = REPO_ROOT / "HUD.gd"


def test_hud_scene_exists() -> None:
    assert HUD_TSCN.is_file(), f"Expected HUD scene at {HUD_TSCN}"


def test_hud_script_exists() -> None:
    assert HUD_GD.is_file(), f"Expected HUD script at {HUD_GD}"


def test_hud_scene_has_blue_progress_bar() -> None:
    text = HUD_TSCN.read_text(encoding="utf-8")
    assert "ProgressBar" in text, "HUD should include a ProgressBar for mana"
    assert "StyleBoxFlat_fill" in text
    assert "theme_override_styles/fill" in text
    # Blue-forward fill: b > g and b > r in StyleBoxFlat_fill bg_color
    m = re.search(
        r"\[sub_resource[^\]]*id=\"StyleBoxFlat_fill\"[^\]]*\][^\[]*?bg_color\s*=\s*Color\(([^)]+)\)",
        text,
        re.DOTALL,
    )
    assert m, "StyleBoxFlat_fill sub_resource with bg_color should exist"
    parts = [p.strip() for p in m.group(1).split(",")]
    r, g, b = float(parts[0]), float(parts[1]), float(parts[2])
    assert b > g and b > r, "Mana fill should be visually blue (dominant blue channel)"


def test_hud_script_max_and_current_api() -> None:
    text = HUD_GD.read_text(encoding="utf-8")
    assert re.search(r"func\s+set_max_mana\s*\(", text), "HUD.gd should define set_max_mana"
    assert re.search(r"func\s+set_current_mana\s*\(", text), "HUD.gd should define set_current_mana"
    assert "_mana_bar.max_value" in text
    assert "_mana_bar.value" in text
    assert "clampf" in text
