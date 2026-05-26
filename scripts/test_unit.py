"""Fast smoke tests for CI (game structure via validate.py)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_validate_game_project_structure() -> None:
    root = Path(__file__).resolve().parents[1]
    validate = root / "validate.py"
    assert validate.is_file(), "validate.py must exist at repo root"
    subprocess.run(
        [sys.executable, str(validate)],
        cwd=str(root),
        check=True,
    )
