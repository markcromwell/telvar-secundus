#!/usr/bin/env python3
"""
Structural validation for Telvar Secundus (Godot 4.x text resources).

Uses stdlib only — no Godot binary. Intended for CI and worker pipelines.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent
errors: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def require_file(rel: str) -> Path | None:
    path = REPO_ROOT / rel
    if not path.is_file():
        err(f"missing file: {rel}")
        return None
    return path


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        err(f"invalid JSON {path.relative_to(REPO_ROOT)}: {exc}")
        return None


def _dialogue_by_id(nodes: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for node in nodes:
        node_id = node.get("id")
        if not isinstance(node_id, str) or not node_id:
            err("timon.json: dialogue node missing non-empty string id")
            continue
        if node_id in out:
            err(f"timon.json: duplicate dialogue id {node_id!r}")
        out[node_id] = node
    return out


def _choice_texts(entry: dict[str, Any]) -> list[str]:
    choices = entry.get("choices")
    if choices is None:
        return []
    if not isinstance(choices, list):
        err(f"timon.json: node {entry.get('id')!r} choices must be a list")
        return []
    texts: list[str] = []
    for i, ch in enumerate(choices):
        if not isinstance(ch, dict):
            err(f"timon.json: node {entry.get('id')!r} choice[{i}] must be an object")
            continue
        t = ch.get("text")
        if not isinstance(t, str):
            err(f"timon.json: node {entry.get('id')!r} choice[{i}] text must be a string")
            continue
        texts.append(t)
    return texts


def _choice_nexts(entry: dict[str, Any]) -> list[tuple[str, str]]:
    """Return (text, next_id) for each choice."""
    choices = entry.get("choices")
    if not isinstance(choices, list):
        return []
    out: list[tuple[str, str]] = []
    for i, ch in enumerate(choices):
        if not isinstance(ch, dict):
            continue
        text = ch.get("text")
        nxt = ch.get("next")
        if isinstance(text, str) and isinstance(nxt, str):
            out.append((text, nxt))
        else:
            err(f"timon.json: node {entry.get('id')!r} choice[{i}] needs string text and next")
    return out


def validate_quest_timons_spectacles(path: Path) -> None:
    data = _load_json(path)
    if not isinstance(data, dict):
        err("timons_spectacles.json: root must be an object")
        return
    if data.get("id") != "timons_spectacles":
        err('timons_spectacles.json: id must be "timons_spectacles"')
    objectives = data.get("objectives")
    if not isinstance(objectives, list) or not objectives:
        err("timons_spectacles.json: objectives must be a non-empty list")
        return
    ids = [o.get("id") for o in objectives if isinstance(o, dict)]
    if "find_spectacles" not in ids:
        err('timons_spectacles.json: must include objective id "find_spectacles"')


def validate_lore_banishment_codex(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if 'lore_id = "banishment_codex"' not in text:
        err('banishment_codex.tres: expected lore_id = "banishment_codex"')
    if 'title = "The Banishment Codex"' not in text:
        err('banishment_codex.tres: expected title = "The Banishment Codex"')


def validate_spectacles_scene(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if "Area2D" not in text:
        err("spectacles.tscn: expected Area2D node type text")


def validate_timon_dialogue(path: Path) -> None:
    data = _load_json(path)
    if not isinstance(data, list) or not data:
        err("timon.json: root must be a non-empty dialogue array")
        return

    by_id = _dialogue_by_id(data)
    required_nodes = (
        "start",
        "spectacles_problem",
        "quest_accepted",
        "codex_reveal_1",
        "codex_reveal_2",
        "codex_reveal_3",
        "codex_aftermath",
    )
    for rid in required_nodes:
        if rid not in by_id:
            err(f"timon.json: missing required dialogue id {rid!r}")

    start = by_id.get("start")
    if start:
        found_gate = False
        for text, nxt in _choice_nexts(start):
            if nxt == "codex_reveal_1":
                if "[quest_complete:timons_spectacles:find_spectacles]" in text:
                    found_gate = True
                else:
                    err(
                        "timon.json: choice leading to codex_reveal_1 must include "
                        "[quest_complete:timons_spectacles:find_spectacles] "
                        "(spectacles quest must be completed first)"
                    )
        if not found_gate:
            err(
                "timon.json: start must offer a choice to codex_reveal_1 gated by "
                "[quest_complete:timons_spectacles:find_spectacles]"
            )

    prob = by_id.get("spectacles_problem")
    if prob:
        texts = " ".join(_choice_texts(prob))
        if "[quest_give:timons_spectacles]" not in texts:
            err("timon.json: spectacles_problem must offer [quest_give:timons_spectacles]")

    r1, r2, r3 = by_id.get("codex_reveal_1"), by_id.get("codex_reveal_2"), by_id.get("codex_reveal_3")
    if r1 and r2:
        nexts = [n for _, n in _choice_nexts(r1)]
        if "codex_reveal_2" not in nexts:
            err("timon.json: codex_reveal_1 must link to codex_reveal_2")
    if r2 and r3:
        nexts = [n for _, n in _choice_nexts(r2)]
        if "codex_reveal_3" not in nexts:
            err("timon.json: codex_reveal_2 must link to codex_reveal_3")

    if r3:
        found_lore = False
        for text, nxt in _choice_nexts(r3):
            if "[lore_unlock:banishment_codex]" in text:
                found_lore = True
                if nxt != "codex_aftermath":
                    err(
                        "timon.json: codex_reveal_3 lore choice should continue to "
                        "codex_aftermath after [lore_unlock:banishment_codex]"
                    )
        if not found_lore:
            err("timon.json: codex_reveal_3 must include [lore_unlock:banishment_codex] on a choice")


def main() -> int:
    quest = require_file("assets/quests/timons_spectacles.json")
    lore = require_file("assets/lore/banishment_codex.tres")
    scene = require_file("scenes/items/spectacles.tscn")
    dialogue = require_file("assets/dialogue/timon.json")

    if quest:
        validate_quest_timons_spectacles(quest)
    if lore:
        validate_lore_banishment_codex(lore)
    if scene:
        validate_spectacles_scene(scene)
    if dialogue:
        validate_timon_dialogue(dialogue)

    if errors:
        for e in errors:
            print("FAIL:", e)
        return 1

    print("validate.py: all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
