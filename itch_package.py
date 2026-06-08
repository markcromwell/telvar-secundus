#!/usr/bin/env python3
"""itch_package.py — package a Godot HTML5 export into an itch.io-ready zip.

Consumes a completed Godot HTML5 export directory and produces a timestamped
archive named ``Telvar-Secundus-YYYYMMDD-HHMMSS.zip``. The zip bundles:

  * ``index.html`` and every other file emitted by the Godot Web export,
  * ``CREDITS.md`` from the repository root, and
  * the project's CC0 / attribution audio files under ``audio/`` (with their
    ATTRIBUTION.txt manifests) so the licensing source travels with the build.

Every entry is stored under a verified relative path — absolute paths and
parent-directory (``..``) traversal are rejected. Archive contents use a fixed
internal timestamp so repeated runs over identical inputs are byte-for-byte
deterministic. The zip is capped at 50 MiB (non-zero exit if exceeded) and is
written to a unique temp file then atomically renamed into place, so repeated
or concurrent invocations never observe a partial archive.

Usage:
    python itch_package.py <export_dir> [--output-dir DIR]

Exits 0 on success; on any failure prints a diagnostic to stderr and exits
non-zero, so it can be dropped into a GitHub Actions step unchanged.
"""
import argparse
import datetime
import os
import sys
import tempfile
import zipfile


ROOT = os.path.dirname(os.path.abspath(__file__))

ZIP_NAME_PREFIX = "Telvar-Secundus"
# 50 MiB ceiling on the finished archive.
MAX_ZIP_BYTES = 50 * 1024 * 1024
# Files we treat as bundled audio worth shipping alongside the export.
AUDIO_EXTENSIONS = (".ogg", ".wav", ".mp3", ".flac")
AUDIO_MANIFESTS = ("ATTRIBUTION.txt",)
# Fixed entry timestamp (the ZIP format epoch) for reproducible archives.
ZIP_EPOCH = (1980, 1, 1, 0, 0, 0)


def fail(message):
    """Print a diagnostic to stderr and exit non-zero."""
    print(f"itch_package: ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def log(message):
    """Emit progress to stderr (stdout stays clean for the produced path)."""
    print(f"itch_package: {message}", file=sys.stderr)


def safe_arcname(arcname):
    """Return a normalized relative POSIX arcname, or None if unsafe.

    Rejects absolute paths and any path that escapes the archive root via a
    ``..`` component. Backslashes are treated as separators so the check holds
    regardless of the platform the export was produced on.
    """
    if os.path.isabs(arcname):
        return None
    parts = []
    for part in arcname.replace("\\", "/").split("/"):
        if part in ("", "."):
            continue
        if part == "..":
            return None
        parts.append(part)
    if not parts:
        return None
    return "/".join(parts)


def add_entry(entries, arcname, source):
    """Register source -> arcname, first writer wins, with path validation.

    Returns True if the entry was added. Earlier sources (the export itself)
    take precedence over supplemental sources so a file already present in the
    export is never duplicated under the same arcname.
    """
    safe = safe_arcname(arcname)
    if safe is None:
        fail(f"refusing unsafe archive path {arcname!r} for {source}")
    if safe in entries:
        return False
    entries[safe] = source
    return True


def collect_export(entries, export_dir):
    """Add every file in the Godot export, keyed by its path under export_dir."""
    count = 0
    for dirpath, _dirnames, filenames in os.walk(export_dir):
        for filename in sorted(filenames):
            source = os.path.join(dirpath, filename)
            arcname = os.path.relpath(source, export_dir)
            if add_entry(entries, arcname, source):
                count += 1
    return count


def collect_credits(entries, credits_path):
    """Ensure CREDITS.md is present at the archive root."""
    if not os.path.isfile(credits_path):
        fail(f"CREDITS.md not found: {credits_path}")
    add_entry(entries, "CREDITS.md", credits_path)


def collect_audio(entries, audio_dir):
    """Add bundled audio files (and their attribution manifests) under audio/."""
    if not os.path.isdir(audio_dir):
        log(f"no audio directory at {audio_dir}; skipping audio bundle")
        return 0
    count = 0
    for dirpath, _dirnames, filenames in os.walk(audio_dir):
        for filename in sorted(filenames):
            lower = filename.lower()
            is_audio = lower.endswith(AUDIO_EXTENSIONS)
            is_manifest = filename in AUDIO_MANIFESTS
            if not (is_audio or is_manifest):
                continue
            source = os.path.join(dirpath, filename)
            # Preserve the repo-relative layout, e.g. audio/sfx/foo.ogg.
            arcname = os.path.relpath(source, ROOT)
            if add_entry(entries, arcname, source):
                count += 1
    return count


def build_zip(entries, dest_tmp):
    """Write entries into dest_tmp deterministically (sorted, fixed mtime)."""
    with zipfile.ZipFile(dest_tmp, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for arcname in sorted(entries):
            source = entries[arcname]
            info = zipfile.ZipInfo(arcname, date_time=ZIP_EPOCH)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            with open(source, "rb") as handle:
                zf.writestr(info, handle.read())


def verify_zip(path):
    """Re-open the finished archive and confirm its integrity and contents."""
    with zipfile.ZipFile(path, "r") as zf:
        bad = zf.testzip()
        if bad is not None:
            fail(f"archive integrity check failed on entry {bad}")
        names = zf.namelist()
    for name in names:
        if os.path.isabs(name) or safe_arcname(name) != name:
            fail(f"archive contains an unsafe path: {name!r}")
    if "index.html" not in names:
        fail("archive is missing index.html")
    if "CREDITS.md" not in names:
        fail("archive is missing CREDITS.md")
    return names


def main(argv):
    parser = argparse.ArgumentParser(
        description="Package a Godot HTML5 export into an itch.io-ready zip.",
    )
    parser.add_argument(
        "export_dir",
        help="Path to a completed Godot HTML5 export directory (contains index.html).",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        default=os.getcwd(),
        help="Directory to write the zip into (default: current directory).",
    )
    parser.add_argument(
        "--credits",
        default=os.path.join(ROOT, "CREDITS.md"),
        help="Path to CREDITS.md (default: repo root CREDITS.md).",
    )
    parser.add_argument(
        "--audio-dir",
        default=os.path.join(ROOT, "audio"),
        help="Directory of bundled audio to include (default: repo root audio/).",
    )
    args = parser.parse_args(argv)

    export_dir = os.path.abspath(args.export_dir)
    if not os.path.isdir(export_dir):
        fail(f"export directory not found: {export_dir}")
    if not os.path.isfile(os.path.join(export_dir, "index.html")):
        fail(f"index.html not found in export directory: {export_dir}")

    output_dir = os.path.abspath(args.output_dir)
    os.makedirs(output_dir, exist_ok=True)

    entries = {}
    n_export = collect_export(entries, export_dir)
    collect_credits(entries, os.path.abspath(args.credits))
    n_audio = collect_audio(entries, os.path.abspath(args.audio_dir))
    log(f"collected {n_export} export files, {n_audio} audio files, CREDITS.md")

    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d-%H%M%S")
    zip_name = f"{ZIP_NAME_PREFIX}-{timestamp}.zip"
    dest = os.path.join(output_dir, zip_name)

    # Build into a unique temp file in the destination directory so the atomic
    # rename stays on one filesystem and concurrent runs never share a temp.
    fd, tmp_path = tempfile.mkstemp(
        prefix=f".{ZIP_NAME_PREFIX}-", suffix=".zip.tmp", dir=output_dir
    )
    os.close(fd)
    try:
        build_zip(entries, tmp_path)
        size = os.path.getsize(tmp_path)
        if size > MAX_ZIP_BYTES:
            fail(
                f"archive is {size} bytes, exceeding the "
                f"{MAX_ZIP_BYTES} byte (50 MiB) limit"
            )
        verify_zip(tmp_path)
        os.replace(tmp_path, dest)
    except BaseException:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise

    log(f"wrote {dest} ({os.path.getsize(dest)} bytes, {len(entries)} entries)")
    # Emit the final path on stdout so callers / CI can capture it.
    print(dest)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
