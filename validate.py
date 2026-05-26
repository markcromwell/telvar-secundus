#!/usr/bin/env python3
"""Text-based structural validation for the Godot project (no Godot runtime).

Exits 0 when checks pass; prints lines prefixed with ``FAIL:`` and exits 1 otherwise.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent


def fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _parse_ext_resource_ids(text: str) -> dict[str, str]:
    """Map ext_resource id -> path (attribute order on the line may vary)."""
    out: dict[str, str] = {}
    for line in text.splitlines():
        if not line.startswith("[ext_resource"):
            continue
        m_path = re.search(r'path="([^"]+)"', line)
        m_id = re.search(r'id="([^"]+)"', line)
        if m_path and m_id:
            out[m_id.group(1)] = m_path.group(1)
    return out


def _iter_node_blocks(text: str) -> list[tuple[str, str, dict[str, str]]]:
    """Return list of (node_name, node_type, properties_dict) for each [node ...] section."""
    lines = text.splitlines()
    blocks: list[tuple[str, str, dict[str, str]]] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("[node "):
            m_name = re.search(r'name="([^"]*)"', line)
            m_type = re.search(r'type="([^"]*)"', line)
            if not m_name or not m_type:
                i += 1
                continue
            name, typ = m_name.group(1), m_type.group(1)
            props: dict[str, str] = {}
            i += 1
            while i < len(lines) and not lines[i].startswith("["):
                raw = lines[i]
                if "=" in raw and not raw.strip().startswith("#"):
                    k, _, rest = raw.partition("=")
                    props[k.strip()] = rest.strip()
                i += 1
            blocks.append((name, typ, props))
            continue
        i += 1
    return blocks


def check_project_godot() -> bool:
    path = REPO_ROOT / "project.godot"
    if not path.is_file():
        fail("missing project.godot at repo root")
        return False
    if not path.stat().st_size:
        fail("project.godot is empty")
        return False
    return True


def check_all_godot_sources() -> bool:
    """Every *.tscn and *.gd under the repo (excluding VCS) must exist as a readable file."""
    ok = True
    skip_parts = {".git"}
    for pattern in ("**/*.tscn", "**/*.gd"):
        for p in REPO_ROOT.glob(pattern):
            if any(part in skip_parts for part in p.parts):
                continue
            if not p.is_file():
                fail(f"expected file missing: {p.relative_to(REPO_ROOT)}")
                ok = False
            elif p.stat().st_size == 0:
                fail(f"empty file: {p.relative_to(REPO_ROOT)}")
                ok = False
    # Require at least one scene and one script (sanity for empty tree)
    tscns = [p for p in REPO_ROOT.glob("**/*.tscn") if ".git" not in p.parts]
    gds = [p for p in REPO_ROOT.glob("**/*.gd") if ".git" not in p.parts]
    if not tscns:
        fail("no .tscn files found under repo root")
        ok = False
    if not gds:
        fail("no .gd files found under repo root")
        ok = False
    return ok


def check_well_burst(path: Path) -> bool:
    if not path.is_file():
        fail(f"missing {path.relative_to(REPO_ROOT)}")
        return False
    text = _read(path)
    blocks = _iter_node_blocks(text)
    gpu = [(n, t, pr) for n, t, pr in blocks if t == "GPUParticles2D"]
    if not gpu:
        fail("WellBurst.tscn: no GPUParticles2D node")
        return False
    _name, _t, props = gpu[0]
    if props.get("lifetime") != "0.5":
        fail("WellBurst.tscn: GPUParticles2D must set lifetime = 0.5")
        return False
    if props.get("one_shot") != "true":
        fail("WellBurst.tscn: GPUParticles2D must set one_shot = true")
        return False
    if "emission_sphere_radius = 160" not in text and "emission_sphere_radius = 160.0" not in text:
        fail("WellBurst.tscn: particle material must set emission_sphere_radius = 160 (5 tiles)")
        return False
    return True


def check_myramar_distant(path: Path) -> bool:
    if not path.is_file():
        fail(f"missing {path.relative_to(REPO_ROOT)}")
        return False
    text = _read(path)
    if not re.search(r'\[node[^\]]*type="Sprite2D"', text):
        fail("MyramarDistant.tscn: missing Sprite2D node")
        return False
    blocks = _iter_node_blocks(text)
    root_pos = None
    for name, typ, props in blocks:
        if name == "MyramarDistant" and typ == "Node2D":
            pos = props.get("position")
            if pos and pos.startswith("Vector2("):
                m = re.match(r"Vector2\(\s*([+-]?\d+(?:\.\d+)?)\s*,\s*([+-]?\d+(?:\.\d+)?)\s*\)", pos)
                if m:
                    root_pos = (float(m.group(1)), float(m.group(2)))
            break
    if root_pos is None:
        fail("MyramarDistant.tscn: could not parse root Node2D position")
        return False
    x, y = root_pos
    # 1280x720 design resolution: NW quadrant (strict half viewport)
    if not (x < 640.0 and y < 360.0):
        fail(
            f"MyramarDistant.tscn: root position {root_pos} is not in NW viewport quadrant "
            "(expect x < 640 and y < 360)"
        )
        return False
    return True


def check_thug_npc_script(path: Path) -> bool:
    if not path.is_file():
        fail(f"missing {path.relative_to(REPO_ROOT)}")
        return False
    text = _read(path)
    if "func start_flee(" not in text:
        fail("scripts/ThugNPC.gd must define func start_flee(")
        return False
    if "_fleeing" not in text:
        fail("scripts/ThugNPC.gd must define or reference _fleeing state")
        return False
    return True


def check_world_tscn(path: Path) -> bool:
    if not path.is_file():
        fail(f"missing {path.relative_to(REPO_ROOT)}")
        return False
    text = _read(path)
    if 'path="res://scripts/WellEvent.gd"' not in text:
        fail("World.tscn must reference WellEvent.gd (ext_resource path)")
        return False
    ext = _parse_ext_resource_ids(text)
    thug_ids = [eid for eid, pth in ext.items() if pth.endswith("ThugNPC.tscn")]
    if not thug_ids:
        fail("World.tscn must include an ext_resource for ThugNPC.tscn")
        return False
    count = 0
    for eid in thug_ids:
        count += len(re.findall(rf'instance=ExtResource\("{re.escape(eid)}"\)', text))
    if count < 2:
        fail("World.tscn must instance ThugNPC at least twice (two thugs)")
        return False
    return True


def main() -> int:
    checks = [
        check_project_godot(),
        check_all_godot_sources(),
        check_well_burst(REPO_ROOT / "scenes/effects/WellBurst.tscn"),
        check_myramar_distant(REPO_ROOT / "scenes/npcs/MyramarDistant.tscn"),
        check_thug_npc_script(REPO_ROOT / "scripts/ThugNPC.gd"),
        check_world_tscn(REPO_ROOT / "scenes/world/World.tscn"),
    ]

    if not all(checks):
        return 1

    print("validate.py: all structural checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
