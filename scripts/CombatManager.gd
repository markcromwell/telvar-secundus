extends Node
## Autoload singleton: combat flow, initiative (d6 + speed), and turn order.

enum CombatState {
	PLAYER_TURN,
	ENEMY_TURN,
}

signal combat_started
signal combat_ended
signal initiative_rolled(actor_id: String, speed: int, die: int, total: int)
signal turn_advanced(round_index: int, actor_index: int, state: CombatState)

var in_combat: bool = false
## Mirrors whether the current actor is Telvar (player) or an enemy (UI / logic).
var state: CombatState = CombatState.PLAYER_TURN
var current_round: int = 0
var current_actor_index: int = 0

## Each entry: { "id": String, "is_player": bool, "speed": int, "initiative": int, "die": int }
var _turn_queue: Array[Dictionary] = []


func roll_initiative(speed: int) -> int:
	var die := randi_range(1, 6)
	return die + speed


func start_combat(player_speed: int, enemy_speeds: Array) -> void:
	if enemy_speeds.is_empty():
		push_warning("CombatManager.start_combat: no enemies; refusing to start.")
		return
	end_combat()

	in_combat = true
	current_round = 1
	_turn_queue.clear()

	var player_die := randi_range(1, 6)
	var player_total := player_die + player_speed
	_turn_queue.append(
		{
			"id": "telvar",
			"is_player": true,
			"speed": player_speed,
			"initiative": player_total,
			"die": player_die,
		}
	)
	initiative_rolled.emit("telvar", player_speed, player_die, player_total)

	var i := 0
	for spd in enemy_speeds:
		if spd is not int:
			push_warning("CombatManager.start_combat: expected int speeds, skipping entry.")
			continue
		var e_die := randi_range(1, 6)
		var e_total := e_die + spd
		var eid := "enemy_%d" % i
		_turn_queue.append(
			{
				"id": eid,
				"is_player": false,
				"speed": spd,
				"initiative": e_total,
				"die": e_die,
			}
		)
		initiative_rolled.emit(eid, spd, e_die, e_total)
		i += 1

	if _turn_queue.size() < 2:
		_turn_queue.clear()
		in_combat = false
		push_warning("CombatManager.start_combat: no valid enemies after filtering.")
		return

	_sort_initiative_queue()
	current_actor_index = 0
	_sync_state_from_current_actor()
	combat_started.emit()
	turn_advanced.emit(current_round, current_actor_index, state)


func advance_turn() -> void:
	if not in_combat or _turn_queue.is_empty():
		return
	var at_end := current_actor_index >= _turn_queue.size() - 1
	if at_end:
		current_round += 1
		current_actor_index = 0
	else:
		current_actor_index += 1
	_sync_state_from_current_actor()
	turn_advanced.emit(current_round, current_actor_index, state)


func end_combat() -> void:
	if not in_combat and _turn_queue.is_empty():
		return
	in_combat = false
	_turn_queue.clear()
	current_actor_index = 0
	current_round = 0
	state = CombatState.PLAYER_TURN
	combat_ended.emit()


func get_current_actor_id() -> String:
	if _turn_queue.is_empty():
		return ""
	return String(_turn_queue[current_actor_index].get("id", ""))


func is_current_actor_player() -> bool:
	if _turn_queue.is_empty():
		return true
	return bool(_turn_queue[current_actor_index].get("is_player", false))


func _sort_initiative_queue() -> void:
	# Player entry is index 0 before sort; keep stable ordering for ties after speed tiebreak.
	_turn_queue.sort_custom(_initiative_sort)


func _initiative_sort(a: Dictionary, b: Dictionary) -> bool:
	var ai: int = int(a.get("initiative", 0))
	var bi: int = int(b.get("initiative", 0))
	if ai != bi:
		return ai > bi
	var aspd: int = int(a.get("speed", 0))
	var bspd: int = int(b.get("speed", 0))
	if aspd != bspd:
		return aspd > bspd
	# Absolute tie: Telvar wins priority when initiative and speed match.
	var a_player: bool = bool(a.get("is_player", false))
	var b_player: bool = bool(b.get("is_player", false))
	if a_player != b_player:
		return a_player
	return String(a.get("id", "")) < String(b.get("id", ""))


func _sync_state_from_current_actor() -> void:
	if _turn_queue.is_empty():
		state = CombatState.PLAYER_TURN
		return
	state = (
		CombatState.PLAYER_TURN
		if is_current_actor_player()
		else CombatState.ENEMY_TURN
	)
