#!/usr/bin/env python3
"""
TELVAR-RPG validation script (bootstrap stub).
Full validation is implemented in spec #1246.
During early development, this exits 0 to allow the pipeline to proceed.
"""
import sys
from pathlib import Path

# Bootstrap mode: check only what is strictly required at this stage
errors = []

_REPO = Path(__file__).resolve().parent
_REQUIRED_FILES = [
    _REPO / "scenes" / "veneficturis_main_hall.tscn",
    _REPO / "scripts" / "veneficturis_main_hall.gd",
    _REPO / "tilesets" / "dark_stone_lpc.tres",
    _REPO / "assets" / "tiles" / "dark_stone_lpc.png",
]

for _path in _REQUIRED_FILES:
    if not _path.is_file():
        errors.append(f"Missing required file: {_path.relative_to(_REPO)}")

# Only enforce critical structural checks here
# (Full validation in spec 1246)

if errors:
    for e in errors:
        print("FAIL:", e)
    sys.exit(1)

print("Bootstrap checks passed (spec 1246 will add full validation)")
sys.exit(0)
