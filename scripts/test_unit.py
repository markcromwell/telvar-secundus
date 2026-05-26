"""Structural checks for Godot TileSet resources (text parse; no engine runtime)."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
TILESET_PATH = REPO_ROOT / "assets" / "tilesets" / "lpc_terrain.tres"


def _parse_vec2i(line: str) -> tuple[int, int] | None:
    m = re.search(r"Vector2i\(\s*(-?\d+)\s*,\s*(-?\d+)\s*\)", line)
    if not m:
        return None
    return int(m.group(1)), int(m.group(2))


def test_lpc_terrain_tileset_contract() -> None:
    assert TILESET_PATH.is_file(), f"missing {TILESET_PATH}"

    text = TILESET_PATH.read_text(encoding="utf-8")

    assert 'path="res://assets/tilesets/lpc_terrain.png"' in text
    assert "type=\"TileSet\"" in text.splitlines()[0]

    m_tile = re.search(r"^\s*tile_size\s*=\s*Vector2i\(\s*(\d+)\s*,\s*(\d+)\s*\)\s*$", text, re.MULTILINE)
    assert m_tile, "tile_size not found on TileSet [resource]"
    assert (int(m_tile.group(1)), int(m_tile.group(2))) == (32, 32)

    sub_start = text.index("[sub_resource type=\"TileSetAtlasSource\"")
    resource_start = text.index("\n[resource]")
    sub_block = text[sub_start:resource_start]

    trs = _parse_vec2i(
        next(
            ln
            for ln in sub_block.splitlines()
            if re.match(r"^\s*texture_region_size\s*=", ln)
        )
    )
    assert trs == (16, 16)

    sep = _parse_vec2i(next(ln for ln in sub_block.splitlines() if re.match(r"^\s*separation\s*=", ln)))
    mar = _parse_vec2i(next(ln for ln in sub_block.splitlines() if re.match(r"^\s*margins\s*=", ln)))
    assert sep is not None and mar is not None
    assert sep[0] >= 1 and sep[1] >= 1
    assert mar[0] >= 1 and mar[1] >= 1

    assert re.search(r"^\s*use_texture_padding\s*=\s*true\s*$", sub_block, re.MULTILINE)

    for name in ("stone_floor", "grass", "dirt", "wall"):
        assert name in text, f"expected tile id {name!r} in {TILESET_PATH.name}"

    alt_lines = re.findall(r"^\s*(\d+):(\d+)/0\s*=\s*0\s*$", text, re.MULTILINE)
    assert sorted(alt_lines) == [("0", "0"), ("0", "1"), ("1", "0"), ("2", "0")], (
        f"expected exactly four base atlas tiles; got {alt_lines!r}"
    )

    assert re.search(r"^\s*physics_layer_0/collision_layer\s*=", text, re.MULTILINE)
    assert re.search(r"^\s*physics_layer_0/collision_mask\s*=", text, re.MULTILINE)

    assert re.search(r"^\s*custom_data_layer_0/name\s*=", text, re.MULTILINE)
    assert re.search(r"^\s*custom_data_layer_0/type\s*=\s*4\s*$", text, re.MULTILINE)


if __name__ == "__main__":
    pytest.main([__file__, "-q"])
