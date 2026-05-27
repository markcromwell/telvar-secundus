"""Spec 2702: Sealed Wings quest journal line after telvar-room night scene trigger."""

from __future__ import annotations

import json
from pathlib import Path

from tests.test_godot_config import REPO_ROOT

QUEST_JSON = REPO_ROOT / "data" / "quests" / "sealed_wings.json"
QUEST_LOG_GD = REPO_ROOT / "autoload" / "quest_log.gd"
NIGHT_SCRIPT = REPO_ROOT / "scripts" / "night_scenes" / "sealed_wings_post_rest_event.gd"
EXPECTED_OBJECTIVE = "I know what Myramar wants. He wants me to go in there."


def _simulated_sealed_wings_objective_after_night() -> str:
    """Mirror QuestLog.apply_sealed_wings_after_telvar_room_night JSON read logic (no Godot)."""
    data = json.loads(QUEST_JSON.read_text(encoding="utf-8"))
    lines = data.get("objective_lines", {})
    if not isinstance(lines, dict):
        return ""
    raw = lines.get("after_telvar_room_rest_night", "")
    return str(raw)


def test_simulated_quest_state_matches_exact_journal_line() -> None:
    assert _simulated_sealed_wings_objective_after_night() == EXPECTED_OBJECTIVE


def test_quest_log_apply_reads_after_telvar_room_rest_night_key() -> None:
    text = QUEST_LOG_GD.read_text(encoding="utf-8")
    assert 'lines.get("after_telvar_room_rest_night"' in text
    assert "func apply_sealed_wings_after_telvar_room_night" in text


def test_night_runner_invokes_quest_apply_after_myramar_sprite_cleanup() -> None:
    body = NIGHT_SCRIPT.read_text(encoding="utf-8")
    assert "QuestLog.apply_sealed_wings_after_telvar_room_night()" in body
    lines = body.splitlines()
    idx_queue = next(i for i, ln in enumerate(lines) if "sprite.queue_free()" in ln)
    idx_apply = next(i for i, ln in enumerate(lines) if "QuestLog.apply_sealed_wings_after_telvar_room_night()" in ln)
    assert idx_apply > idx_queue
