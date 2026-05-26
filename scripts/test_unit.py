"""Smoke tests for repo automation (structural validation)."""

import subprocess
import sys
from pathlib import Path

def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def test_validate_py_exits_zero():
    root = _repo_root()
    result = subprocess.run(
        [sys.executable, str(root / "validate.py")],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, (
        f"validate.py failed (code {result.returncode})\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
