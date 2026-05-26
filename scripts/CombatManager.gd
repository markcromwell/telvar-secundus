extends Node

## Autoload: combat encounter state, initiative/HP UI, and CombatUI scene lifecycle.
## HUD nodes (HP bars, turn label, damage floats) are built here so CombatUI.tscn
## stays a thin overlay shell owned by another phase.

const COMBAT_UI_SCENE := preload("res://scenes/CombatUI.tscn")

enum CombatState {
	PLAYER_TURN,
	ENEMY_TURN,
}

const SPELL_MANA_COST := 5

var _rng := RandomNumberGenerator.new()

var _combat_ui: CanvasLayer
var _hud_root: Control
var _turn_label: Label
var _hp_bars: Array[ProgressBar] = []
var _name_labels: Array[Label] = []
var _hp_value_labels: Array[Label] = []

var _combatants: Array[Dictionary] = []
var _order: Array[int] = []
var _turn_idx: int = 0
var _state: CombatState = CombatState.PLAYER_TURN


func _ready() -> void:
	_rng.randomize()


func start_combat(player: Variant = null, enemies: Variant = null) -> void:
	if _combat_ui != null and is_instance_valid(_combat_ui):
		return
	_setup_encounter(player, enemies)
	_combat_ui = COMBAT_UI_SCENE.instantiate() as CanvasLayer
	get_tree().root.add_child(_combat_ui)
	if _combat_ui.has_method("show_combat"):
		_combat_ui.show_combat()
	_roll_initiative()
	_build_managed_hud()
	_sync_turn_pointer_to_first_living()
	_refresh_ui()
	_process_enemy_chain()


func end_combat(_victory: bool) -> void:
	_tear_down_encounter_state()
	if _combat_ui == null or not is_instance_valid(_combat_ui):
		_combat_ui = null
		return
	var ui := _combat_ui
	_combat_ui = null
	if ui.has_method("remove_combat_ui"):
		ui.remove_combat_ui()
	else:
		ui.queue_free()


func is_combat_active() -> bool:
	return _combat_ui != null and is_instance_valid(_combat_ui)


func get_combat_state() -> CombatState:
	return _state


## Physical attack from the current actor if it is the player. Returns damage dealt (0 if invalid).
func player_attack(defender_index: int = -1) -> int:
	if not is_combat_active() or _state != CombatState.PLAYER_TURN:
		return 0
	var atk_i: int = _order[_turn_idx]
	if not bool(_combatants[atk_i].get("is_player", false)):
		return 0
	var def_i: int = _resolve_defender_index(defender_index)
	if def_i < 0:
		return 0
	var dmg: int = _roll_physical_damage(_combatants[atk_i], _combatants[def_i])
	_apply_damage(def_i, dmg)
	_spawn_damage_float(dmg, def_i)
	_after_player_action()
	return dmg


## Spell attack using mana from the player. Returns damage dealt (0 if not player turn or OOM).
func player_cast_spell(defender_index: int = -1) -> int:
	if not is_combat_active() or _state != CombatState.PLAYER_TURN:
		return 0
	var atk_i: int = _order[_turn_idx]
	if not bool(_combatants[atk_i].get("is_player", false)):
		return 0
	var def_i: int = _resolve_defender_index(defender_index)
	if def_i < 0:
		return 0
	var pi: int = _get_player_index()
	var mana: int = int(_combatants[pi].get("mana", 0))
	if mana < SPELL_MANA_COST:
		return 0
	_combatants[pi]["mana"] = mana - SPELL_MANA_COST
	var dmg: int = _roll_spell_damage(_combatants[atk_i], _combatants[def_i])
	_apply_damage(def_i, dmg)
	_spawn_damage_float(dmg, def_i)
	_after_player_action()
	return dmg


## 70% success ends combat as a non-victory escape. Failed flee consumes the turn.
func player_flee() -> bool:
	if not is_combat_active() or _state != CombatState.PLAYER_TURN:
		return false
	if _rng.randf() < 0.7:
		end_combat(false)
		return true
	_after_player_action()
	return false


func _setup_encounter(player: Variant, enemies: Variant) -> void:
	_combatants.clear()
	_order.clear()
	_turn_idx = 0
	var p: Dictionary = player if typeof(player) == TYPE_DICTIONARY else _default_player()
	var enemy_list: Array = enemies if typeof(enemies) == TYPE_ARRAY else [_default_enemy()]
	_combatants.append(p.duplicate(true))
	for e in enemy_list:
		if typeof(e) == TYPE_DICTIONARY:
			_combatants.append((e as Dictionary).duplicate(true))


func _tear_down_encounter_state() -> void:
	_combatants.clear()
	_order.clear()
	_turn_idx = 0
	_hp_bars.clear()
	_name_labels.clear()
	_hp_value_labels.clear()
	_hud_root = null
	_turn_label = null


func _default_player() -> Dictionary:
	return {
		"name": "Telvar",
		"speed": 5,
		"attack": 8,
		"defense": 2,
		"max_hp": 30,
		"hp": 30,
		"max_mana": 20,
		"mana": 20,
		"is_player": true,
	}


func _default_enemy() -> Dictionary:
	return {
		"name": "Street Thug",
		"speed": 4,
		"attack": 6,
		"defense": 1,
		"max_hp": 22,
		"hp": 22,
		"max_mana": 0,
		"mana": 0,
		"is_player": false,
	}


func _roll_initiative() -> void:
	var order: Array[int] = []
	for i in _combatants.size():
		var c: Dictionary = _combatants[i]
		var spd: int = int(c.get("speed", 1))
		c["initiative"] = spd + _rng.randi_range(1, 6)
		order.append(i)
	order.sort_custom(func(a: int, b: int) -> bool:
		return int(_combatants[a]["initiative"]) > int(_combatants[b]["initiative"])
	)
	_order = order


func _sync_turn_pointer_to_first_living() -> void:
	if _order.is_empty():
		return
	for i in _order.size():
		var ci: int = _order[i]
		if int(_combatants[ci].get("hp", 0)) > 0:
			_turn_idx = i
			return


func _get_player_index() -> int:
	for i in _combatants.size():
		if bool(_combatants[i].get("is_player", false)):
			return i
	return 0


func _resolve_defender_index(defender_index: int) -> int:
	if defender_index >= 0 and defender_index < _combatants.size():
		var cand: Dictionary = _combatants[defender_index]
		if not bool(cand.get("is_player", false)) and int(cand.get("hp", 0)) > 0:
			return defender_index
	for i in _combatants.size():
		var c: Dictionary = _combatants[i]
		if not bool(c.get("is_player", false)) and int(c.get("hp", 0)) > 0:
			return i
	return -1


func _roll_physical_damage(attacker: Dictionary, defender: Dictionary) -> int:
	var atk: int = int(attacker.get("attack", 1))
	var dfs: int = int(defender.get("defense", 0))
	var roll: int = _rng.randi_range(-2, 2)
	return maxi(1, atk - dfs + roll)


func _roll_spell_damage(attacker: Dictionary, defender: Dictionary) -> int:
	var atk: int = int(attacker.get("attack", 1))
	var dfs: int = int(defender.get("defense", 0))
	var roll: int = _rng.randi_range(-2, 2)
	return maxi(1, atk - dfs + roll + 2)


func _apply_damage(combatant_index: int, amount: int) -> void:
	var c: Dictionary = _combatants[combatant_index]
	var hp: int = int(c.get("hp", 0))
	c["hp"] = maxi(0, hp - amount)
	_refresh_ui()


func _build_managed_hud() -> void:
	_hud_root = Control.new()
	_hud_root.name = "ManagedCombatHUD"
	_hud_root.set_anchors_preset(Control.PRESET_FULL_RECT)
	_hud_root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_combat_ui.add_child(_hud_root)

	var margin := MarginContainer.new()
	margin.set_anchors_preset(Control.PRESET_FULL_RECT)
	margin.add_theme_constant_override("margin_left", 16)
	margin.add_theme_constant_override("margin_top", 12)
	margin.add_theme_constant_override("margin_right", 16)
	margin.add_theme_constant_override("margin_bottom", 12)
	_hud_root.add_child(margin)

	var root_vb := VBoxContainer.new()
	root_vb.size_flags_vertical = Control.SIZE_EXPAND_FILL
	margin.add_child(root_vb)

	_turn_label = Label.new()
	_turn_label.add_theme_font_size_override("font_size", 22)
	root_vb.add_child(_turn_label)

	root_vb.add_child(HSeparator.new())

	var stats_header := Label.new()
	stats_header.text = "Combatants"
	stats_header.add_theme_font_size_override("font_size", 16)
	root_vb.add_child(stats_header)

	_hp_bars.clear()
	_name_labels.clear()
	_hp_value_labels.clear()
	for i in _combatants.size():
		var row := HBoxContainer.new()
		root_vb.add_child(row)
		var nl := Label.new()
		nl.custom_minimum_size = Vector2(200, 0)
		nl.clip_text = true
		row.add_child(nl)
		_name_labels.append(nl)
		var bar := ProgressBar.new()
		bar.custom_minimum_size = Vector2(240, 24)
		bar.show_percentage = false
		bar.max_value = 100
		bar.value = 100
		row.add_child(bar)
		_hp_bars.append(bar)
		var hv := Label.new()
		hv.add_theme_font_size_override("font_size", 14)
		row.add_child(hv)
		_hp_value_labels.append(hv)


func _refresh_ui() -> void:
	if _combat_ui == null or not is_instance_valid(_combat_ui) or _hud_root == null:
		return
	for i in _hp_bars.size():
		if i >= _combatants.size():
			break
		var c: Dictionary = _combatants[i]
		var mx: int = maxi(1, int(c.get("max_hp", 1)))
		var hp: int = clampi(int(c.get("hp", 0)), 0, mx)
		_hp_bars[i].max_value = mx
		_hp_bars[i].value = hp
		if i < _name_labels.size():
			var init_roll: int = int(c.get("initiative", -1))
			_name_labels[i].text = "%s (init %d)" % [str(c.get("name", "?")), init_roll]
		if i < _hp_value_labels.size():
			_hp_value_labels[i].text = "%d / %d" % [hp, mx]
	if _order.is_empty() or _turn_label == null:
		return
	var cur_i: int = _order[_turn_idx]
	var actor: Dictionary = _combatants[cur_i]
	var aname: String = str(actor.get("name", "?"))
	_turn_label.text = "Turn: %s" % aname
	_state = CombatState.PLAYER_TURN if bool(actor.get("is_player", false)) else CombatState.ENEMY_TURN


func _spawn_damage_float(amount: int, defender_index: int) -> void:
	if _hud_root == null or not is_instance_valid(_hud_root):
		return
	var flo := Label.new()
	flo.text = "-%d" % amount
	flo.add_theme_font_size_override("font_size", 26)
	flo.modulate = Color(1.0, 0.35, 0.35, 1.0)
	var x_base: float = 400.0 + float(defender_index) * 40.0
	var y_base: float = 200.0
	flo.position = Vector2(x_base, y_base)
	flo.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_hud_root.add_child(flo)
	var tw := create_tween()
	tw.set_parallel(true)
	tw.tween_property(flo, "position:y", y_base - 72.0, 0.55).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	tw.tween_property(flo, "modulate:a", 0.0, 0.55)
	tw.chain().tween_callback(flo.queue_free)


func _check_end_conditions() -> void:
	var player_alive := false
	var any_enemy_alive := false
	for c in _combatants:
		var alive: bool = int(c.get("hp", 0)) > 0
		if bool(c.get("is_player", false)):
			player_alive = player_alive or alive
		else:
			any_enemy_alive = any_enemy_alive or alive
	if not player_alive:
		end_combat(false)
	elif not any_enemy_alive:
		end_combat(true)


func _advance_turn() -> void:
	if _order.is_empty():
		return
	var start_idx: int = _turn_idx
	while true:
		_turn_idx = (_turn_idx + 1) % _order.size()
		var ci: int = _order[_turn_idx]
		if int(_combatants[ci].get("hp", 0)) > 0:
			break
		if _turn_idx == start_idx:
			break


func _after_player_action() -> void:
	_check_end_conditions()
	if not is_combat_active():
		return
	_advance_turn()
	_refresh_ui()
	_process_enemy_chain()


func _process_enemy_chain() -> void:
	if not is_combat_active() or _order.is_empty():
		return
	while true:
		var ci: int = _order[_turn_idx]
		var actor: Dictionary = _combatants[ci]
		if int(actor.get("hp", 0)) <= 0:
			_advance_turn()
			_refresh_ui()
			continue
		if bool(actor.get("is_player", false)):
			break
		var pi: int = _get_player_index()
		var dmg: int = _roll_physical_damage(actor, _combatants[pi])
		_apply_damage(pi, dmg)
		_spawn_damage_float(dmg, pi)
		_check_end_conditions()
		if not is_combat_active():
			return
		_advance_turn()
		_refresh_ui()
