"""Unit tests for itch_package.py — the itch.io HTML5 build packager.

Invokes the script as a subprocess (it is an argparse/sys.exit CLI) and asserts
on the produced itch-build.zip: a single timestamped top-level folder, inclusion
of the supplied build files, the missing-build-dir failure path, and the
--output-path override. Mirrors tests/test_godot_config.py (REPO_ROOT/pathlib).
"""

from __future__ import annotations

import re
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
ITCH_PACKAGE = REPO_ROOT / "itch_package.py"

# telvar-YYYYMMDD-HHMMSS/relative/path inside the zip.
TIMESTAMP_ENTRY = re.compile(r"^telvar-(\d{8}-\d{6})/")


def _run_package(source_dir: Path, output_path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(ITCH_PACKAGE),
            "--source-dir",
            str(source_dir),
            "--output-path",
            str(output_path),
        ],
        capture_output=True,
        text=True,
    )


def _make_build(build_dir: Path) -> dict[str, str]:
    """Create a minimal HTML5 build tree; return {relative_path: contents}."""
    build_dir.mkdir(parents=True, exist_ok=True)
    files = {
        "index.html": "<html><body>Telvar</body></html>",
        "index.wasm": "wasm-bytes",
        "assets/data.pck": "pck-bytes",
    }
    for rel, contents in files.items():
        target = build_dir / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(contents, encoding="utf-8")
    return files


def test_itch_package_exists() -> None:
    assert ITCH_PACKAGE.is_file()


def test_creates_itch_build_zip(tmp_path: Path) -> None:
    build_dir = tmp_path / "build"
    _make_build(build_dir)
    output_path = tmp_path / "itch-build.zip"

    proc = _run_package(build_dir, output_path)

    assert proc.returncode == 0, proc.stderr
    assert output_path.name == "itch-build.zip"
    assert output_path.is_file()
    assert zipfile.is_zipfile(output_path)


def test_timestamped_top_level_entry(tmp_path: Path) -> None:
    build_dir = tmp_path / "build"
    _make_build(build_dir)
    output_path = tmp_path / "itch-build.zip"

    proc = _run_package(build_dir, output_path)
    assert proc.returncode == 0, proc.stderr

    with zipfile.ZipFile(output_path) as zf:
        names = zf.namelist()

    assert names, "zip is empty"
    # Every entry must live under one timestamped telvar-<stamp>/ folder.
    stamps = {m.group(1) for n in names if (m := TIMESTAMP_ENTRY.match(n))}
    assert len(stamps) == 1, f"expected a single timestamped folder, got {sorted(stamps)}"
    top_levels = {n.split("/", 1)[0] for n in names}
    assert len(top_levels) == 1, f"expected one top-level dir, got {sorted(top_levels)}"


def test_zip_contains_supplied_build_files(tmp_path: Path) -> None:
    build_dir = tmp_path / "build"
    files = _make_build(build_dir)
    output_path = tmp_path / "itch-build.zip"

    proc = _run_package(build_dir, output_path)
    assert proc.returncode == 0, proc.stderr

    with zipfile.ZipFile(output_path) as zf:
        names = zf.namelist()
        # Strip the timestamped prefix to compare against the supplied tree.
        stripped = {n.split("/", 1)[1] for n in names if "/" in n}
        assert set(files) <= stripped
        # Round-trip contents of one file to confirm payload integrity.
        prefix = names[0].split("/", 1)[0]
        recovered = zf.read(f"{prefix}/index.html").decode("utf-8")
        assert recovered == files["index.html"]


def test_missing_build_dir_fails(tmp_path: Path) -> None:
    missing = tmp_path / "does-not-exist"
    output_path = tmp_path / "itch-build.zip"

    proc = _run_package(missing, output_path)

    assert proc.returncode != 0
    assert not output_path.exists()
    assert "not found" in proc.stdout.lower() or "not found" in proc.stderr.lower()


def test_output_path_override(tmp_path: Path) -> None:
    build_dir = tmp_path / "build"
    _make_build(build_dir)
    custom_output = tmp_path / "nested" / "custom-name.zip"
    custom_output.parent.mkdir(parents=True, exist_ok=True)

    proc = _run_package(build_dir, custom_output)

    assert proc.returncode == 0, proc.stderr
    assert custom_output.is_file()
    assert zipfile.is_zipfile(custom_output)
