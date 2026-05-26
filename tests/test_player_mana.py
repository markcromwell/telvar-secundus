"""Static checks for Player mana (GDScript source)."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
PLAYER_GD = REPO_ROOT / "player" / "Player.gd"


def test_player_script_exists() -> None:
    assert PLAYER_GD.is_file(), f"Expected Player script at {PLAYER_GD}"


def test_player_mana_properties_and_defaults() -> None:
    text = PLAYER_GD.read_text(encoding="utf-8")
    assert re.search(r"var\s+mana\s*:\s*float\s*=\s*50\.0", text), "mana should be float initialized to 50"
    assert re.search(r"var\s+max_mana\s*:\s*float\s*=\s*50\.0", text), "max_mana should be float initialized to 50"


def test_player_mana_ready_clamps_to_max() -> None:
    text = PLAYER_GD.read_text(encoding="utf-8")
    assert "_ready" in text
    assert re.search(r"mana\s*=\s*max_mana", text), "_ready should sync mana to max_mana"


def test_player_regenerates_one_per_second() -> None:
    text = PLAYER_GD.read_text(encoding="utf-8")
    assert "_physics_process" in text
    assert re.search(r"MANA_REGEN_PER_SEC\s*:\s*float\s*=\s*1\.0", text) or re.search(
        r"1\.0\s*\*\s*delta", text
    ), "regeneration should be 1 mana per second (constant or literal)"


def test_player_mana_clamped_to_bounds() -> None:
    text = PLAYER_GD.read_text(encoding="utf-8")
    assert "clampf" in text
    assert re.search(r"clampf\s*\(\s*mana\s*,\s*0\.0\s*,\s*max_mana\s*\)", text), "mana should clamp to [0, max_mana]"
