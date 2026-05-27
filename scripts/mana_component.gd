extends Node
class_name ManaComponent

## Tracks spell mana, emits `mana_changed`, and regenerates:
## - In combat: +1 when `regen_mana_combat_turn()` is called once per combat turn.
## - Out of combat: +1 every `out_of_combat_regen_interval` seconds (default 5).

signal mana_changed(current: int, maximum: int)

@export var max_mana: int = 20
@export var out_of_combat_regen_interval: float = 5.0

var current_mana: int = 0

var _combat_active: bool = false
var _regen_timer: Timer


func _ready() -> void:
	current_mana = max_mana

	_regen_timer = Timer.new()
	_regen_timer.one_shot = false
	_regen_timer.wait_time = out_of_combat_regen_interval
	_regen_timer.timeout.connect(_on_out_of_combat_regen_tick)
	add_child(_regen_timer)

	_refresh_regen_driver()
	mana_changed.emit(current_mana, max_mana)


func get_current_mana() -> int:
	return current_mana


func get_max_mana() -> int:
	return max_mana


func set_combat_active(active: bool) -> void:
	if _combat_active == active:
		return
	_combat_active = active
	_refresh_regen_driver()


func regen_mana_combat_turn() -> void:
	if not _combat_active:
		return
	_restore_mana(1)


func use_mana(cost: int) -> bool:
	if cost <= 0:
		return true
	if current_mana < cost:
		return false
	current_mana -= cost
	mana_changed.emit(current_mana, max_mana)
	return true


func _on_out_of_combat_regen_tick() -> void:
	if _combat_active:
		return
	_restore_mana(1)


func _restore_mana(amount: int) -> void:
	if amount <= 0:
		return
	if current_mana >= max_mana:
		return
	current_mana = mini(max_mana, current_mana + amount)
	mana_changed.emit(current_mana, max_mana)


func _refresh_regen_driver() -> void:
	if _regen_timer == null:
		return
	if _combat_active:
		_regen_timer.stop()
	else:
		_regen_timer.wait_time = out_of_combat_regen_interval
		_regen_timer.start()
