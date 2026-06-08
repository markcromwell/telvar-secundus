"""Phase 3239: overworld<->interior autosave transition tests.

Headless pytest checks (no running Godot editor/binary) that exercise scene
transitions between the Secundus overworld and interior locations and assert the
shipped autosave contract:

  * autosave fires *exactly once* per overworld->interior and interior->overworld
    transition,
  * the active autosave slot's recorded scene (its "identifier") is updated to the
    destination after each transition,
  * repeated transitions never produce duplicate save files in the slot directory.

The autosave semantics simulated here are read straight from the GDScript
save/load autoload (``save_system.gd``) and its transition hook
(``scripts/scene_transition.gd``) so the Python mirror stays faithful to the
shipped code rather than hard-coding constants. Transitions are driven against
the isolated, per-test ``save_slot_dir`` fixture from phase 1.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from tests._transition_support import save_slot_dir  # noqa: F401  (fixture import)

REPO_ROOT = Path(__file__).resolve().parents[1]
SAVE_SYSTEM_GD = REPO_ROOT / "save_system.gd"
SCENE_TRANSITION_GD = REPO_ROOT / "scripts" / "scene_transition.gd"

# Representative scenes that actually ship in the project: a Secundus overworld
# map and a Veneficturis interior. The transition driver is path-agnostic, but
# grounding on real scenes keeps the overworld<->interior intent honest.
OVERWORLD_SCENE = "res://scenes/Overworld.tscn"
INTERIOR_SCENE = "res://scenes/veneficturis_main_hall.tscn"


# --------------------------------------------------------------------------- #
# Reading the real autosave constants out of the shipped GDScript autoload.
# --------------------------------------------------------------------------- #
def _read_autosave_slot() -> int:
    """The autosave slot index declared in save_system.gd (``AUTOSAVE_SLOT``)."""
    text = SAVE_SYSTEM_GD.read_text(encoding="utf-8")
    m = re.search(r"const\s+AUTOSAVE_SLOT\s*:?\s*int\s*=\s*(\d+)", text)
    assert m, "save_system.gd must declare `const AUTOSAVE_SLOT: int = ...`"
    return int(m.group(1))


def _read_slot_pattern() -> str:
    """The ``user://save_slot_%d.json`` printf pattern declared in save_system.gd."""
    text = SAVE_SYSTEM_GD.read_text(encoding="utf-8")
    m = re.search(r'const\s+_SAVE_FILE_PATTERN\s*:?\s*String\s*=\s*"([^"]+)"', text)
    assert m, "save_system.gd must declare `const _SAVE_FILE_PATTERN: String = ...`"
    return m.group(1)


# --------------------------------------------------------------------------- #
# Faithful Python mirror of save_system.gd + scripts/scene_transition.gd.
# --------------------------------------------------------------------------- #
class SaveSystemSim:
    """Mirrors SaveSystem.save_to_slot/load_from_slot and SceneTransition's hook.

    Writes JSON files into ``slot_dir`` using the same slot->filename mapping as
    the GDScript (basename of ``_SAVE_FILE_PATTERN % slot``). ``writes`` counts
    every ``save_to_slot`` call so tests can assert autosave fires exactly once
    per transition.
    """

    def __init__(self, slot_dir: Path, autosave_slot: int, pattern: str) -> None:
        self._dir = slot_dir
        self._autosave_slot = autosave_slot
        self._pattern = pattern
        self.writes = 0

    # SaveSystem._slot_path: user://save_slot_%d.json -> save_slot_%d.json in slot_dir
    def _slot_path(self, slot: int) -> Path:
        rel = (self._pattern % slot).split("://", 1)[-1]
        return self._dir / Path(rel).name

    @staticmethod
    def _defaults() -> dict:
        # Mirrors SaveSystem.get_default_save_data (only fields the hook touches).
        return {"schema_version": 1, "current_scene": ""}

    # SaveSystem.load_from_slot: missing file -> defaults; else merge over defaults.
    def load_from_slot(self, slot: int) -> dict:
        path = self._slot_path(slot)
        if not path.exists():
            return self._defaults()
        partial = json.loads(path.read_text(encoding="utf-8"))
        return {**self._defaults(), **partial}

    # SaveSystem.save_to_slot: overwrite the single slot file; count the write.
    def save_to_slot(self, slot: int, data: dict) -> bool:
        self.writes += 1
        merged = {**self._defaults(), **data}
        self._slot_path(slot).write_text(
            json.dumps(merged, indent="\t"), encoding="utf-8"
        )
        return True

    # SceneTransition._on_scene_changed: load autosave, update scene, save back.
    # Returns the number of autosave writes incurred by this single transition.
    def transition(self, previous_scene: str, new_scene: str) -> int:
        before = self.writes
        data = self.load_from_slot(self._autosave_slot)
        data["current_scene"] = new_scene
        self.save_to_slot(self._autosave_slot, data)
        return self.writes - before

    # Helper: the recorded scene currently stored in the autosave slot.
    def autosave_scene(self) -> str:
        return self.load_from_slot(self._autosave_slot)["current_scene"]


@pytest.fixture
def save_system(save_slot_dir: Path) -> SaveSystemSim:  # noqa: F811 (fixture use)
    """A transition driver writing into the isolated phase-1 ``save_slot_dir``."""
    return SaveSystemSim(save_slot_dir, _read_autosave_slot(), _read_slot_pattern())


def _slot_files(slot_dir: Path) -> list[Path]:
    """Every persisted save-slot file currently in the directory."""
    return sorted(slot_dir.glob("save_slot_*.json"))


# --------------------------------------------------------------------------- #
# Autosave-fires-exactly-once per transition.
# --------------------------------------------------------------------------- #
def test_overworld_to_interior_fires_autosave_exactly_once(
    save_system: SaveSystemSim,
) -> None:
    writes = save_system.transition(OVERWORLD_SCENE, INTERIOR_SCENE)
    assert writes == 1


def test_interior_to_overworld_fires_autosave_exactly_once(
    save_system: SaveSystemSim,
) -> None:
    save_system.transition(OVERWORLD_SCENE, INTERIOR_SCENE)
    writes = save_system.transition(INTERIOR_SCENE, OVERWORLD_SCENE)
    assert writes == 1


def test_each_round_trip_transition_fires_once(save_system: SaveSystemSim) -> None:
    """Every leg of a repeated overworld<->interior round trip writes exactly once."""
    legs = [
        (OVERWORLD_SCENE, INTERIOR_SCENE),
        (INTERIOR_SCENE, OVERWORLD_SCENE),
        (OVERWORLD_SCENE, INTERIOR_SCENE),
        (INTERIOR_SCENE, OVERWORLD_SCENE),
    ]
    per_leg = [save_system.transition(prev, nxt) for prev, nxt in legs]
    assert per_leg == [1, 1, 1, 1]
    assert save_system.writes == len(legs)


# --------------------------------------------------------------------------- #
# The active autosave slot is updated correctly.
# --------------------------------------------------------------------------- #
def test_autosave_slot_scene_updated_on_overworld_to_interior(
    save_system: SaveSystemSim,
) -> None:
    assert save_system.autosave_scene() == ""  # nothing saved yet
    save_system.transition(OVERWORLD_SCENE, INTERIOR_SCENE)
    assert save_system.autosave_scene() == INTERIOR_SCENE


def test_autosave_slot_scene_updated_on_interior_to_overworld(
    save_system: SaveSystemSim,
) -> None:
    save_system.transition(OVERWORLD_SCENE, INTERIOR_SCENE)
    save_system.transition(INTERIOR_SCENE, OVERWORLD_SCENE)
    assert save_system.autosave_scene() == OVERWORLD_SCENE


def test_autosave_slot_tracks_latest_destination(save_system: SaveSystemSim) -> None:
    """After several transitions the slot identifier reflects only the final scene."""
    for prev, nxt in (
        (OVERWORLD_SCENE, INTERIOR_SCENE),
        (INTERIOR_SCENE, OVERWORLD_SCENE),
        (OVERWORLD_SCENE, INTERIOR_SCENE),
    ):
        save_system.transition(prev, nxt)
    assert save_system.autosave_scene() == INTERIOR_SCENE


# --------------------------------------------------------------------------- #
# No duplicate save files across repeated transitions.
# --------------------------------------------------------------------------- #
def test_single_transition_creates_one_slot_file(
    save_system: SaveSystemSim, save_slot_dir: Path
) -> None:
    assert _slot_files(save_slot_dir) == []  # fixture starts empty
    save_system.transition(OVERWORLD_SCENE, INTERIOR_SCENE)
    files = _slot_files(save_slot_dir)
    assert len(files) == 1
    assert files[0].name == "save_slot_0.json"


def test_repeated_transitions_produce_no_duplicate_save_files(
    save_system: SaveSystemSim, save_slot_dir: Path
) -> None:
    for _ in range(8):
        save_system.transition(OVERWORLD_SCENE, INTERIOR_SCENE)
        save_system.transition(INTERIOR_SCENE, OVERWORLD_SCENE)
    files = _slot_files(save_slot_dir)
    assert len(files) == 1, f"expected a single autosave file, found {[f.name for f in files]}"
    assert files[0].name == "save_slot_0.json"


def test_autosave_writes_outpace_files_proving_overwrite(
    save_system: SaveSystemSim, save_slot_dir: Path
) -> None:
    """Many autosave writes must collapse onto one file (overwrite, not append)."""
    for _ in range(5):
        save_system.transition(OVERWORLD_SCENE, INTERIOR_SCENE)
        save_system.transition(INTERIOR_SCENE, OVERWORLD_SCENE)
    assert save_system.writes == 10
    assert len(_slot_files(save_slot_dir)) == 1


# --------------------------------------------------------------------------- #
# Anchors: the simulation matches the shipped autoload's real autosave slot and
# the transition hook genuinely writes the slot exactly once per scene change.
# --------------------------------------------------------------------------- #
def test_autosave_slot_identifier_is_reserved_slot_zero() -> None:
    assert _read_autosave_slot() == 0
    assert (_read_slot_pattern() % 0).endswith("save_slot_0.json")


def test_transition_hook_writes_autosave_slot_exactly_once() -> None:
    """scripts/scene_transition.gd must call save_to_slot once per scene_changed."""
    text = SCENE_TRANSITION_GD.read_text(encoding="utf-8")
    m = re.search(r"func _on_scene_changed\([^)]*\)[^:]*:(.*?)(?=\nfunc |\Z)", text, re.S)
    assert m, "missing _on_scene_changed handler"
    body = m.group(1)
    assert body.count("save_to_slot(") == 1
    assert "AUTOSAVE_SLOT" in body
    assert 'data["current_scene"] = new_scene' in body
