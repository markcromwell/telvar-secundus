extends CharacterBody2D
## Minimal exploration movement so the player can reach encounter zones.

const SPEED := 220.0


func _physics_process(_delta: float) -> void:
	var dir := Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")
	velocity = dir * SPEED
	move_and_slide()
