#!/usr/bin/env python3
"""
TELVAR-RPG validation script (bootstrap + structural checks).
Full validation is implemented in spec #1246.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent

errors = []


def require_text(text: str, needle: str, message: str) -> None:
    if needle not in text:
        errors.append(message)


def parse_tscn_nodes(text: str) -> dict[str, dict[str, str]]:
    """Parse enough Godot text scene structure for validation.py checks."""
    nodes: dict[str, dict[str, str]] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("[node "):
            continue

        attrs: dict[str, str] = {}
        chunk = line.removeprefix("[node ").removesuffix("]")
        for part in chunk.split('" '):
            key, sep, value = part.partition("=")
            if sep:
                attrs[key] = value.strip('"')

        name = attrs.get("name")
        if name:
            nodes[name] = attrs
    return nodes

required_files = [
    REPO_ROOT / "project.godot",
    REPO_ROOT / "scenes/combat_ui.tscn",
    REPO_ROOT / "scripts/combat_ui.gd",
    REPO_ROOT / "scripts/combat_manager.gd",
    REPO_ROOT / "scripts/player_combat_actions.gd",
]
for path in required_files:
    if not path.is_file():
        errors.append(f"Missing required file: {path.relative_to(REPO_ROOT)}")

project_path = REPO_ROOT / "project.godot"
if project_path.is_file():
    project_text = project_path.read_text(encoding="utf-8")
    if "CombatManager=" not in project_text or "scripts/combat_manager.gd" not in project_text:
        errors.append("project.godot must autoload CombatManager at scripts/combat_manager.gd")
    if "PlayerCombatActions=" not in project_text or "scripts/player_combat_actions.gd" not in project_text:
        errors.append("project.godot must autoload PlayerCombatActions at scripts/player_combat_actions.gd")
    if "run/main_scene" not in project_text or "combat_ui.tscn" not in project_text:
        errors.append("project.godot should set run/main_scene to scenes/combat_ui.tscn")

combat_scene = REPO_ROOT / "scenes/combat_ui.tscn"
if combat_scene.is_file():
    tscn = combat_scene.read_text(encoding="utf-8")
    nodes = parse_tscn_nodes(tscn)

    expected_nodes = {
        "CombatUI": {"type": "CanvasLayer"},
        "Root": {"type": "Control", "parent": "."},
        "PlayerHPBar": {"type": "ProgressBar", "parent": "Root/StatsColumn/PlayerRow"},
        "EnemyHPBar": {"type": "ProgressBar", "parent": "Root/StatsColumn/EnemyRow"},
        "ActionMenuVBox": {"type": "VBoxContainer", "parent": "Root"},
        "Attack": {"type": "Button", "parent": "Root/ActionMenuVBox"},
        "CastSpell": {"type": "Button", "parent": "Root/ActionMenuVBox"},
        "Flee": {"type": "Button", "parent": "Root/ActionMenuVBox"},
        "UseItem": {"type": "Button", "parent": "Root/ActionMenuVBox"},
    }
    for name, attrs in expected_nodes.items():
        if name not in nodes:
            errors.append(f"scenes/combat_ui.tscn missing node {name!r}")
            continue
        for attr, expected in attrs.items():
            actual = nodes[name].get(attr)
            if actual != expected:
                errors.append(
                    f"scenes/combat_ui.tscn node {name!r} must have {attr}={expected!r}, got {actual!r}"
                )

    require_text(
        tscn,
        'path="res://scripts/combat_ui.gd"',
        "scenes/combat_ui.tscn must attach scripts/combat_ui.gd",
    )
    for label in ('text = "Attack"', 'text = "Cast Spell"', 'text = "Flee"', 'text = "Use Item"'):
        require_text(tscn, label, f"scenes/combat_ui.tscn must contain button {label}")

actions_script = REPO_ROOT / "scripts/player_combat_actions.gd"
if actions_script.is_file():
    actions = actions_script.read_text(encoding="utf-8")
    action_checks = [
        ("const MELEE_RANGE_TILES: int = 1", "Attack must be range 1"),
        ("const FLEE_SUCCESS_CHANCE: float = 0.6", "Flee success chance must be 60%"),
        ("const HEALING_HERB_HP: int = 10", "Healing herb must restore 10 HP"),
        ("randi_range(2, 6)", "Attack/counterattack damage must use 2-6 range"),
        ("CombatManager.enemy_hp = maxi(0, CombatManager.enemy_hp - damage)", "Attack must apply enemy HP damage"),
        ("_refresh_enemy_hp_bar()", "Attack must refresh enemy HP bar"),
        ("_spawn_damage_float(damage)", "Attack must spawn floating damage text"),
        ("randf() < FLEE_SUCCESS_CHANCE", "Flee must roll against configured chance"),
        ("CombatManager.player_hp = maxi(0, CombatManager.player_hp - damage)", "Failed flee must counterattack player"),
        ("CombatManager.player_hp = mini(CombatManager.player_max_hp, CombatManager.player_hp + HEALING_HERB_HP)", "Use Item must clamp healing herb recovery"),
    ]
    for needle, message in action_checks:
        require_text(actions, needle, f"scripts/player_combat_actions.gd: {message}")

combat_ui_script = REPO_ROOT / "scripts/combat_ui.gd"
if combat_ui_script.is_file():
    ui = combat_ui_script.read_text(encoding="utf-8")
    ui_checks = [
        ("@onready var player_hp_bar: ProgressBar = %PlayerHPBar", "CombatUI must bind player HP bar"),
        ("@onready var enemy_hp_bar: ProgressBar = %EnemyHPBar", "CombatUI must bind enemy HP bar"),
        ("@onready var action_menu: VBoxContainer = %ActionMenuVBox", "CombatUI must bind action menu"),
        ("CombatManager.combat_state_changed.connect(_on_combat_state_changed)", "CombatUI must observe combat state"),
        ("state == CombatManager.CombatState.PLAYER_TURN", "CombatUI must enable menu only on player turns"),
        ("b.disabled = not enabled", "CombatUI must disable buttons during enemy turns"),
    ]
    for needle, message in ui_checks:
        require_text(ui, needle, f"scripts/combat_ui.gd: {message}")

if errors:
    for e in errors:
        print("FAIL:", e)
    sys.exit(1)

print("Structural checks passed.")
sys.exit(0)
