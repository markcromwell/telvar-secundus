"""Validate assets/dialogue/myramar.json for the Confront path (spec phase 2710)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
MYRAMAR_DIALOGUE = REPO_ROOT / "assets" / "dialogue" / "myramar.json"


def _load_dialogue_tree() -> list[dict]:
    assert MYRAMAR_DIALOGUE.is_file(), f"Missing dialogue file: {MYRAMAR_DIALOGUE}"
    data = json.loads(MYRAMAR_DIALOGUE.read_text(encoding="utf-8"))
    assert isinstance(data, list), "Dialogue root must be a JSON array"
    for i, node in enumerate(data):
        assert isinstance(node, dict), f"Entry {i} must be an object"
        assert "id" in node and isinstance(node["id"], str), f"Entry {i} needs string id"
    return data


def test_myramar_dialogue_json_loads() -> None:
    tree = _load_dialogue_tree()
    assert len(tree) >= 1


def test_myramar_dialogue_references_valid() -> None:
    tree = _load_dialogue_tree()
    ids = {node["id"] for node in tree}

    def _check_ref(ref: str, ctx: str) -> None:
        assert ref in ids, f"{ctx}: unknown next id {ref!r}"

    for node in tree:
        nid = node["id"]
        if "next" in node and node["next"] is not None:
            _check_ref(str(node["next"]), f"node {nid!r}")
        for choice in node.get("choices", []) or []:
            assert "next" in choice, f"choice in {nid!r} missing next"
            _check_ref(str(choice["next"]), f"choice in {nid!r}")


def test_confront_path_three_exchanges_myramar_unreadable() -> None:
    """Exactly three Telvar↔Myramar exchanges; Myramar lines stay unreadable (obfuscated)."""
    tree = _load_dialogue_tree()
    by_id = {n["id"]: n for n in tree}

    assert "confront_exchange_1_telvar" in by_id
    assert "confront_exchange_3_myramar" in by_id

    chain = [
        "confront_exchange_1_telvar",
        "confront_exchange_1_myramar",
        "confront_exchange_2_telvar",
        "confront_exchange_2_myramar",
        "confront_exchange_3_telvar",
        "confront_exchange_3_myramar",
    ]
    for cid in chain:
        assert cid in by_id, f"missing confront node {cid}"

    for mid in (
        "confront_exchange_1_myramar",
        "confront_exchange_2_myramar",
        "confront_exchange_3_myramar",
    ):
        text = str(by_id[mid].get("text", ""))
        assert "▒" in text or "▓" in text or "░" in text, f"{mid} should look unreadable/obfuscated"

    assert by_id["confront_exchange_1_telvar"].get("next") == "confront_exchange_1_myramar"
    assert by_id["confront_exchange_3_myramar"].get("next") == "after_confront_choice"


def test_outcomes_walk_away_and_walk_in() -> None:
    tree = _load_dialogue_tree()
    by_id = {n["id"]: n for n in tree}
    assert "outcome_walk_away_gameover" in by_id
    assert "outcome_walk_in_wings" in by_id
    assert by_id["outcome_walk_away_gameover"].get("outcome") == "game_over_save_prompt"
    assert by_id["outcome_walk_in_wings"].get("outcome") == "transition_wings"


def test_after_evidence_binary_choice() -> None:
    tree = _load_dialogue_tree()
    by_id = {n["id"]: n for n in tree}
    node = by_id["after_evidence_choice"]
    choices = node.get("choices") or []
    assert len(choices) == 2


def test_after_confront_binary_choice() -> None:
    tree = _load_dialogue_tree()
    by_id = {n["id"]: n for n in tree}
    node = by_id["after_confront_choice"]
    choices = node.get("choices") or []
    assert len(choices) == 2
    nexts = {c["next"] for c in choices}
    assert "outcome_walk_away_gameover" in nexts
    assert "outcome_walk_in_wings" in nexts
