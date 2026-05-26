#!/usr/bin/env python3
"""Structural validation for the Godot project (text checks only; no Godot runtime)."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent


def _failures() -> list[str]:
    failed: list[str] = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        if ok:
            print(f"PASS: {name}")
        else:
            msg = f"FAIL: {name}"
            if detail:
                msg += f": {detail}"
            print(msg)
            failed.append(name)

    credits = REPO_ROOT / "CREDITS.md"
    check("CREDITS.md", credits.is_file(), "missing file at repo root")

    main_tscn = REPO_ROOT / "scenes" / "Main.tscn"
    if not main_tscn.is_file():
        missing = f"missing {main_tscn.relative_to(REPO_ROOT)}"
        check("Main.tscn: CreditsButton", False, missing)
        check("Main.tscn: CreditsPanel", False, missing)
    else:
        tscn = main_tscn.read_text(encoding="utf-8")
        check("Main.tscn: CreditsButton", "CreditsButton" in tscn, "string not found in Main.tscn")
        check("Main.tscn: CreditsPanel", "CreditsPanel" in tscn, "string not found in Main.tscn")

    main_gd = REPO_ROOT / "scripts" / "Main.gd"
    if not main_gd.is_file():
        check("Main.gd: _on_credits_pressed", False, f"missing {main_gd.relative_to(REPO_ROOT)}")
    else:
        gd = main_gd.read_text(encoding="utf-8")
        check("Main.gd: _on_credits_pressed", "_on_credits_pressed" in gd, "symbol not found in Main.gd")

    return failed


def main() -> int:
    failed = _failures()
    if failed:
        print(f"\n{len(failed)} check(s) failed.", file=sys.stderr)
        return 1
    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
