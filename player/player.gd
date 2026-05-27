class_name TelvarPlayer
extends CharacterBody2D
## Top-down player: manual input or externally driven scripted velocity.

@export var speed: float = 64.0  # pixels/sec (2 tiles at 32px)
@export var can_move: bool = true
## When false, arrow keys are ignored; scripted movement may still apply.
@export var manual_input_enabled: bool = true

var _scripted_velocity_active: bool = false
var _scripted_velocity: Vector2 = Vector2.ZERO


func set_scripted_velocity(v: Vector2) -> void:
	_scripted_velocity_active = true
	_scripted_velocity = v


func clear_scripted_velocity() -> void:
	_scripted_velocity_active = false
	_scripted_velocity = Vector2.ZERO


func _physics_process(_delta: float) -> void:
	if not can_move:
		velocity = Vector2.ZERO
		move_and_slide()
		return

	if manual_input_enabled:
		var dir := Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")
		velocity = dir * speed
	elif _scripted_velocity_active:
		velocity = _scripted_velocity
	else:
		velocity = Vector2.ZERO

	move_and_slide()
