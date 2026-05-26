extends CharacterBody2D

# ~2560 px Merchant↔Temple centers in Overworld.tscn → ~20 s at this speed (spec timing).
@export var speed: float = 128.0  # pixels/sec
@export var can_move: bool = true


func _physics_process(_delta: float) -> void:
	if not can_move:
		return
	var dir := Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")
	velocity = dir * speed
	move_and_slide()
