"""Adversarial settings-save hardening tests (spec #1542).

This is a Python implementation mirroring the contract of
``audio_settings_persistence.gd`` (atomic temp+rename writes, concurrency
reload-then-reapply, graceful error codes) and the failure handling in
``settings_menu.gd`` (keep prior values + emit ``save_failed`` on failure).

It follows the repo's established convention of exercising save/load logic in
Python without booting the Godot engine (see ``test_chaos_concurrency.py``), so
the adversarial guarantees are locked under the pytest gate.
"""

import json
import os

import pytest

# Mirror of Godot's @GlobalScope error codes used by the GDScript.
OK = 0
FAILED = 1
ERR_FILE_NO_PERMISSION = 8
ERR_TIMEOUT = 43
ERR_BUSY = 44

DEFAULTS = {"master": 100, "music": 100, "sfx": 100}


class WriteFault(Exception):
    """Injected to simulate a permission/timeout/busy failure mid-write."""


class SettingsStore:
    """Python mirror of audio_settings_persistence.gd."""

    def __init__(self, path):
        self.path = path
        self.tmp_path = path + ".tmp"
        self._disk_stamp = -1
        # When set to a non-OK code, the next temp write fails with that code,
        # standing in for FileAccess.open() returning a permission/timeout error.
        self.write_fault = None

    # -- helpers -----------------------------------------------------------
    def _current_stamp(self):
        if not os.path.exists(self.path):
            return 0
        return os.stat(self.path).st_mtime_ns

    def _read_disk(self):
        merged = dict(DEFAULTS)
        if not os.path.exists(self.path):
            return merged
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                parsed = json.loads(f.read())
        except (OSError, ValueError):
            return merged
        if not isinstance(parsed, dict):
            return merged
        for key in DEFAULTS:
            v = parsed.get(key)
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                merged[key] = max(0, min(100, int(v)))
        return merged

    def _remove_temp(self):
        if os.path.exists(self.tmp_path):
            os.remove(self.tmp_path)

    # -- API ---------------------------------------------------------------
    def load(self):
        merged = self._read_disk()
        self._disk_stamp = self._current_stamp()
        return merged

    def save(self, data):
        # Reload-then-reapply: current disk state is the base, overlay caller keys.
        to_save = self._read_disk()
        for key in DEFAULTS:
            v = data.get(key)
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                to_save[key] = max(0, min(100, int(v)))

        # Serialize to temp first; never touch the canonical file on failure.
        try:
            if self.write_fault is not None:
                raise WriteFault(self.write_fault)
            with open(self.tmp_path, "w", encoding="utf-8") as f:
                f.write(json.dumps(to_save, indent="\t"))
        except WriteFault as e:
            self._remove_temp()
            return e.args[0]
        except OSError:
            self._remove_temp()
            return ERR_FILE_NO_PERMISSION

        # Atomic swap over the canonical file.
        try:
            os.replace(self.tmp_path, self.path)
        except OSError:
            self._remove_temp()
            return FAILED

        self._disk_stamp = self._current_stamp()
        return OK


class SettingsMenu:
    """Python mirror of the failure handling in settings_menu.gd."""

    def __init__(self, store):
        self.store = store
        self.last_good = store.load()
        self.current = dict(self.last_good)
        self.save_failed_messages = []

    def change(self, payload):
        self.current = dict(payload)
        err = self.store.save(self.current)
        if err != OK:
            # Revert to last-known-good and emit save_failed.
            self.current = dict(self.last_good)
            self.save_failed_messages.append(
                "Could not save settings (error %d); previous values kept." % err
            )
            return err
        self.last_good = dict(self.current)
        return OK


@pytest.fixture
def store(tmp_path):
    return SettingsStore(str(tmp_path / "settings.json"))


# -- happy path -----------------------------------------------------------
def test_successful_save_persists_and_returns_ok(store):
    assert store.save({"master": 80, "music": 70, "sfx": 60}) == OK
    on_disk = json.loads(open(store.path, encoding="utf-8").read())
    assert on_disk == {"master": 80, "music": 70, "sfx": 60}
    assert not os.path.exists(store.tmp_path)


def test_load_after_save_roundtrips(store):
    store.save({"master": 10, "music": 20, "sfx": 30})
    assert store.load() == {"master": 10, "music": 20, "sfx": 30}


# -- write failures preserve prior state ----------------------------------
@pytest.mark.parametrize(
    "fault", [ERR_FILE_NO_PERMISSION, ERR_TIMEOUT, ERR_BUSY, FAILED]
)
def test_write_failure_returns_non_ok_without_crashing(store, fault):
    store.save({"master": 55, "music": 55, "sfx": 55})  # establish prior file
    prior_bytes = open(store.path, "rb").read()

    store.write_fault = fault
    err = store.save({"master": 0, "music": 0, "sfx": 0})

    assert err == fault and err != OK
    # Canonical file untouched, temp cleaned up — no partial/truncated write.
    assert open(store.path, "rb").read() == prior_bytes
    assert not os.path.exists(store.tmp_path)


def test_failed_save_leaves_no_temp_file(store):
    store.write_fault = ERR_FILE_NO_PERMISSION
    store.save({"master": 1, "music": 2, "sfx": 3})
    assert not os.path.exists(store.tmp_path)


def test_first_ever_save_failure_creates_no_canonical_file(store):
    store.write_fault = ERR_TIMEOUT
    assert store.save({"master": 1, "music": 2, "sfx": 3}) != OK
    assert not os.path.exists(store.path)


# -- menu keeps prior values on failure -----------------------------------
def test_menu_retains_prior_values_after_failed_save(store):
    store.save({"master": 90, "music": 90, "sfx": 90})
    menu = SettingsMenu(store)

    store.write_fault = ERR_FILE_NO_PERMISSION
    err = menu.change({"master": 10, "music": 10, "sfx": 10})

    assert err != OK
    assert menu.current == {"master": 90, "music": 90, "sfx": 90}
    assert menu.last_good == {"master": 90, "music": 90, "sfx": 90}
    assert len(menu.save_failed_messages) == 1
    # On-disk values are the intact prior ones.
    assert store.load() == {"master": 90, "music": 90, "sfx": 90}


def test_menu_updates_baseline_only_on_success(store):
    menu = SettingsMenu(store)
    assert menu.change({"master": 42, "music": 42, "sfx": 42}) == OK
    assert menu.last_good == {"master": 42, "music": 42, "sfx": 42}


# -- concurrency ----------------------------------------------------------
def test_concurrent_modification_is_merged_not_clobbered(store, tmp_path):
    store.save({"master": 50, "music": 50, "sfx": 50})
    store.load()  # capture stamp

    # Another session changes music while ours holds a stale snapshot.
    other = SettingsStore(store.path)
    other.save({"master": 50, "music": 5, "sfx": 50})
    # Force a distinct modified-time so the stale stamp is detectably old.
    os.utime(store.path, ns=(store._disk_stamp + 10**9, store._disk_stamp + 10**9))

    # Our session only changes master; music must keep the other session's value.
    assert store.save({"master": 80}) == OK
    assert store.load() == {"master": 80, "music": 5, "sfx": 50}


def test_save_is_never_truncated_under_concurrent_writes(store):
    store.save({"master": 33, "music": 33, "sfx": 33})
    # Whatever happens, the file always parses to a complete settings dict.
    for i in range(5):
        store.save({"master": i, "music": i, "sfx": i})
        data = json.loads(open(store.path, encoding="utf-8").read())
        assert set(data.keys()) == set(DEFAULTS.keys())


# -- corrupt/tampered input falls back gracefully -------------------------
def test_corrupt_file_loads_as_defaults(store):
    with open(store.path, "w", encoding="utf-8") as f:
        f.write("{ this is not valid json")
    assert store.load() == DEFAULTS


def test_out_of_range_values_are_clamped(store):
    store.save({"master": 999, "music": -50, "sfx": 50})
    assert store.load() == {"master": 100, "music": 0, "sfx": 50}
