#!/usr/bin/env python3
"""Structural validation for TileSet and MainScene (text parse; no Godot runtime)."""
from __future__ import annotations

import re
import struct
import sys
from pathlib import Path


def fail(msg: str) -> None:
    print(f"validate: FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def _png_pixel_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        fail(f"not a PNG: {path}")
    width = struct.unpack(">I", data[16:20])[0]
    height = struct.unpack(">I", data[20:24])[0]
    return int(width), int(height)


def main() -> None:
    root = Path(__file__).resolve().parent
    png = root / "assets" / "tilesets" / "lpc_terrain.png"
    tres = root / "assets" / "tilesets" / "lpc_terrain.tres"

    if not png.is_file():
        fail(f"missing {png.relative_to(root)}")
    if not tres.is_file():
        fail(f"missing {tres.relative_to(root)}")

    pw, ph = _png_pixel_size(png)

    lines = tres.read_text(encoding="utf-8").splitlines()
    if not lines or not lines[0].startswith('[gd_resource type="TileSet"'):
        fail("lpc_terrain.tres must start with [gd_resource type=\"TileSet\" ...]")

    text = "\n".join(lines)
    if 'path="res://assets/tilesets/lpc_terrain.png"' not in text:
        fail("TileSet must reference res://assets/tilesets/lpc_terrain.png")

    if not re.search(r"^\s*sources/0\s*=\s*SubResource\(", text, re.MULTILINE):
        fail("TileSet must define sources/0 (floor atlas)")
    if not re.search(r"^\s*sources/1\s*=\s*SubResource\(", text, re.MULTILINE):
        fail("TileSet must define sources/1 (wall atlas)")

    if text.count('[sub_resource type="TileSetAtlasSource"') != 2:
        fail("expected exactly two TileSetAtlasSource sub-resources")

    if not re.search(r"^\s*texture_region_size\s*=\s*Vector2i\(\s*16\s*,\s*16\s*\)\s*$", text, re.MULTILINE):
        fail("texture_region_size must be Vector2i(16, 16)")

    for name in ("stone_floor", "grass", "dirt", "wall_stone", "wall_brick"):
        if name not in text:
            fail(f"expected tile marker {name!r} in {tres.name}")

    # Bounds: each declared tile atlas cell must fit inside the texture for its atlas block.
    sub_re = re.compile(
        r'\[sub_resource type="TileSetAtlasSource"[^\]]*\](.*?)(?=\n\[sub_resource|\n\[resource\])',
        re.DOTALL,
    )
    blocks = sub_re.findall(text)
    if len(blocks) != 2:
        fail("could not parse two TileSetAtlasSource blocks")

    for bi, block in enumerate(blocks):
        m_mar = re.search(r"^\s*margins\s*=\s*Vector2i\(\s*(-?\d+)\s*,\s*(-?\d+)\s*\)\s*$", block, re.MULTILINE)
        m_sep = re.search(r"^\s*separation\s*=\s*Vector2i\(\s*(-?\d+)\s*,\s*(-?\d+)\s*\)\s*$", block, re.MULTILINE)
        if not m_mar or not m_sep:
            fail(f"atlas source {bi}: missing margins or separation")
        mx, my = int(m_mar.group(1)), int(m_mar.group(2))
        sx, sy = int(m_sep.group(1)), int(m_sep.group(2))
        for ac in re.findall(r"^\s*(\d+):(\d+)/", block, re.MULTILINE):
            ax, ay = int(ac[0]), int(ac[1])
            left = mx + ax * (16 + sx)
            top = my + ay * (16 + sy)
            right = left + 16
            bottom = top + 16
            if left < 0 or top < 0 or right > pw or bottom > ph:
                fail(
                    f"atlas source {bi}: tile ({ax},{ay}) region Rect2i({left},{top},16,16) "
                    f"outside PNG bounds {pw}x{ph}"
                )

    # MainScene: TileMap + spawn marker (Godot 4 text scene; structural parse only).
    scene = root / "MainScene.tscn"
    if not scene.is_file():
        fail(f"missing {scene.relative_to(root)}")
    scene_text = scene.read_text(encoding="utf-8")
    if "[node name=\"TileMap\" type=\"TileMap\"" not in scene_text:
        fail("MainScene.tscn must contain a TileMap node")
    if "tile_set = ExtResource(" not in scene_text:
        fail("MainScene.tscn TileMap must set tile_set = ExtResource(...)")
    if 'path="res://assets/tilesets/lpc_terrain.tres"' not in scene_text:
        fail("MainScene.tscn must reference res://assets/tilesets/lpc_terrain.tres")
    if "[node name=\"PlayerSpawn\" type=\"Node2D\"" not in scene_text:
        fail("MainScene.tscn must contain a Node2D named PlayerSpawn")
    if not re.search(r"^\s*position\s*=\s*Vector2\(\s*160\s*,\s*160\s*\)\s*$", scene_text, re.MULTILINE):
        fail("PlayerSpawn must use position = Vector2(160, 160)")

    total_cells = 0
    source_ids: set[int] = set()
    layer_tile_re = re.compile(
        r"^\s*layer_(\d+)/tile_data\s*=\s*PackedInt32Array\(\s*(.*?)\s*\)\s*$",
        re.MULTILINE | re.DOTALL,
    )
    for m in layer_tile_re.finditer(scene_text):
        inner = m.group(2).strip()
        if not inner:
            nums: list[int] = []
        else:
            nums = [int(x.strip()) for x in inner.split(",") if x.strip()]
        if len(nums) % 3 != 0:
            fail(f"layer {m.group(1)} tile_data length {len(nums)} is not a multiple of 3")
        total_cells += len(nums) // 3
        for i in range(0, len(nums), 3):
            blob = struct.pack("<iii", nums[i], nums[i + 1], nums[i + 2])
            _x, _y, sid, _ax, _ay, _alt = struct.unpack_from("<HHHHHH", blob, 0)
            source_ids.add(int(sid))
    if total_cells != 40 * 23:
        fail(f"expected 920 populated TileMap cells, got {total_cells}")
    if len(source_ids) < 2:
        fail("TileMap must use at least two distinct tile source IDs across layers")

    print("validate: OK")


if __name__ == "__main__":
    main()
