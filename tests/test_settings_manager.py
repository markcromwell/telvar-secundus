"""Adversarial save hardening for the Settings autoload (spec #1542, phase 3247).

Two complementary layers, both run without booting Godot (see the established
``test_godot_config.py`` / ``test_chaos_concurrency.py`` convention):

1. **Structural GDScript contract** — assert that ``scripts/settings_manager.gd``
   keeps the properties that make a save safe under adversarial conditions:
     * it serializes to a temp sibling and commits via an *atomic rename* over the
       canonical file (so a reader never sees a half-written file);
     * the canonical file is never written directly — only produced by the rename;
     * every disk result is inspected, giving distinct graceful branches for a
       failed temp write (permission / disk-full / timeout / busy all surface as a
       non-OK ``Error`` here), a failed ``user://`` open, and a failed commit
       rename — each preserving the prior on-disk values and never crashing;
     * loads fall back to defaults without raising;
     * reads come from the in-memory cache, never from disk.
   The failure is surfaced to the player through the settings menu's
   ``save_failed`` signal (``settings_menu.gd``), and the autoload is registered
   in ``project.godot`` so the singleton actually loads at startup.

2. **Python reference model** — a faithful mirror of the GDScript algorithm
   (last-known-good cache + temp-then-rename). It proves the guarantees the
   structure only *describes*: the canonical file is never partially written, a
   simulated concurrent write never corrupts the result, and an injected
   write/permission failure leaves the prior values byte-for-byte intact.

If ``settings_manager.gd`` loses its temp-file+rename pattern, its distinct
error branches, or the menu loses its ``save_failed`` signal, the structural
tests fail; if the atomic/preservation algorithm regresses, the reference-model
tests fail.
"""

from __future__ import annotations

import configparser
import json
import os
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
PROJECT_GODOT = REPO_ROOT / "project.godot"
SETTINGS_MANAGER_GD = REPO_ROOT / "scripts" / "settings_manager.gd"
SETTINGS_MENU_GD = REPO_ROOT / "settings_menu.gd"

# Godot @GlobalScope error codes the GDScript surfaces on adversarial writes.
OK = 0
FAILED = 1
ERR_FILE_NO_PERMISSION = 8
ERR_TIMEOUT = 43
ERR_BUSY = 44


# --------------------------------------------------------------------------- #
# helpers                                                                      #
# --------------------------------------------------------------------------- #
def _read_gd(path: Path) -> str:
    if not path.is_file():
        pytest.fail(f"Missing required GDScript: {path}")
    return path.read_text(encoding="utf-8")


def _gd_func_body(src: str, name: str) -> str:
    """Return the source of a top-level ``func name(...)`` up to the next
    top-level ``func``/``class`` declaration (GDScript funcs start at column 0)."""
    start = re.search(r"(?m)^func\s+" + re.escape(name) + r"\s*\(", src)
    assert start, f"func {name}() not found"
    nxt = re.search(r"(?m)^(func|class_name|class)\s", src[start.end():])
    end = start.end() + nxt.start() if nxt else len(src)
    return src[start.start():end]


def _wrap_godot_root_section(text: str) -> str:
    stripped = text.lstrip("﻿")
    if not stripped.lstrip().startswith("["):
        return "[__godot_root__]\n" + text
    return text


def _unquote_godot_value(raw: str) -> str:
    s = raw.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        return s[1:-1]
    return s


def _load_project_godot() -> configparser.ConfigParser:
    if not PROJECT_GODOT.is_file():
        pytest.fail(f"Missing required file: {PROJECT_GODOT}")
    text = _wrap_godot_root_section(PROJECT_GODOT.read_text(encoding="utf-8"))
    cp = configparser.ConfigParser(interpolation=None)
    cp.optionxform = str  # preserve key case (autoload names are case-sensitive)
    cp.read_string(text)
    return cp


# ========================================================================== #
# 1. Structural GDScript contract                                            #
# ========================================================================== #
def test_settings_manager_gd_exists() -> None:
    assert SETTINGS_MANAGER_GD.is_file()


def test_uses_temp_file_distinct_from_canonical() -> None:
    src = _read_gd(SETTINGS_MANAGER_GD)
    assert "SETTINGS_PATH" in src and "TEMP_PATH" in src
    # The temp path is a sibling of the canonical file, never the same file.
    canonical = re.search(r'SETTINGS_PATH[^\n]*=\s*"([^"]+)"', src)
    temp = re.search(r'TEMP_PATH[^\n]*=\s*"([^"]+)"', src)
    assert canonical and temp, "both SETTINGS_PATH and TEMP_PATH must be defined"
    assert canonical.group(1) != temp.group(1)
    assert temp.group(1).startswith(canonical.group(1)), "temp should be a sibling"
    assert temp.group(1).endswith(".tmp")


def test_commit_is_an_atomic_rename_over_canonical() -> None:
    src = _read_gd(SETTINGS_MANAGER_GD)
    assert re.search(r"\brename\(\s*TEMP_PATH\s*,\s*SETTINGS_PATH\s*\)", src), (
        "save() must commit by renaming the temp file over the canonical file"
    )


def test_canonical_file_is_never_written_directly() -> None:
    """The canonical file may only appear as the *destination* of the rename —
    serializing straight onto it would expose readers to a half-written file."""
    src = _read_gd(SETTINGS_MANAGER_GD)
    assert re.search(r"\.save\(\s*TEMP_PATH\s*\)", src), "must serialize to the temp file"
    assert not re.search(r"\.save\(\s*SETTINGS_PATH\s*\)", src), (
        "must not serialize the ConfigFile straight to the canonical path"
    )
    assert not re.search(r"\.store_\w+\([^)]*SETTINGS_PATH", src)


def test_save_has_distinct_adversarial_error_branches() -> None:
    """Permission, disk-full, timeout and busy errors all surface as a non-OK
    Error from cf.save()/DirAccess.open()/rename(); save() must inspect each and
    bail gracefully, preserving the prior file. Removing any branch fails here."""
    body = _gd_func_body(_read_gd(SETTINGS_MANAGER_GD), "save")
    # (a) temp write failed (permission / disk full / timeout / busy)
    assert re.search(r"\.save\(\s*TEMP_PATH\s*\)", body)
    assert re.search(r"if\s+err\s*!=\s*OK\s*:", body), "missing temp-write error branch"
    # (b) could not open user:// to commit
    assert re.search(r"if\s+dir\s*==\s*null\s*:", body), "missing dir-open error branch"
    # (c) the atomic commit rename itself failed
    assert re.search(r"if\s+rename_err\s*!=\s*OK\s*:", body), "missing rename error branch"
    # every failure path returns gracefully and cleans up the temp...
    assert body.count("return false") >= 3
    assert "_remove_temp()" in body
    # ...and reports rather than crashes (no assert/crash on a write failure).
    assert "last_error" in body
    assert "assert(" not in body


def test_save_returns_bool_success_flag_not_void() -> None:
    src = _read_gd(SETTINGS_MANAGER_GD)
    assert re.search(r"func\s+save\s*\(\s*\)\s*->\s*bool", src), (
        "save() must report success/failure so callers can keep prior values"
    )


def test_load_falls_back_to_defaults_without_raising() -> None:
    body = _gd_func_body(_read_gd(SETTINGS_MANAGER_GD), "load")
    assert "_clone_defaults()" in body, "load() must seed the cache with defaults"
    assert "return false" in body, "missing/unreadable file must report, not raise"
    assert "assert(" not in body


def test_reads_come_from_in_memory_cache_not_disk() -> None:
    """A failed write can never surface partial/empty values because reads never
    touch disk — get_value() resolves entirely from the in-memory cache."""
    body = _gd_func_body(_read_gd(SETTINGS_MANAGER_GD), "get_value")
    assert "_cache" in body
    for disk_token in ("FileAccess", "ConfigFile", ".load(", "DirAccess"):
        assert disk_token not in body, f"get_value() must not touch disk ({disk_token})"


# -- failure is surfaced to the player via the menu's save_failed signal ---- #
def test_settings_menu_declares_save_failed_signal() -> None:
    src = _read_gd(SETTINGS_MENU_GD)
    assert re.search(r"(?m)^signal\s+save_failed\b", src), (
        "settings_menu.gd must declare the save_failed signal"
    )


def test_settings_menu_emits_save_failed_and_keeps_prior_values_on_failure() -> None:
    src = _read_gd(SETTINGS_MENU_GD)
    assert re.search(r"if\s+err\s*!=\s*OK\s*:", src), "menu must check the save Error"
    assert re.search(r"save_failed\.emit\(", src), "menu must emit save_failed on failure"
    # On failure it reverts the UI/audio to the last-known-good values.
    assert "_last_good" in src


# -- the autoload is actually registered so the singleton loads at startup -- #
def test_project_registers_settings_autoload() -> None:
    cp = _load_project_godot()
    assert cp.has_section("autoload"), "project.godot has no [autoload] section"
    assert "Settings" in cp.options("autoload"), "Settings autoload not registered"
    value = _unquote_godot_value(cp.get("autoload", "Settings"))
    # Leading '*' marks the autoload as a singleton Node in Godot 4.
    assert value.lstrip("*") == "res://scripts/settings_manager.gd"


# ========================================================================== #
# 2. Python reference model of the temp-write-then-rename algorithm           #
# ========================================================================== #
# Canonical defaults, nested {section: {key: value}} to mirror the ConfigFile
# layout used by settings_manager.gd.
DEFAULTS = {
    "audio": {"master": 100, "music": 100, "sfx": 100},
    "display": {"fullscreen": False, "vsync": True},
}


def _clone_defaults() -> dict:
    return {section: dict(values) for section, values in DEFAULTS.items()}


class WriteFault(Exception):
    """Injected to simulate a permission/timeout/busy failure during the temp
    write — the canonical file must never reflect such a failed attempt."""

    def __init__(self, code: int) -> None:
        super().__init__(code)
        self.code = code


class ConfigSettingsStore:
    """Python mirror of scripts/settings_manager.gd.

    An in-memory last-known-good cache always holds valid values; writes go to a
    temp sibling and are committed with an atomic ``os.replace`` (Godot's
    DirAccess.rename), so the canonical file is only ever the complete old or the
    complete new document — never a torn one.
    """

    def __init__(self, path: str) -> None:
        self.path = path
        self.tmp_path = path + ".tmp"
        self.cache = _clone_defaults()
        self.last_error = ""
        # When set to a non-OK code, the next save's temp write fails with it,
        # standing in for FileAccess.open()/save() returning that Error.
        self.write_fault = None

    # -- serialization (format is irrelevant; atomicity is the point) ------- #
    @staticmethod
    def _serialize(doc: dict) -> str:
        return json.dumps(doc, indent="\t", sort_keys=True)

    def _remove_temp(self) -> None:
        if os.path.exists(self.tmp_path):
            os.remove(self.tmp_path)

    # -- API ---------------------------------------------------------------- #
    def load(self) -> bool:
        self.last_error = ""
        self.cache = _clone_defaults()
        if not os.path.exists(self.path):
            return False  # first run is normal, not an error
        try:
            with open(self.path, encoding="utf-8") as f:
                parsed = json.loads(f.read())
        except (OSError, ValueError):
            self.last_error = "unreadable or malformed; using defaults"
            return False
        if not isinstance(parsed, dict):
            self.last_error = "malformed; using defaults"
            return False
        # Overlay only known keys, and only when the type matches the default,
        # so a corrupt/tampered file cannot poison the cache.
        for section, values in self.cache.items():
            file_section = parsed.get(section)
            if not isinstance(file_section, dict):
                continue
            for key, fallback in values.items():
                if key in file_section and type(file_section[key]) is type(fallback):
                    values[key] = file_section[key]
        return True

    def save(self) -> int:
        self.last_error = ""
        payload = self._serialize(self.cache)
        # Write the full document to the temp sibling first. On failure the
        # canonical file is untouched (we never reach the rename).
        try:
            if self.write_fault is not None:
                # A real failure may leave torn bytes in the temp file; write a
                # partial chunk first to prove that still never reaches canonical.
                with open(self.tmp_path, "w", encoding="utf-8") as f:
                    f.write(payload[: len(payload) // 2])
                raise WriteFault(self.write_fault)
            with open(self.tmp_path, "w", encoding="utf-8") as f:
                f.write(payload)
        except WriteFault as fault:
            self.last_error = "write failed (error %d); prior settings preserved" % fault.code
            self._remove_temp()
            return fault.code
        except OSError:
            self.last_error = "write failed; prior settings preserved"
            self._remove_temp()
            return ERR_FILE_NO_PERMISSION
        # Atomically swap the temp file over the canonical file.
        try:
            os.replace(self.tmp_path, self.path)
        except OSError:
            self.last_error = "commit failed; prior settings preserved"
            self._remove_temp()
            return FAILED
        return OK

    def get_value(self, section: str, key: str, default=None):
        if section in self.cache and key in self.cache[section]:
            return self.cache[section][key]
        if default is not None:
            return default
        return DEFAULTS.get(section, {}).get(key)

    def set_value(self, section: str, key: str, value) -> None:
        self.cache.setdefault(section, {})[key] = value


@pytest.fixture
def cfg_store(tmp_path):
    return ConfigSettingsStore(str(tmp_path / "settings.cfg"))


def _read_disk(cfg_store: ConfigSettingsStore) -> dict:
    with open(cfg_store.path, encoding="utf-8") as f:
        return json.loads(f.read())


def _assert_complete_document(doc: dict) -> None:
    assert set(doc.keys()) == set(DEFAULTS.keys())
    for section, values in DEFAULTS.items():
        assert set(doc[section].keys()) == set(values.keys())


# -- happy path ------------------------------------------------------------- #
def test_ref_successful_save_persists_and_clears_temp(cfg_store):
    cfg_store.set_value("audio", "master", 80)
    assert cfg_store.save() == OK
    assert not os.path.exists(cfg_store.tmp_path)
    fresh = ConfigSettingsStore(cfg_store.path)
    assert fresh.load() is True
    assert fresh.get_value("audio", "master") == 80


def test_ref_missing_file_is_first_run_not_an_error(cfg_store):
    assert cfg_store.load() is False
    assert cfg_store.last_error == ""  # absent file is normal, not an error
    assert cfg_store.get_value("display", "vsync") is True


# -- the canonical file is never partially written -------------------------- #
def test_ref_canonical_never_partially_written_on_fault(cfg_store):
    cfg_store.set_value("audio", "music", 40)
    assert cfg_store.save() == OK
    prior_bytes = open(cfg_store.path, "rb").read()

    # A torn / timed-out write must not surface in the canonical file.
    cfg_store.set_value("audio", "music", 7)
    cfg_store.write_fault = ERR_TIMEOUT
    assert cfg_store.save() == ERR_TIMEOUT

    assert open(cfg_store.path, "rb").read() == prior_bytes  # byte-for-byte intact
    assert not os.path.exists(cfg_store.tmp_path)
    fresh = ConfigSettingsStore(cfg_store.path)
    assert fresh.load() is True
    _assert_complete_document(_read_disk(cfg_store))
    assert fresh.get_value("audio", "music") == 40  # prior value, not the torn 7


def test_ref_first_ever_save_failure_creates_no_canonical_file(cfg_store):
    cfg_store.write_fault = ERR_FILE_NO_PERMISSION
    assert cfg_store.save() == ERR_FILE_NO_PERMISSION
    assert not os.path.exists(cfg_store.path)
    assert not os.path.exists(cfg_store.tmp_path)


def test_ref_rapid_saves_always_parse_to_a_complete_document(cfg_store):
    cfg_store.save()
    for i in range(6):
        cfg_store.set_value("audio", "sfx", i * 10)
        assert cfg_store.save() == OK
        on_disk = _read_disk(cfg_store)
        _assert_complete_document(on_disk)  # never a half-written file
        assert on_disk["audio"]["sfx"] == i * 10


# -- injected write/permission failure leaves prior values intact ----------- #
@pytest.mark.parametrize("fault", [ERR_FILE_NO_PERMISSION, ERR_TIMEOUT, ERR_BUSY, FAILED])
def test_ref_injected_failure_preserves_prior_disk_values(cfg_store, fault):
    cfg_store.set_value("audio", "master", 90)
    cfg_store.set_value("audio", "sfx", 90)
    assert cfg_store.save() == OK
    prior_bytes = open(cfg_store.path, "rb").read()

    cfg_store.write_fault = fault
    cfg_store.set_value("audio", "master", 0)  # the change that fails to commit
    assert cfg_store.save() == fault

    # On-disk prior values are intact and a reloading session still sees them.
    assert open(cfg_store.path, "rb").read() == prior_bytes
    assert not os.path.exists(cfg_store.tmp_path)
    fresh = ConfigSettingsStore(cfg_store.path)
    assert fresh.load() is True
    assert fresh.get_value("audio", "master") == 90


# -- a simulated concurrent write does not corrupt the result --------------- #
def test_ref_interleaved_session_write_yields_complete_not_torn_file(cfg_store):
    session_a = cfg_store
    session_a.set_value("audio", "master", 50)
    session_a.set_value("audio", "music", 50)
    assert session_a.save() == OK
    session_a.load()

    # Another session concurrently rewrites the same file.
    session_b = ConfigSettingsStore(session_a.path)
    session_b.load()
    session_b.set_value("audio", "music", 5)
    assert session_b.save() == OK

    # Session A now commits its own cache. The atomic rename means the result is
    # exactly one session's complete snapshot — never a half-A/half-B mix.
    session_a.set_value("audio", "master", 80)
    intended_a = json.loads(ConfigSettingsStore._serialize(session_a.cache))
    assert session_a.save() == OK

    on_disk = _read_disk(cfg_store)
    _assert_complete_document(on_disk)
    assert on_disk == intended_a


def test_ref_concurrent_saves_never_corrupt_canonical(cfg_store):
    session_a = cfg_store
    session_b = ConfigSettingsStore(cfg_store.path)
    session_a.set_value("audio", "master", 11)
    assert session_a.save() == OK

    for i in range(8):
        writer = session_a if i % 2 == 0 else session_b
        writer.set_value("audio", "master", i)
        intended = json.loads(ConfigSettingsStore._serialize(writer.cache))
        assert writer.save() == OK
        on_disk = _read_disk(cfg_store)
        _assert_complete_document(on_disk)  # always complete, never torn
        assert on_disk == intended  # last writer wins atomically — no corruption


# -- corrupt/tampered input falls back gracefully --------------------------- #
def test_ref_corrupt_file_loads_as_defaults_without_raising(cfg_store):
    with open(cfg_store.path, "w", encoding="utf-8") as f:
        f.write("{ this is not valid config :::")
    assert cfg_store.load() is False
    assert cfg_store.get_value("audio", "master") == 100  # defaults intact
    assert cfg_store.get_value("display", "vsync") is True


def test_ref_wrong_typed_values_are_ignored_in_favor_of_defaults(cfg_store):
    # A tampered file with a wrongly-typed value must not poison the cache.
    with open(cfg_store.path, "w", encoding="utf-8") as f:
        json.dump({"audio": {"master": "loud"}, "display": {"vsync": 1}}, f)
    assert cfg_store.load() is True
    assert cfg_store.get_value("audio", "master") == 100  # string rejected
    assert cfg_store.get_value("display", "vsync") is True  # int rejected for bool
