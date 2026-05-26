#!/usr/bin/env python3
"""Structural validation for TileSet and MainScene (text parse; no Godot runtime)."""
from __future__ import annotations

import re
import struct
import sys
from pathlib import Path

EXPECTED_TILESET_PATH = "res://assets/tilesets/lpc_terrain.tres"
LPC_IMPORT_REL = Path("assets") / "tilesets" / "lpc_terrain.png.import"


def fail(msg: str) -> None:
    print(f"validate: FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def _parse_ext_resource_ids(scene_text: str) -> dict[str, str]:
    """Map ExtResource id -> res:// path from [ext_resource ...] lines."""
    out: dict[str, str] = {}
    for m in re.finditer(r"\[ext_resource([^\]]*)\]", scene_text):
        block = m.group(1)
        pm = re.search(r'path="([^"]+)"', block)
        im = re.search(r'\bid="([^"]+)"', block)
        if pm and im:
            out[im.group(1)] = pm.group(1)
    return out


def _tilemap_node_body(scene_text: str) -> str | None:
    m = re.search(
        r'^\[node name="TileMap" type="TileMap"[^\]]*\]\s*\n(.*?)(?=^\[node |\Z)',
        scene_text,
        re.MULTILINE | re.DOTALL,
    )
    return m.group(1) if m else None


def _playerspawn_position(scene_text: str) -> tuple[float, float] | None:
    m = re.search(
        r'^\[node name="PlayerSpawn" type="Node2D"[^\]]*\]\s*\n'
        r'(.*?)(?=^\[node |\Z)',
        scene_text,
        re.MULTILINE | re.DOTALL,
    )
    if not m:
        return None
    body = m.group(1)
    pm = re.search(r"^\s*position\s*=\s*Vector2\(\s*([-\d.]+)\s*,\s*([-\d.]+)\s*\)\s*$", body, re.MULTILINE)
    if not pm:
        return None
    return float(pm.group(1)), float(pm.group(2))


def _import_disables_texture_filter(import_text: str) -> bool:
    """True if Godot import settings disable filtering (pixel art)."""
    if re.search(r"^\s*flags/filter\s*=\s*false\s*$", import_text, re.MULTILINE):
        return True
    if re.search(r"^\s*filter\s*=\s*false\s*$", import_text, re.MULTILINE):
        return True
    return False


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

    lpc_import = root / LPC_IMPORT_REL
    if not lpc_import.is_file():
        fail(f"missing {lpc_import.relative_to(root)}")
    import_text = lpc_import.read_text(encoding="utf-8")
    if not _import_disables_texture_filter(import_text):
        fail("filter not disabled")

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

    tilemap_body = _tilemap_node_body(scene_text)
    if tilemap_body is None:
        fail("TileMap node missing")

    ext_by_id = _parse_ext_resource_ids(scene_text)
    ts_m = re.search(r'tile_set\s*=\s*ExtResource\("([^"]+)"\)', tilemap_body)
    if not ts_m:
        fail("TileMap node must set tile_set = ExtResource(...)")
    tileset_ref = ts_m.group(1)
    resolved = ext_by_id.get(tileset_ref)
    if resolved != EXPECTED_TILESET_PATH:
        fail(
            f"TileMap tile_set ExtResource({tileset_ref!r}) must resolve to "
            f"{EXPECTED_TILESET_PATH!r}, got {resolved!r}"
        )

    if "[node name=\"PlayerSpawn\" type=\"Node2D\"" not in scene_text:
        fail("MainScene.tscn must contain a Node2D named PlayerSpawn")
    spawn_pos = _playerspawn_position(scene_text)
    if spawn_pos != (160.0, 160.0):
        fail("PlayerSpawn position mismatch")

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
