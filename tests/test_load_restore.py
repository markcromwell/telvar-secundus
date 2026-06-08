"""Tests for the load screen slot selection and state restoration.

Verifies that loading a save slot restores the exact game state that was saved,
and that there is no data bleed between slots. Also includes chaos tests
for robustness.
"""

from __future__ import annotations

import copy
import json
from typing import Any

import pytest

# Duplicated from test_save_data_schema.py for test isolation.
# In a real project, these would be in a shared test utility module.

SCHEMA_VERSION = 1


def _default_save_dict() -> dict[str, Any]:
    """Mirrors SaveDataSchema.default_save_dict() in GDScript."""
    return {
        "version": SCHEMA_VERSION,
        "scene_path": "",
        "tile_coords": {"x": 0, "y": 0},
        "quest_state": {},
        "lore_entries": [],
        "inventory": {},
        "hp": 1.0,
        "max_hp": 1.0,
        "mana": 0.0,
        "max_mana": 0.0,
        "act_flags": {},
        "dialogue_flags": {},
        "play_time_seconds": 0.0,
    }


def _merge_with_defaults(data: dict) -> dict:
    """Mirrors SaveDataSchema.merge_with_defaults() in GDScript."""
    out = copy.deepcopy(_default_save_dict())
    for k, v in data.items():
        if k == "tile_coords" and isinstance(v, dict):
            merged = dict(out["tile_coords"])
            for ck, cv in v.items():
                merged[ck] = cv
            out["tile_coords"] = merged
        else:
            out[k] = v
    return out


def _deep_equal(a: Any, b: Any) -> bool:
    """Deeply compares two objects."""
    if type(a) is not type(b):
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            return float(a) == float(b)
        return False
    if isinstance(a, dict):
        if set(a) != set(b):
            return False
        return all(_deep_equal(a[k], b[k]) for k in a)
    if isinstance(a, list):
        if len(a) != len(b):
            return False
        return all(_deep_equal(x, y) for x, y in zip(a, b, strict=True))
    return a == b


# Mocking the Save/Load Manager behavior for pure Python tests
class MockSaveManager:
    """A mock of the GDScript SaveManager for testing save/load logic."""

    def __init__(self) -> None:
        self.slots: dict[int, str] = {}
        self.live_game_state: dict[str, Any] = {}

    def save_game(self, slot_index: int) -> None:
        """Saves the live_game_state to a slot as a JSON string."""
        save_data = self._export_state_to_dictionary()
        self.slots[slot_index] = self._to_json_string(save_data)

    def load_game(self, slot_index: int) -> bool:
        """Loads a slot's JSON string into the live_game_state."""
        if slot_index not in self.slots:
            return False
        json_string = self.slots[slot_index]
        loaded_data = self._from_json_string(json_string)
        if not loaded_data:
            return False
        self._populate_state_from_dictionary(loaded_data)
        return True

    def _export_state_to_dictionary(self) -> dict:
        """Mirrors SaveDataSchema.export_state_to_dictionary."""
        return copy.deepcopy(_merge_with_defaults(self.live_game_state))

    def _populate_state_from_dictionary(self, source: dict) -> None:
        """Mirrors SaveDataSchema.populate_state_from_dictionary."""
        merged = _merge_with_defaults(source)
        self.live_game_state.clear()
        for k, v in merged.items():
            self.live_game_state[k] = v

    def _to_json_string(self, data: dict) -> str:
        """Mirrors SaveDataSchema._to_json_string."""
        return json.dumps(data, separators=(",", ":"), ensure_ascii=False)

    def _from_json_string(self, text: str) -> dict:
        """Mirrors SaveDataSchema._from_json_string."""
        stripped = text.strip()
        if not stripped:
            return {}
        try:
            root = json.loads(stripped)
        except json.JSONDecodeError:
            return {}
        return root if isinstance(root, dict) else {}


@pytest.fixture
def save_payloads() -> dict[int, dict[str, Any]]:
    """Provides distinct, known-good save data payloads for 3 slots."""
    return {
        0: {
            "scene_path": "res://scenes/main_hall.tscn",
            "tile_coords": {"x": 10, "y": 20},
            "quest_state": {"main": 1},
            "inventory": {"potion": 5},
            "hp": 0.8,
            "mana": 0.9,
            "play_time_seconds": 120.5,
        },
        1: {
            "scene_path": "res://scenes/library.tscn",
            "tile_coords": {"x": 5, "y": 15},
            "quest_state": {"main": 2, "side_quest": 1},
            "inventory": {"scroll": 1, "gold": 100},
            "act_flags": {"met_librarian": True},
            "hp": 1.0,
            "mana": 0.5,
            "play_time_seconds": 3600.0,
        },
        2: {
            "scene_path": "res://scenes/overworld.tscn",
            "tile_coords": {"x": 100, "y": 200},
            "lore_entries": ["history_of_secundus"],
            "hp": 0.5,
            "max_hp": 1.2,
            "mana": 0.1,
            "max_mana": 1.2,
            "dialogue_flags": {"king_intro": True},
            "play_time_seconds": 7200.2,
        },
    }


@pytest.mark.parametrize("slot_index", [0, 1, 2])
def test_load_restores_slot_state_perfectly(
    slot_index: int, save_payloads: dict[int, dict[str, Any]]
) -> None:
    """Verify that loading a slot restores the exact state that was saved."""
    save_manager = MockSaveManager()
    original_data = save_payloads[slot_index]

    # 1. Set the live game state to the original data
    save_manager.live_game_state = copy.deepcopy(original_data)

    # 2. Save the game to the specified slot
    save_manager.save_game(slot_index)

    # 3. Clear the live state to simulate loading from scratch
    save_manager.live_game_state.clear()
    save_manager.live_game_state["version"] = 0 # Corrupt live state

    # 4. Load the game from the slot
    assert save_manager.load_game(slot_index) is True

    # 5. Assert that the restored state is identical to the original
    # The loaded data will have all default fields merged in.
    expected_full_data = _merge_with_defaults(original_data)
    assert _deep_equal(save_manager.live_game_state, expected_full_data)


def test_chaos_rapid_transitions_no_bleed() -> None:
    """Simulate rapid transitions between load slots, ensuring no data bleed."""
    save_manager = MockSaveManager()

    # Save to slot 0 with some data
    save_manager.live_game_state = {"hp": 0.5, "inventory": {"gem": 1}}
    save_manager.save_game(0)

    # Save to slot 1 with completely different data
    save_manager.live_game_state = {"hp": 1.0, "inventory": {"sword": 1}, "mana": 1.0}
    save_manager.save_game(1)

    # Load slot 0
    save_manager.load_game(0)
    state_after_load_0 = copy.deepcopy(save_manager.live_game_state)

    # Immediately load slot 1
    save_manager.load_game(1)
    state_after_load_1 = copy.deepcopy(save_manager.live_game_state)

    # Verify that the state from loading slot 0 is what we expect for slot 0
    expected_state_0 = _merge_with_defaults({"hp": 0.5, "inventory": {"gem": 1}})
    assert _deep_equal(state_after_load_0, expected_state_0)

    # Verify that the state from loading slot 1 is what we expect for slot 1
    expected_state_1 = _merge_with_defaults(
        {"hp": 1.0, "inventory": {"sword": 1}, "mana": 1.0}
    )
    assert _deep_equal(state_after_load_1, expected_state_1)

    # Final check: the two states should be different
    assert not _deep_equal(state_after_load_0, state_after_load_1)


def test_chaos_rapid_slot_clicks(save_payloads: dict[int, dict[str, Any]]) -> None:
    """Simulate rapid, repeated clicks on different slots, verifying final state."""
    save_manager = MockSaveManager()

    # 1. Pre-populate all save slots with their respective payloads
    for i in range(3):
        save_manager.live_game_state = copy.deepcopy(save_payloads[i])
        save_manager.save_game(i)

    # 2. Simulate a series of rapid, chaotic load operations
    # Pattern: 0 -> 2 -> 1 -> 2 -> 0
    save_manager.load_game(0)
    save_manager.load_game(2)
    save_manager.load_game(1)
    save_manager.load_game(2)
    save_manager.load_game(0) # Final load should be slot 0

    # 3. Verify that the final state is correctly that of the last loaded slot (0)
    expected_state = _merge_with_defaults(save_payloads[0])
    assert _deep_equal(save_manager.live_game_state, expected_state)


def test_chaos_latency_avoids_stale_state(
    save_payloads: dict[int, dict[str, Any]]
) -> None:
    """Simulate a delayed load operation to ensure stale live state is overwritten."""
    save_manager = MockSaveManager()

    # 1. Save initial state to slot 1
    original_state = save_payloads[1]
    save_manager.live_game_state = copy.deepcopy(original_state)
    save_manager.save_game(1)

    # 2. Live game state changes to something else (e.g., player moves)
    save_manager.live_game_state["tile_coords"] = {"x": 999, "y": 999}
    save_manager.live_game_state["hp"] = 0.1

    # 3. Simulate a "late" decision to load slot 1
    save_manager.load_game(1)

    # 4. Verify the live state is fully restored to the saved state, not the
    #    interim "stale" state.
    expected_state = _merge_with_defaults(original_state)
    assert _deep_equal(save_manager.live_game_state, expected_state)
    assert save_manager.live_game_state["tile_coords"]["x"] == 5 # Original value
    assert save_manager.live_game_state["hp"] == 1.0 # Original value
