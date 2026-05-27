"""Unit tests for validate.py structural checks (synthetic projects in tmp_path)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _validate_script() -> Path:
    return _repo_root() / "validate.py"


def _run_validate(cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(_validate_script())],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )


_VALID_PROJECT_GODOT = """\
; minimal stub for validate.py
[display]
window/size/viewport_width=1280
"""

_VALID_MAIN_SCENE = """\
[gd_scene load_steps=1 format=3]

[node name="MainScene" type="Node2D"]

[node name="TileMap" type="TileMap" parent="."]

[node name="Player" type="CharacterBody2D" parent="."]

[node name="Camera2D" type="Camera2D" parent="Player"]
position_smoothing_enabled = true
position_smoothing_speed = 10.0
"""

_VALID_PLAYER_GD = """\
extends CharacterBody2D

@export var speed: float = 64.0
@export var can_move: bool = true

func _physics_process(_delta):
	pass
"""

_VALID_CREDITS = """\
# Credits
LPC terrain placeholder for validation tests.
"""


def _write_minimal_valid_project(tmp: Path) -> None:
    tmp.mkdir(parents=True, exist_ok=True)
    (tmp / "project.godot").write_text(_VALID_PROJECT_GODOT, encoding="utf-8")
    (tmp / "MainScene.tscn").write_text(_VALID_MAIN_SCENE, encoding="utf-8")
    (tmp / "Player.gd").write_text(_VALID_PLAYER_GD, encoding="utf-8")
    (tmp / "CREDITS.md").write_text(_VALID_CREDITS, encoding="utf-8")


def test_validate_exits_zero_for_fully_valid_synthetic_project(tmp_path: Path) -> None:
    _write_minimal_valid_project(tmp_path)
    result = _run_validate(tmp_path)
    assert result.returncode == 0, (
        f"expected exit 0, got {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "All checks passed" in result.stdout


def test_validate_exits_one_when_mainscene_missing_tilemap(tmp_path: Path) -> None:
    _write_minimal_valid_project(tmp_path)
    main_no_tilemap = """\
[gd_scene load_steps=1 format=3]

[node name="MainScene" type="Node2D"]

[node name="Player" type="CharacterBody2D" parent="."]

[node name="Camera2D" type="Camera2D" parent="Player"]
position_smoothing_enabled = true
position_smoothing_speed = 10.0
"""
    (tmp_path / "MainScene.tscn").write_text(main_no_tilemap, encoding="utf-8")
    result = _run_validate(tmp_path)
    assert result.returncode == 1
    assert "TileMap" in result.stdout or "TileMap" in (result.stderr or "")


def test_validate_exits_one_when_mainscene_player_not_characterbody2d(tmp_path: Path) -> None:
    _write_minimal_valid_project(tmp_path)
    main_wrong_player = """\
[gd_scene load_steps=1 format=3]

[node name="MainScene" type="Node2D"]

[node name="TileMap" type="TileMap" parent="."]

[node name="Player" type="Area2D" parent="."]

[node name="Camera2D" type="Camera2D" parent="Player"]
position_smoothing_enabled = true
position_smoothing_speed = 10.0
"""
    (tmp_path / "MainScene.tscn").write_text(main_wrong_player, encoding="utf-8")
    result = _run_validate(tmp_path)
    assert result.returncode == 1
    out = result.stdout + (result.stderr or "")
    assert "Player" in out and "CharacterBody2D" in out


def test_validate_exits_one_when_player_gd_missing_speed_export(tmp_path: Path) -> None:
    _write_minimal_valid_project(tmp_path)
    gd = """\
extends CharacterBody2D

@export var can_move: bool = true

func _physics_process(_delta):
	pass
"""
    (tmp_path / "Player.gd").write_text(gd, encoding="utf-8")
    result = _run_validate(tmp_path)
    assert result.returncode == 1
    assert "speed" in result.stdout


def test_validate_exits_one_when_player_gd_missing_can_move_export(tmp_path: Path) -> None:
    _write_minimal_valid_project(tmp_path)
    gd = """\
extends CharacterBody2D

@export var speed: float = 64.0

func _physics_process(_delta):
	pass
"""
    (tmp_path / "Player.gd").write_text(gd, encoding="utf-8")
    result = _run_validate(tmp_path)
    assert result.returncode == 1
    assert "can_move" in result.stdout


def test_credits_md_at_repo_root_contains_lpc() -> None:
    root = _repo_root()
    credits = root / "CREDITS.md"
    assert credits.is_file(), "CREDITS.md must exist at repository root"
    text = credits.read_text(encoding="utf-8")
    assert "LPC" in text
