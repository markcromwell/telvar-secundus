extends Node2D
## Resolves combat actions (Attack, Cast Spell, Flee) and enemy turns without
## modifying CombatManager / CombatUI scripts (owned by adjacent spec phases).

const SPELL_MANA_COST := 5
const FLEE_SUCCESS_CHANCE := 0.7

@export var player_max_hp: int = 100
@export var player_attack: int = 8
@export var player_defense: int = 2
@export var player_max_mana: int = 30

@export var enemy_max_hp: int = 40
@export var enemy_attack: int = 5
@export var enemy_defense: int = 1

@onready var _combat_ui: Node = $CombatUI
@onready var _encounter: Node = $EncounterZone

var _player_hp: int = 100
var _player_mana: int = 30
## enemy_id -> current hp
var _enemy_hp: Dictionary = {}


func _ready() -> void:
	_combat_ui.action_chosen.connect(_on_action_chosen)
	CombatManager.combat_started.connect(_on_combat_started)
	CombatManager.combat_ended.connect(_on_combat_ended)
	CombatManager.turn_advanced.connect(_on_turn_advanced)


static func roll_action_damage(attacker_attack: int, defender_defense: int) -> int:
	# Spec: max(1, attack - defense + rand(-2, 2))
	return maxi(1, attacker_attack - defender_defense + randi_range(-2, 2))


func _on_combat_started() -> void:
	_player_hp = player_max_hp
	_player_mana = player_max_mana
	_enemy_hp.clear()
	var n := maxi(1, int(_encounter.get("enemy_count")))
	for i in n:
		_enemy_hp["enemy_%d" % i] = enemy_max_hp
	_refresh_hp_bars()
	_update_menu_mouse_filter()
	call_deferred("_resolve_enemy_turn_if_needed")


func _on_combat_ended() -> void:
	_enemy_hp.clear()
	_update_menu_mouse_filter()


func _on_turn_advanced(_round_index: int, _actor_index: int, _state: CombatManager.CombatState) -> void:
	_update_menu_mouse_filter()
	call_deferred("_resolve_enemy_turn_if_needed")


func _update_menu_mouse_filter() -> void:
	var root := _combat_ui.get_node_or_null("ControlRoot")
	if root == null or not root is Control:
		return
	var cr := root as Control
	if not CombatManager.in_combat:
		cr.mouse_filter = Control.MOUSE_FILTER_STOP
		return
	cr.mouse_filter = (
		Control.MOUSE_FILTER_STOP
		if CombatManager.is_current_actor_player()
		else Control.MOUSE_FILTER_IGNORE
	)


func _refresh_hp_bars() -> void:
	_combat_ui.set_player_hp(_player_hp, player_max_hp)
	var emax := enemy_max_hp * maxi(_enemy_hp.size(), 1)
	var esum := 0
	for _k in _enemy_hp.keys():
		esum += int(_enemy_hp[_k])
	_combat_ui.set_enemy_hp(esum, emax)


func _pick_live_enemy_id() -> String:
	var n := maxi(1, int(_encounter.get("enemy_count")))
	for i in n:
		var eid := "enemy_%d" % i
		if int(_enemy_hp.get(eid, 0)) > 0:
			return eid
	return ""


func _all_enemies_defeated() -> bool:
	for k in _enemy_hp.keys():
		if int(_enemy_hp[k]) > 0:
			return false
	return not _enemy_hp.is_empty()


func _on_action_chosen(action: String) -> void:
	if not CombatManager.in_combat:
		return
	if not CombatManager.is_current_actor_player():
		return
	match action:
		"attack":
			_do_player_attack()
		"cast_spell":
			_do_player_cast()
		"flee":
			_do_player_flee()
		_:
			push_warning("WorldDemoController: unknown action %s" % action)


func _do_player_attack() -> void:
	var tid := _pick_live_enemy_id()
	if tid == "":
		return
	var dmg := roll_action_damage(player_attack, enemy_defense)
	_enemy_hp[tid] = maxi(int(_enemy_hp[tid]) - dmg, 0)
	_refresh_hp_bars()
	if _all_enemies_defeated():
		CombatManager.end_combat()
		return
	CombatManager.advance_turn()


func _do_player_cast() -> void:
	if _player_mana < SPELL_MANA_COST:
		push_warning("WorldDemoController: not enough mana to cast.")
		return
	var tid := _pick_live_enemy_id()
	if tid == "":
		return
	_player_mana -= SPELL_MANA_COST
	var dmg := roll_action_damage(player_attack, enemy_defense)
	_enemy_hp[tid] = maxi(int(_enemy_hp[tid]) - dmg, 0)
	_refresh_hp_bars()
	if _all_enemies_defeated():
		CombatManager.end_combat()
		return
	CombatManager.advance_turn()


func _do_player_flee() -> void:
	if randf() < FLEE_SUCCESS_CHANCE:
		CombatManager.end_combat()
	else:
		CombatManager.advance_turn()


func _resolve_enemy_turn_if_needed() -> void:
	if not CombatManager.in_combat:
		return
	while CombatManager.in_combat and not CombatManager.is_current_actor_player():
		var eid := CombatManager.get_current_actor_id()
		if eid == "":
			return
		if int(_enemy_hp.get(eid, 0)) <= 0:
			CombatManager.advance_turn()
			continue
		var dmg := roll_action_damage(enemy_attack, player_defense)
		_player_hp = maxi(_player_hp - dmg, 0)
		_refresh_hp_bars()
		if _player_hp <= 0:
			CombatManager.end_combat()
			return
		CombatManager.advance_turn()
		return
