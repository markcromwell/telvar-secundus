extends CharacterBody2D

## Simple hall exploration: WASD move, E presents admission letter at the reception desk.

const SPEED := 115.0


func _physics_process(_delta: float) -> void:
	var dir := Vector2(
		float(Input.is_physical_key_pressed(KEY_D)) - float(Input.is_physical_key_pressed(KEY_A)),
		float(Input.is_physical_key_pressed(KEY_S)) - float(Input.is_physical_key_pressed(KEY_W))
	)
	if dir.length_squared() > 1.0:
		dir = dir.normalized()
	velocity = dir * SPEED
	move_and_slide()


func _unhandled_input(event: InputEvent) -> void:
	if not (event is InputEventKey and event.pressed and not event.echo):
		return
	if event.physical_keycode != KEY_E:
		return
	var hall := get_parent()
	if hall and hall.has_method("try_present_admission_letter"):
		hall.call("try_present_admission_letter", self)
