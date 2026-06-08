import json
import os
import time
import pytest
from unittest.mock import patch

# This is a Python implementation mirroring the logic from save_system.gd
# It allows testing the save/load flow without running the Godot engine.
class SaveSystem:
    AUTOSAVE_SLOT = 0
    MIN_MANUAL_SLOT = 1
    MAX_MANUAL_SLOT = 3
    _SAVE_FILE_PATTERN = "save_slot_%d.json"

    def __init__(self, path):
        self.save_path = path
        self.last_save_error = ""
        self.last_load_error = ""

    def _slot_path(self, slot: int) -> str:
        return os.path.join(self.save_path, self._SAVE_FILE_PATTERN % slot)

    def is_slot_valid(self, slot: int) -> bool:
        return self.AUTOSAVE_SLOT <= slot <= self.MAX_MANUAL_SLOT

    def get_default_save_data(self) -> dict:
        return {
            "schema_version": 1,
            "player_pos": {"x": 0.0, "y": 0.0},
            "quest_flags": {},
            "lore_unlocked": [],
            "inventory": [],
            "current_scene": "",
            "play_time": 0.0,
            "game_complete": False,
            "dark_robe_unlocked": False,
        }

    def merge_with_defaults(self, partial: dict) -> dict:
        merged = self.get_default_save_data()
        merged.update(partial)
        return merged

    def _validate_payload(self, payload: dict) -> str:
        if "play_time" in payload and not isinstance(payload["play_time"], (int, float)):
            return "Invalid play_time type."
        if "game_complete" in payload and not isinstance(payload["game_complete"], bool):
            return "Invalid game_complete type."
        if "dark_robe_unlocked" in payload and not isinstance(payload["dark_robe_unlocked"], bool):
            return "Invalid dark_robe_unlocked type."
        if "player_pos" in payload and not isinstance(payload["player_pos"], dict):
            return "Invalid player_pos type."
        if "quest_flags" in payload and not isinstance(payload["quest_flags"], dict):
            return "Invalid quest_flags type."
        if "lore_unlocked" in payload and not isinstance(payload["lore_unlocked"], list):
            return "Invalid lore_unlocked type."
        if "inventory" in payload and not isinstance(payload["inventory"], list):
            return "Invalid inventory type."
        if "current_scene" in payload and not isinstance(payload["current_scene"], str):
            return "Invalid current_scene type."
        return ""

    def save_to_slot(self, slot: int, data: dict) -> bool:
        self.last_save_error = ""
        if not self.is_slot_valid(slot):
            self.last_save_error = "Invalid save slot index."
            return False
        
        merged = self.merge_with_defaults(data)
        err = self._validate_payload(merged)
        if err:
            self.last_save_error = err
            return False

        path = self._slot_path(slot)
        try:
            with open(path, "w") as f:
                json.dump(merged, f, indent=4)
        except IOError as e:
            self.last_save_error = f"Could not open save file for writing: {path} ({e})"
            return False
        return True

    def load_from_slot(self, slot: int) -> dict:
        self.last_load_error = ""
        if not self.is_slot_valid(slot):
            self.last_load_error = "Invalid save slot index."
            return self.get_default_save_data()

        path = self._slot_path(slot)
        if not os.path.exists(path):
            return self.get_default_save_data()

        try:
            with open(path, "r") as f:
                parsed = json.load(f)
        except (IOError, json.JSONDecodeError):
            self.last_load_error = "Could not read or parse save file."
            return self.get_default_save_data()

        if not isinstance(parsed, dict):
            self.last_load_error = "Save file root must be a JSON object."
            return self.get_default_save_data()

        err = self._validate_payload(parsed)
        if err:
            self.last_load_error = err
            return self.get_default_save_data()

        return self.merge_with_defaults(parsed)


def test_latency(tmp_path):
    """Simulates load latency affecting a subsequent save, asserting state consistency."""
    save_system = SaveSystem(tmp_path)
    slot = 1
    
    state_v1 = save_system.get_default_save_data()
    state_v1["play_time"] = 100.0
    state_v1["current_scene"] = "res://scenes/world/world.tscn"
    assert save_system.save_to_slot(slot, state_v1)
    
    loaded_data = save_system.load_from_slot(slot)
    time.sleep(0.05)
    
    state_v2 = loaded_data
    state_v2["play_time"] += 50.0
    state_v2["inventory"].append("item_key")
    assert save_system.save_to_slot(slot, state_v2)
    
    final_data = save_system.load_from_slot(slot)
    assert final_data["play_time"] == 150.0
    assert final_data["inventory"] == ["item_key"]
    assert final_data["current_scene"] == state_v1["current_scene"]


def test_rapid_transition(tmp_path):
    """Simulates rapid transitions leading to interleaved I/O, asserting no state corruption."""
    save_system = SaveSystem(tmp_path)
    slot_a, slot_b = 1, 2

    state_a = save_system.get_default_save_data()
    state_a["current_scene"] = "scene_A"
    assert save_system.save_to_slot(slot_a, state_a)

    state_b = save_system.get_default_save_data()
    state_b["current_scene"] = "scene_B"
    assert save_system.save_to_slot(slot_b, state_b)

    loaded_a = save_system.load_from_slot(slot_a)
    save_system.load_from_slot(slot_b)
    
    loaded_a["play_time"] = 99
    assert save_system.save_to_slot(slot_a, loaded_a)

    final_a = save_system.load_from_slot(slot_a)
    final_b = save_system.load_from_slot(slot_b)

    assert final_a["current_scene"] == "scene_A"
    assert final_a["play_time"] == 99
    assert final_b["current_scene"] == "scene_B"
    assert final_b["play_time"] == 0.0


def test_repeated_slot_clicks(tmp_path):
    """Simulates repeated slot clicks, with a mock UI debounce to ensure a single write."""
    save_system = SaveSystem(tmp_path)
    slot = 1
    state = {"play_time": 789}

    class MockUI:
        def __init__(self, system):
            self.save_system = system
            self.save_button_disabled = False

        def on_save_click(self, s, d):
            if self.save_button_disabled:
                return 
            self.save_button_disabled = True
            try:
                self.save_system.save_to_slot(s, d)
            finally:
                # In a real UI, this might be re-enabled after a delay or success signal
                pass

    with patch.object(save_system, 'save_to_slot', wraps=save_system.save_to_slot) as mocked_save:
        mock_ui = MockUI(save_system)

        # Simulate two rapid clicks
        mock_ui.on_save_click(slot, state)
        mock_ui.on_save_click(slot, state)

        mocked_save.assert_called_once()

    # Verify that the single write was correct
    final_data = save_system.load_from_slot(slot)
    assert final_data["play_time"] == 789
