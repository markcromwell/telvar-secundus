"""Contract tests for save slot JSON loading (see tests/save_manager_contract.py)."""

from __future__ import annotations

import json
import warnings
from pathlib import Path

import pytest

from tests.save_manager_contract import empty_save_slot, load_save_slot


def test_missing_file_returns_empty_slot(tmp_path: Path) -> None:
	missing = tmp_path / "nope.json"
	out = load_save_slot(missing)
	assert out == empty_save_slot()


def test_malformed_json_logs_warning_and_returns_empty_slot(tmp_path: Path) -> None:
	bad = tmp_path / "bad.json"
	bad.write_text("{ not json", encoding="utf-8")
	with warnings.catch_warnings(record=True) as wrec:
		warnings.simplefilter("always")
		out = load_save_slot(bad)
	assert out == empty_save_slot()
	assert len(wrec) == 1
	assert "corrupt save json" in str(wrec[0].message).lower()


def test_valid_json_loads_without_data_loss(tmp_path: Path) -> None:
	good = tmp_path / "good.json"
	payload = {"empty": False, "version": 1, "player": "telvar", "scene": "secundus"}
	good.write_text(json.dumps(payload), encoding="utf-8")
	assert load_save_slot(good) == payload


def test_non_object_json_returns_empty_slot(tmp_path: Path) -> None:
	arr = tmp_path / "array.json"
	arr.write_text("[1, 2, 3]", encoding="utf-8")
	with warnings.catch_warnings(record=True) as wrec:
		warnings.simplefilter("always")
		out = load_save_slot(arr)
	assert out == empty_save_slot()
	assert any("not an object" in str(w.message).lower() for w in wrec)
