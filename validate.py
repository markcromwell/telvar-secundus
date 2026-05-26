#!/usr/bin/env python3
"""
TELVAR-RPG structural validation (no Godot binary).

Checks project-critical assets using plain Python parsing. Exits 0 on success.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent
MYRAMAR_JSON = REPO_ROOT / "assets" / "dialogue" / "myramar.json"

# Phase 1 branch entry nodes; `start` must offer choices that route here.
MYRAMAR_MISSING_APPRENTICES_DIPLOMATIC_ENTRY = "myramar_deflect_missing_apprentices_diplomatic_a"
MYRAMAR_MISSING_APPRENTICES_CONFRONTATIONAL_ENTRY = (
    "myramar_deflect_missing_apprentices_confrontational_a"
)
MYRAMAR_MISSING_APPRENTICES_CLOSE = "myramar_missing_apprentices_close_neutral"


def _collect_next_targets(node: dict[str, Any]) -> list[str]:
    """Return all non-null `next` ids referenced from a dialogue node."""
    out: list[str] = []
    if "choices" in node:
        ch = node.get("choices")
        if not isinstance(ch, list):
            return out
        for c in ch:
            if not isinstance(c, dict):
                continue
            nxt = c.get("next")
            if nxt is None:
                continue
            if isinstance(nxt, str) and nxt:
                out.append(nxt)
    if "next" in node:
        nxt = node["next"]
        if isinstance(nxt, str) and nxt:
            out.append(nxt)
    return out


def validate_myramar_dialogue() -> list[str]:
    """Validate assets/dialogue/myramar.json structure and missing-apprentices routing."""
    errors: list[str] = []
    if not MYRAMAR_JSON.is_file():
        errors.append(f"Missing dialogue file: {MYRAMAR_JSON.relative_to(REPO_ROOT)}")
        return errors

    try:
        raw = MYRAMAR_JSON.read_text(encoding="utf-8")
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON in myramar.json: {e}")
        return errors

    if not isinstance(data, list):
        errors.append("myramar.json: root must be a JSON array of nodes")
        return errors

    by_id: dict[str, dict[str, Any]] = {}
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            errors.append(f"myramar.json: node {i} must be an object")
            continue
        nid = item.get("id")
        if not isinstance(nid, str) or not nid.strip():
            errors.append(f"myramar.json: node {i} missing non-empty string 'id'")
            continue
        if nid in by_id:
            errors.append(f"myramar.json: duplicate dialogue id {nid!r}")
            continue
        by_id[nid] = item

    for nid, node in by_id.items():
        if not isinstance(node.get("text"), str) or not str(node["text"]).strip():
            errors.append(f"myramar.json: node {nid!r} needs non-empty string 'text'")
        if not isinstance(node.get("speaker"), str) or not str(node["speaker"]).strip():
            errors.append(f"myramar.json: node {nid!r} needs non-empty string 'speaker'")

        has_choices = "choices" in node
        has_next = "next" in node
        if has_choices and has_next:
            errors.append(f"myramar.json: node {nid!r} must not mix top-level 'next' with 'choices'")
            continue
        if not has_choices and not has_next:
            errors.append(f"myramar.json: node {nid!r} needs either 'choices' or 'next'")
            continue

        if has_choices:
            ch = node["choices"]
            if not isinstance(ch, list) or len(ch) == 0:
                errors.append(f"myramar.json: node {nid!r} 'choices' must be a non-empty array")
                continue
            for j, c in enumerate(ch):
                if not isinstance(c, dict):
                    errors.append(f"myramar.json: node {nid!r} choice {j} must be an object")
                    continue
                if not isinstance(c.get("text"), str) or not str(c["text"]).strip():
                    errors.append(f"myramar.json: node {nid!r} choice {j} needs non-empty 'text'")
                nxt = c.get("next")
                if not isinstance(nxt, str) or not nxt.strip():
                    errors.append(f"myramar.json: node {nid!r} choice {j} needs non-empty string 'next'")
        else:
            nxt = node["next"]
            if nxt is not None and not isinstance(nxt, str):
                errors.append(f"myramar.json: node {nid!r} 'next' must be string or null")

    if errors:
        return errors

    # Graph integrity: every referenced next id exists (except we already validated non-empty str).
    for nid, node in by_id.items():
        for tgt in _collect_next_targets(node):
            if tgt not in by_id:
                errors.append(f"myramar.json: node {nid!r} references unknown id {tgt!r}")

    if "start" not in by_id:
        errors.append("myramar.json: missing required node id 'start'")

    if errors:
        return errors

    start = by_id["start"]
    if "choices" not in start:
        errors.append("myramar.json: 'start' must expose player choices (missing-apprentices hub)")
        return errors

    start_targets = _collect_next_targets(start)
    if MYRAMAR_MISSING_APPRENTICES_DIPLOMATIC_ENTRY not in start_targets:
        errors.append(
            "myramar.json: 'start' must offer a choice routing to "
            f"{MYRAMAR_MISSING_APPRENTICES_DIPLOMATIC_ENTRY!r} (diplomatic missing-apprentices path)"
        )
    if MYRAMAR_MISSING_APPRENTICES_CONFRONTATIONAL_ENTRY not in start_targets:
        errors.append(
            "myramar.json: 'start' must offer a choice routing to "
            f"{MYRAMAR_MISSING_APPRENTICES_CONFRONTATIONAL_ENTRY!r} (confrontational path)"
        )

    if MYRAMAR_MISSING_APPRENTICES_CLOSE not in by_id:
        errors.append(f"myramar.json: missing closing node {MYRAMAR_MISSING_APPRENTICES_CLOSE!r}")

    close = by_id.get(MYRAMAR_MISSING_APPRENTICES_CLOSE)
    if close is not None:
        if "choices" in close:
            errors.append(
                f"myramar.json: node {MYRAMAR_MISSING_APPRENTICES_CLOSE!r} should end the branch (no choices)"
            )
        if "next" not in close or close["next"] is not None:
            errors.append(
                f"myramar.json: node {MYRAMAR_MISSING_APPRENTICES_CLOSE!r} must use \"next\": null to end"
            )

    return errors


def collect_validation_errors() -> list[str]:
    """All repository checks for validate.py and CI."""
    return validate_myramar_dialogue()


def main() -> None:
    errors = collect_validation_errors()
    if errors:
        for e in errors:
            print("FAIL:", e)
        sys.exit(1)
    print("Validation passed (myramar dialogue structure OK)")
    sys.exit(0)


if __name__ == "__main__":
    main()
