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
_REQUIRED_PATHS = [
    _REPO / "scripts/resources/item.gd",
    _REPO / "scripts/inventory/inventory.gd",
    _REPO / "resources/items/wizard_band_red.tres",
]
_WIZARD_BAND = _REPO / "resources/items/wizard_band_red.tres"

for path in _REQUIRED_PATHS:
    if not path.is_file():
        errors.append(f"Missing required file: {path.relative_to(_REPO)}")

if _WIZARD_BAND.is_file():
    band_text = _WIZARD_BAND.read_text(encoding="utf-8")
    if "magical" not in band_text:
        errors.append("wizard_band_red.tres must include the magical tag")
    if "wizard_band_red" not in band_text:
        errors.append("wizard_band_red.tres must define id wizard_band_red")

# Only enforce critical structural checks here
# (Full validation in spec 1246)

if errors:
    for e in errors:
        print("FAIL:", e)
    sys.exit(1)

print("Bootstrap checks passed (spec 1246 will add full validation)")
sys.exit(0)
