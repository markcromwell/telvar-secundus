extends CharacterBody2D

@export var speed: float = 64.0  # pixels/sec (2 tiles at 32px)
@export var can_move: bool = true

## Current mana; never below 0 or above max_mana.
var mana: float = 50.0
## Maximum mana capacity.
var max_mana: float = 50.0

const MANA_REGEN_PER_SEC: float = 1.0


func _ready() -> void:
	mana = max_mana
	_clamp_mana()


func _physics_process(delta: float) -> void:
	if can_move:
		var dir := Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")
		velocity = dir * speed
		move_and_slide()
	_regenerate_mana(delta)


func _regenerate_mana(delta: float) -> void:
	mana += MANA_REGEN_PER_SEC * delta
	_clamp_mana()


func _clamp_mana() -> void:
	mana = clampf(mana, 0.0, max_mana)
