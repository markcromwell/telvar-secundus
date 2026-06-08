"""Shared helpers and fixtures for overworld<->interior transition tests.

Centralizes the Godot INI parsing logic already proven in
``tests/test_godot_config.py`` (root-section wrapping + value unquoting) so the
autosave and music transition test modules can be developed independently
without duplicating config-parsing code.

Exposes:
  - ``load_godot_ini(path)`` / ``unquote_godot_value(raw)``: Godot-aware parsing.
  - ``declared_autoloads(cp=None)``: autoload names declared in project.godot
    (e.g. the QuestManager save/load autoload and the ambient music system).
  - ``save_slot_dir`` pytest fixture: an isolated tmp directory standing in for
    the save-slot folder, used to assert autosave file counts.
"""

from __future__ import annotations

import configparser
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
PROJECT_GODOT = REPO_ROOT / "project.godot"


def wrap_godot_root_section(text: str) -> str:
    """Godot may place key=value pairs before the first [section]; ConfigParser requires a section."""
    stripped = text.lstrip("\ufeff")
    if not stripped.lstrip().startswith("["):
        return "[__godot_root__]\n" + text
    return text


def unquote_godot_value(raw: str) -> str:
    """Strip a single matching pair of surrounding single or double quotes."""
    s = raw.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        return s[1:-1]
    return s


def load_godot_ini(path: Path) -> configparser.ConfigParser:
    """Parse a Godot INI file (project.godot, export_presets.cfg) with ConfigParser.

    Mirrors ``tests/test_godot_config.py``: project.godot's leading root keys are
    wrapped in a synthetic section and interpolation is disabled.
    """
    if not path.is_file():
        pytest.fail(f"Missing required file: {path}")
    text = path.read_text(encoding="utf-8")
    if path.name == "project.godot":
        text = wrap_godot_root_section(text)
    cp = configparser.ConfigParser(interpolation=None)
    # Preserve key case: Godot autoload singleton names (Menu, QuestManager) are
    # case-sensitive. The keys test_godot_config reads are already lowercase, so
    # this matches its behavior for those lookups.
    cp.optionxform = str
    cp.read_string(text)
    return cp


def declared_autoloads(cp: configparser.ConfigParser | None = None) -> list[str]:
    """Return the autoload singleton names declared in project.godot's [autoload].

    Returns an empty list when no [autoload] section is present. The synthetic
    root-section key (config_version etc.) never appears here.
    """
    if cp is None:
        cp = load_godot_ini(PROJECT_GODOT)
    if not cp.has_section("autoload"):
        return []
    return list(cp.options("autoload"))


@pytest.fixture
def save_slot_dir(tmp_path: Path) -> Path:
    """An isolated, empty save-slot directory for asserting autosave file counts.

    Backed by pytest's per-test ``tmp_path`` so each test gets a fresh folder and
    duplicate-save assertions cannot leak between tests.

    Test modules opt in by importing the fixture into their namespace, e.g.
    ``from tests._transition_support import save_slot_dir  # noqa: F401``.
    """
    slot_dir = tmp_path / "save_slots"
    slot_dir.mkdir()
    return slot_dir
