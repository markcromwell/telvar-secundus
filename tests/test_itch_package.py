"""Unit tests for itch_package.py — the Godot HTML5 → itch.io zip packager.

Mirrors the tests/test_godot_config.py style: pathlib + pytest, standard
library only (no Godot binary, no network). Each test builds a self-contained
fixture "repo" under tmp_path — a fake export directory plus the CREDITS.md and
audio/ tree the packager bundles — then invokes itch_package.main() and asserts
on the produced archive.

itch_package resolves CREDITS.md and audio/ relative to a module-level ROOT
(the repo root in production). We monkeypatch ROOT onto the fixture so the
default credits/audio paths point at fixture files and the bundled audio lands
under clean, ROOT-relative arcnames (e.g. ``audio/sfx/foo.ogg``).
"""

from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path
from types import SimpleNamespace

import pytest

# Ensure the repo root (where itch_package.py lives) is importable regardless of
# the directory pytest is invoked from or whether this module is re-exported via
# scripts/test_unit.py.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import itch_package  # noqa: E402

# Filename the packager must emit: Telvar-Secundus-YYYYMMDD-HHMMSS.zip
ZIP_NAME_RE = re.compile(r"^Telvar-Secundus-\d{8}-\d{6}\.zip$")

# Audio files the packager is expected to bundle, by their archive-relative path.
EXPECTED_AUDIO = (
    "audio/sfx/sfx_click.ogg",
    "audio/sfx/ATTRIBUTION.txt",
    "audio/music/theme_loop.ogg",
    "audio/music/ATTRIBUTION.txt",
)
# Non-audio siblings that must NOT be bundled by the audio collector.
EXCLUDED_AUDIO_SIBLINGS = (
    "audio/sfx/sfx_click.ogg.import",
    "audio/music/README.txt",
)


@pytest.fixture
def repo(tmp_path, monkeypatch):
    """Build a fake project root + Godot export under tmp_path.

    Layout::

        <root>/CREDITS.md
        <root>/audio/sfx/sfx_click.ogg          (+ ATTRIBUTION.txt, .import)
        <root>/audio/music/theme_loop.ogg       (+ ATTRIBUTION.txt, README.txt)
        <root>/export/index.html                (+ js/wasm/pck siblings)
        <root>/export/assets/sprite.png
        <root>/out/                             (output directory)

    ``itch_package.ROOT`` is patched to ``<root>`` so the CREDITS.md / audio
    defaults resolve into the fixture. Returns the paths plus a ``produced``
    helper that returns the single zip emitted into the output dir.
    """
    root = tmp_path / "root"
    export = root / "export"
    assets = export / "assets"
    audio_sfx = root / "audio" / "sfx"
    audio_music = root / "audio" / "music"
    output = root / "out"
    for d in (assets, audio_sfx, audio_music, output):
        d.mkdir(parents=True, exist_ok=True)

    # A minimal Godot Web export.
    (export / "index.html").write_text("<!doctype html><title>Telvar</title>")
    (export / "index.js").write_text("// godot engine loader\n")
    (export / "index.wasm").write_bytes(b"\x00asm\x01\x00\x00\x00")
    (export / "index.pck").write_bytes(b"GDPC" + b"\x00" * 64)
    (assets / "sprite.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 32)

    # CREDITS.md bundled from the (patched) repo root.
    (root / "CREDITS.md").write_text("# Credits\n\n## Audio\nCC0 sources.\n")

    # Audio bundle: real audio + attribution manifests are included; the
    # Godot .import sidecar and a stray README are not.
    (audio_sfx / "sfx_click.ogg").write_bytes(b"OggS" + b"\x00" * 48)
    (audio_sfx / "ATTRIBUTION.txt").write_text("sfx_click.ogg: CC0\n")
    (audio_sfx / "sfx_click.ogg.import").write_text("[remap]\n")
    (audio_music / "theme_loop.ogg").write_bytes(b"OggS" + b"\x00" * 96)
    (audio_music / "ATTRIBUTION.txt").write_text("theme_loop.ogg: CC0\n")
    (audio_music / "README.txt").write_text("not audio\n")

    monkeypatch.setattr(itch_package, "ROOT", str(root))

    def produced():
        zips = sorted(output.glob("*.zip"))
        assert len(zips) == 1, f"expected exactly one zip, found {zips}"
        return zips[0]

    return SimpleNamespace(
        root=root,
        export=export,
        output=output,
        produced=produced,
    )


def _run(repo, *extra_args):
    """Invoke the packager against the fixture; assert success, return rc."""
    argv = [str(repo.export), "--output-dir", str(repo.output), *extra_args]
    return itch_package.main(argv)


# --------------------------------------------------------------------------- #
# Naming
# --------------------------------------------------------------------------- #
def test_zip_name_matches_timestamp_pattern(repo):
    assert _run(repo) == 0
    name = repo.produced().name
    assert ZIP_NAME_RE.match(name), f"{name!r} does not match the required pattern"


def test_main_prints_produced_path_to_stdout(repo, capsys):
    assert _run(repo) == 0
    out = capsys.readouterr().out.strip().splitlines()
    assert out, "expected the produced path on stdout"
    assert Path(out[-1]) == repo.produced()


# --------------------------------------------------------------------------- #
# Member presence and relative paths
# --------------------------------------------------------------------------- #
def test_index_html_present_at_root(repo):
    assert _run(repo) == 0
    with zipfile.ZipFile(repo.produced()) as zf:
        assert "index.html" in zf.namelist()


def test_credits_md_present_at_root(repo):
    assert _run(repo) == 0
    with zipfile.ZipFile(repo.produced()) as zf:
        names = zf.namelist()
        assert "CREDITS.md" in names
        # Bundled from the patched repo root, not the export dir.
        assert b"# Credits" in zf.read("CREDITS.md")


def test_audio_files_present_at_expected_relative_paths(repo):
    assert _run(repo) == 0
    with zipfile.ZipFile(repo.produced()) as zf:
        names = set(zf.namelist())
    for expected in EXPECTED_AUDIO:
        assert expected in names, f"missing bundled audio member {expected!r}"


def test_non_audio_siblings_are_not_bundled(repo):
    assert _run(repo) == 0
    with zipfile.ZipFile(repo.produced()) as zf:
        names = set(zf.namelist())
    for excluded in EXCLUDED_AUDIO_SIBLINGS:
        assert excluded not in names, f"unexpectedly bundled {excluded!r}"


def test_export_assets_kept_at_their_relative_paths(repo):
    assert _run(repo) == 0
    with zipfile.ZipFile(repo.produced()) as zf:
        names = set(zf.namelist())
    for member in ("index.js", "index.wasm", "index.pck", "assets/sprite.png"):
        assert member in names, f"missing export member {member!r}"


def test_all_archive_paths_are_safe_relative(repo):
    """No member may be absolute or escape the archive root."""
    assert _run(repo) == 0
    with zipfile.ZipFile(repo.produced()) as zf:
        for name in zf.namelist():
            assert not name.startswith("/")
            assert ".." not in name.split("/")
            assert itch_package.safe_arcname(name) == name


# --------------------------------------------------------------------------- #
# Size ceiling
# --------------------------------------------------------------------------- #
def test_zip_size_under_50_mib(repo):
    assert _run(repo) == 0
    assert repo.produced().stat().st_size <= itch_package.MAX_ZIP_BYTES


def test_size_limit_enforced(repo, monkeypatch):
    """When the build exceeds the ceiling, packaging fails and emits nothing."""
    monkeypatch.setattr(itch_package, "MAX_ZIP_BYTES", 8)
    with pytest.raises(SystemExit) as exc:
        _run(repo)
    assert exc.value.code != 0
    assert list(repo.output.glob("*.zip")) == []
    # No partial temp archive is left behind.
    assert list(repo.output.glob(".*tmp")) == []
    assert list(repo.output.glob("*.tmp")) == []


# --------------------------------------------------------------------------- #
# Missing-input handling
# --------------------------------------------------------------------------- #
def test_missing_index_html_fails(repo):
    (repo.export / "index.html").unlink()
    with pytest.raises(SystemExit) as exc:
        _run(repo)
    assert exc.value.code != 0
    assert list(repo.output.glob("*.zip")) == []


def test_missing_export_dir_fails(repo):
    argv = [str(repo.root / "does-not-exist"), "--output-dir", str(repo.output)]
    with pytest.raises(SystemExit) as exc:
        itch_package.main(argv)
    assert exc.value.code != 0


def test_missing_credits_fails(repo):
    (repo.root / "CREDITS.md").unlink()
    with pytest.raises(SystemExit) as exc:
        _run(repo)
    assert exc.value.code != 0
    assert list(repo.output.glob("*.zip")) == []


# --------------------------------------------------------------------------- #
# Determinism / atomicity
# --------------------------------------------------------------------------- #
def test_archive_is_byte_for_byte_reproducible(repo):
    """Identical inputs produce byte-identical archives (fixed entry mtimes)."""
    out_a = repo.output / "a"
    out_b = repo.output / "b"
    out_a.mkdir()
    out_b.mkdir()
    assert itch_package.main([str(repo.export), "--output-dir", str(out_a)]) == 0
    assert itch_package.main([str(repo.export), "--output-dir", str(out_b)]) == 0
    bytes_a = next(out_a.glob("*.zip")).read_bytes()
    bytes_b = next(out_b.glob("*.zip")).read_bytes()
    assert bytes_a == bytes_b


def test_successful_run_leaves_no_temp_files(repo):
    assert _run(repo) == 0
    leftovers = [p for p in repo.output.iterdir() if p.suffix != ".zip"]
    assert leftovers == [], f"unexpected leftovers in output dir: {leftovers}"


# --------------------------------------------------------------------------- #
# safe_arcname helper (path-traversal hardening)
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    "raw, expected",
    [
        ("index.html", "index.html"),
        ("audio/sfx/foo.ogg", "audio/sfx/foo.ogg"),
        ("./assets/./sprite.png", "assets/sprite.png"),
        ("a\\b\\c.txt", "a/b/c.txt"),
        ("/etc/passwd", None),
        ("../escape.txt", None),
        ("a/../../b.txt", None),
        ("", None),
        (".", None),
    ],
)
def test_safe_arcname(raw, expected):
    assert itch_package.safe_arcname(raw) == expected
