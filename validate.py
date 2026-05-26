#!/usr/bin/env python3
"""Structural validation for Telvar RPG lore data (no Godot runtime).

Verifies assets/lore/lore_entries.json: exists, valid JSON, entry count,
required keys per entry, and word-count bounds on each entry's text field.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
LORE_PATH = REPO_ROOT / "assets" / "lore" / "lore_entries.json"
REQUIRED_KEYS = ("id", "title", "text")
EXPECTED_COUNT = 10
MIN_WORDS = 100
MAX_WORDS = 200


def _word_count(text: str) -> int:
    return len(text.split())


def main() -> int:
    any_fail = False

    def fail(msg: str) -> None:
        nonlocal any_fail
        any_fail = True
        print(f"FAIL: {msg}")

    def ok(msg: str) -> None:
        print(f"PASS: {msg}")

    if not LORE_PATH.is_file():
        fail(f"Lore file not found (expected {LORE_PATH})")
        return 1

    ok(f"Lore file exists ({LORE_PATH})")

    try:
        raw = LORE_PATH.read_text(encoding="utf-8")
        data = json.loads(raw)
    except OSError as e:
        fail(f"Could not read lore file: {e}")
        return 1
    except json.JSONDecodeError as e:
        fail(f"Invalid JSON: {e}")
        return 1

    ok("JSON parses successfully")

    if not isinstance(data, list):
        fail(f"Root value must be a JSON array, got {type(data).__name__}")
        return 1

    if len(data) != EXPECTED_COUNT:
        fail(f"Expected exactly {EXPECTED_COUNT} lore entries, found {len(data)}")
        return 1

    ok(f"Entry count is exactly {EXPECTED_COUNT}")

    for i, entry in enumerate(data):
        prefix = f"Entry {i}"
        if not isinstance(entry, dict):
            fail(f"{prefix}: must be a JSON object, got {type(entry).__name__}")
            continue

        missing = [k for k in REQUIRED_KEYS if k not in entry]
        if missing:
            fail(f"{prefix}: missing required key(s): {', '.join(repr(k) for k in missing)}")
            continue

        ok(f"{prefix}: has keys {list(REQUIRED_KEYS)}")

        text_val = entry["text"]
        if not isinstance(text_val, str):
            fail(f"{prefix}: 'text' must be a string, got {type(text_val).__name__}")
            continue

        wc = _word_count(text_val)
        if wc < MIN_WORDS or wc > MAX_WORDS:
            fail(
                f"{prefix}: 'text' word count is {wc} "
                f"(required {MIN_WORDS}-{MAX_WORDS} inclusive)"
            )
        else:
            ok(f"{prefix}: 'text' word count {wc} is within {MIN_WORDS}-{MAX_WORDS}")

    if any_fail:
        print("Validation finished with errors.")
        return 1

    print("All lore validation checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
