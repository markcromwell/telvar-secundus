"""Behavioral checks for Veneficturis Main Hall reception / door passage logic.

The Godot runtime lives in ``scripts/veneficturis_main_hall.gd``. This module
keeps a small Python twin of the passage state machine so CI can exercise the
rules without a Godot binary. When editing the GDScript, update
:class:`VeneficturisMainHallPassageSimulator` to stay aligned.

Structural tests assert critical snippets still exist in the source file.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.test_godot_config import MAIN_HALL_SCRIPT, PLAYER_VENEFICTURIS_SCRIPT

REPO_ROOT = Path(__file__).resolve().parents[1]


class VeneficturisMainHallPassageSimulator:
    """Minimal mirror of passage-related branches in ``veneficturis_main_hall.gd``."""

    DIALOGUE_HALT_DOOR = "Receptionist: Halt! Show your admission letter first."
    DIALOGUE_HALT_RECEPTION = (
        "Receptionist: Halt! Show your admission letter first. (Press E here with your letter.)"
    )
    DIALOGUE_NO_LETTER = "Receptionist: You have no admission letter. I cannot let you through."
    DIALOGUE_ADMITTED = "Receptionist: A letter from Myramar? Very well, proceed."
    DIALOGUE_PROCEED_READY = "Receptionist: Proceed when you are ready."

    def __init__(self) -> None:
        self.has_shown_letter = False
        self.player_has_admission_letter = True
        self.player_overlaps_reception = False
        self._door_blocker_count = 4
        self.dialogues: list[str] = []
        self.transitions: list[str] = []

    def on_door_body_entered(self, room_name: str) -> None:
        if self.has_shown_letter:
            self.transitions.append(room_name)
        else:
            self.dialogues.append(self.DIALOGUE_HALT_DOOR)

    def on_receptionist_body_entered(self) -> None:
        if not self.has_shown_letter:
            self.dialogues.append(self.DIALOGUE_HALT_RECEPTION)
        else:
            self.dialogues.append(self.DIALOGUE_PROCEED_READY)

    def try_present_admission_letter(self) -> None:
        if self.has_shown_letter:
            return
        if not self.player_overlaps_reception:
            return
        if not self.player_has_admission_letter:
            self.dialogues.append(self.DIALOGUE_NO_LETTER)
            return
        self.show_letter()

    def show_letter(self) -> None:
        self.has_shown_letter = True
        self.dialogues.append(self.DIALOGUE_ADMITTED)
        self._door_blocker_count = 0


def test_door_blocked_emits_halt_dialogue_until_letter_shown() -> None:
    sim = VeneficturisMainHallPassageSimulator()
    sim.on_door_body_entered("Library")
    assert sim.transitions == []
    assert sim.dialogues == [sim.DIALOGUE_HALT_DOOR]


def test_door_after_letter_requests_transition() -> None:
    sim = VeneficturisMainHallPassageSimulator()
    sim.has_shown_letter = True
    sim.on_door_body_entered("Tower")
    assert sim.transitions == ["Tower"]
    assert sim.dialogues == []


def test_all_four_exits_transition_when_admitted() -> None:
    sim = VeneficturisMainHallPassageSimulator()
    sim.has_shown_letter = True
    for room in ("Library", "Tower", "Classroom", "Lab"):
        sim.on_door_body_entered(room)
    assert sim.transitions == ["Library", "Tower", "Classroom", "Lab"]


def test_reception_overlap_prompts_letter_until_admitted() -> None:
    sim = VeneficturisMainHallPassageSimulator()
    sim.on_receptionist_body_entered()
    assert sim.dialogues == [sim.DIALOGUE_HALT_RECEPTION]


def test_reception_after_letter_shows_ready_message() -> None:
    sim = VeneficturisMainHallPassageSimulator()
    sim.has_shown_letter = True
    sim.on_receptionist_body_entered()
    assert sim.dialogues == [sim.DIALOGUE_PROCEED_READY]


def test_present_letter_requires_reception_overlap() -> None:
    sim = VeneficturisMainHallPassageSimulator()
    sim.player_overlaps_reception = False
    sim.try_present_admission_letter()
    assert not sim.has_shown_letter
    assert sim.dialogues == []


def test_present_letter_without_item_shows_refusal() -> None:
    sim = VeneficturisMainHallPassageSimulator()
    sim.player_overlaps_reception = True
    sim.player_has_admission_letter = False
    sim.try_present_admission_letter()
    assert not sim.has_shown_letter
    assert sim.dialogues == [sim.DIALOGUE_NO_LETTER]


def test_present_letter_with_item_grants_passage_and_clears_blockers() -> None:
    sim = VeneficturisMainHallPassageSimulator()
    sim.player_overlaps_reception = True
    sim.player_has_admission_letter = True
    sim.try_present_admission_letter()
    assert sim.has_shown_letter
    assert sim._door_blocker_count == 0
    assert sim.dialogues == [sim.DIALOGUE_ADMITTED]


def test_show_letter_is_idempotent_for_try_present() -> None:
    sim = VeneficturisMainHallPassageSimulator()
    sim.player_overlaps_reception = True
    sim.try_present_admission_letter()
    sim.try_present_admission_letter()
    assert sim.dialogues.count(sim.DIALOGUE_ADMITTED) == 1


def test_player_script_wires_letter_key_to_hall() -> None:
    text = PLAYER_VENEFICTURIS_SCRIPT.read_text(encoding="utf-8")
    assert "KEY_E" in text
    assert "try_present_admission_letter" in text


@pytest.mark.parametrize(
    "needle",
    [
        "func _on_door_body_entered",
        "if has_shown_letter:",
        "transition_requested.emit(room_name)",
        "Receptionist: Halt! Show your admission letter first.",
        "func _on_receptionist_body_entered",
        "func try_present_admission_letter",
        "get_overlapping_bodies().has(player)",
        "if not player_has_admission_letter:",
        "func show_letter()",
        "_door_blockers.clear()",
    ],
)
def test_main_hall_gdscript_retains_passage_control_flow(needle: str) -> None:
    text = MAIN_HALL_SCRIPT.read_text(encoding="utf-8")
    assert needle in text, f"missing passage-related snippet: {needle!r}"


def test_main_hall_gdscript_door_else_branch_halts_player() -> None:
    """Guards against accidentally removing the ``else`` halt on door overlap."""
    text = MAIN_HALL_SCRIPT.read_text(encoding="utf-8")
    door_fn = text.index("func _on_door_body_entered")
    show_fn = text.index("func _on_receptionist_body_entered")
    body = text[door_fn:show_fn]
    assert "if has_shown_letter:" in body
    assert "else:" in body
    assert "transition_requested.emit(room_name)" in body
    assert "dialogue_shown.emit(" in body
