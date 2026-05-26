#!/usr/bin/env python3
"""
TELVAR-RPG validation script (bootstrap stub).
Full validation is implemented in spec #1246.
During early development, this exits 0 to allow the pipeline to proceed.
"""
import sys, os

# Bootstrap mode: check only what is strictly required at this stage
errors = []

_credits = os.path.join(os.path.dirname(os.path.abspath(__file__)), "CREDITS.md")
if not os.path.isfile(_credits):
    errors.append("Missing CREDITS.md at repository root")
else:
    with open(_credits, encoding="utf-8") as f:
        _ct = f.read()
    if "# Credits" not in _ct:
        errors.append("CREDITS.md must contain a '# Credits' heading")
    for _heading in ("## Art", "## Code", "## Story", "## Audio"):
        if _heading not in _ct:
            errors.append(f"CREDITS.md must contain section {_heading}")

# Only enforce critical structural checks here
# (Full validation in spec 1246)

if errors:
    for e in errors:
        print("FAIL:", e)
    sys.exit(1)

print("Bootstrap checks passed (spec 1246 will add full validation)")
sys.exit(0)
