extends Node

## Turn-based combat coordinator. Drives CombatUI enable/disable from state.

enum CombatState {
	PLAYER_TURN,
	ENEMY_TURN,
}

signal combat_state_changed(state: CombatState)

var combat_state: CombatState = CombatState.PLAYER_TURN:
	set(value):
		if combat_state == value:
			return
		combat_state = value
		combat_state_changed.emit(combat_state)

var player_max_hp: int = 30
var player_hp: int = 30
var enemy_max_hp: int = 25
var enemy_hp: int = 25


func is_player_turn() -> bool:
	return combat_state == CombatState.PLAYER_TURN


func begin_player_turn() -> void:
	combat_state = CombatState.PLAYER_TURN


func begin_enemy_turn() -> void:
	combat_state = CombatState.ENEMY_TURN
