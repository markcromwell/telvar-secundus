"""Filesystem validation for RELEASES.md documentation."""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
RELEASES_MD = REPO_ROOT / "RELEASES.md"


def test_releases_md_exists() -> None:
    """Asserts RELEASES.md exists in the repository root."""
    assert RELEASES_MD.is_file(), "RELEASES.md must exist in the repo root"


def test_releases_md_content() -> None:
    """Asserts RELEASES.md contains the required sections for Itch.io releases."""
    if not RELEASES_MD.is_file():
        pytest.fail("RELEASES.md not found, so content checks cannot run.")

    text = RELEASES_MD.read_text(encoding="utf-8").lower()

    # Check for download and upload steps
    assert "itch-package" in text, "Documentation must mention 'itch-package' artifact download."
    assert "upload to itch.io" in text, "Documentation must describe the Itch.io upload process."

    # Check for verification checklist items
    assert "zip contents" in text, "Verification checklist must include 'zip contents'."
    assert "launch" in text, "Verification checklist must include 'launch'."
    assert "timestamp" in text, "Verification checklist must include 'timestamp'."

    # Check for credential error handling
    assert "credential error" in text, "Documentation must include notes on handling credential errors."
