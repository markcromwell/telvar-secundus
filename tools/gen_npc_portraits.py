#!/usr/bin/env python3
"""Write solid-color 48x48 RGBA PNG placeholders for NPC portraits (no deps)."""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = REPO_ROOT / "assets" / "portraits"

# Distinct placeholder colors (RGBA) per NPC.
NPC_COLORS: dict[str, tuple[int, int, int, int]] = {
    "sabatha": (136, 102, 170, 255),
    "orrson": (68, 102, 204, 255),
    "market_trader": (102, 170, 68, 255),
    "city_guard": (136, 136, 136, 255),
    "beggar_child": (204, 136, 68, 255),
}


def _chunk(chunk_type: bytes, data: bytes) -> bytes:
    crc = zlib.crc32(chunk_type + data) & 0xFFFFFFFF
    return struct.pack(">I", len(data)) + chunk_type + data + struct.pack(">I", crc)


def write_png_rgba(path: Path, width: int, height: int, rgba: tuple[int, int, int, int]) -> None:
    pixel = bytes(rgba)
    raw_rows = b"".join(b"\x00" + pixel * width for _ in range(height))
    compressed = zlib.compress(raw_rows, level=9)
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", ihdr)
    png += _chunk(b"IDAT", compressed)
    png += _chunk(b"IEND", b"")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(png)


def main() -> None:
    for name, rgba in NPC_COLORS.items():
        write_png_rgba(OUT_DIR / f"{name}.png", 48, 48, rgba)
    print(f"Wrote {len(NPC_COLORS)} PNGs to {OUT_DIR}")


if __name__ == "__main__":
    main()
