extends Node
class_name ManaComponent

signal mana_changed(current: int, maximum: int)

@export var max_mana: int = 20
@export var current_mana: int = 20
## Mana restored each regen tick while out of combat.
@export var regen_rate: int = 1

## When true, passive mana regen is paused (e.g. during combat turns).
var in_combat: bool = false

var _regen_accum: float = 0.0
const REGEN_PERIOD_SEC: float = 5.0


func _ready() -> void:
	current_mana = clampi(current_mana, 0, max_mana)
	mana_changed.emit(current_mana, max_mana)


func _process(delta: float) -> void:
	if in_combat:
		return
	if current_mana >= max_mana:
		return
	_regen_accum += delta
	while _regen_accum >= REGEN_PERIOD_SEC:
		_regen_accum -= REGEN_PERIOD_SEC
		if current_mana >= max_mana:
			break
		current_mana = mini(current_mana + regen_rate, max_mana)
		mana_changed.emit(current_mana, max_mana)


func use_mana(cost: int) -> bool:
	if cost <= 0:
		return true
	if current_mana >= cost:
		current_mana -= cost
		mana_changed.emit(current_mana, max_mana)
		return true
	return false


func set_combat_state(active: bool) -> void:
	in_combat = active
