"""JSON save-slot loading contract enforced by CI.

Godot implementation: res://scripts/save_manager.gd (class SaveManager).
Keep behavior in sync when changing either side.
"""

from __future__ import annotations

import json
import warnings
from pathlib import Path
from typing import Any

SAVE_SLOT_VERSION = 1


def empty_save_slot() -> dict[str, Any]:
	return {"empty": True, "version": SAVE_SLOT_VERSION}


def load_save_slot(path: Path | str) -> dict[str, Any]:
	"""Load a save slot JSON file. Missing or invalid input returns empty_save_slot()."""
	p = Path(path) if not isinstance(path, Path) else path
	if str(p) == "":
		return dict(empty_save_slot())
	if not p.is_file():
		return dict(empty_save_slot())
	try:
		text = p.read_text(encoding="utf-8")
	except OSError as exc:
		warnings.warn(f"SaveManager: could not read save file (treating as empty): {p} — {exc}")
		return dict(empty_save_slot())
	try:
		data = json.loads(text)
	except json.JSONDecodeError as exc:
		warnings.warn(f"SaveManager: corrupt save JSON (treating as empty): {p} — {exc}")
		return dict(empty_save_slot())
	if not isinstance(data, dict):
		warnings.warn(f"SaveManager: save root is not an object (treating as empty): {p}")
		return dict(empty_save_slot())
	return data
