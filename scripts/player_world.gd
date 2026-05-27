extends CharacterBody2D
## Minimal player for bootstrap world: movement + HP fields for SaveManager restore.


const SPEED := 220.0

var hp: int = 24
var max_hp: int = 24


func _ready() -> void:
	add_to_group(&"game_player")


func _physics_process(_delta: float) -> void:
	var dir := Vector2(
		float(Input.is_action_pressed(&"ui_right") or Input.is_physical_key_pressed(KEY_D))
		- float(Input.is_action_pressed(&"ui_left") or Input.is_physical_key_pressed(KEY_A)),
		float(Input.is_action_pressed(&"ui_down") or Input.is_physical_key_pressed(KEY_S))
		- float(Input.is_action_pressed(&"ui_up") or Input.is_physical_key_pressed(KEY_W))
	)
	if dir.length_squared() > 1.0:
		dir = dir.normalized()
	velocity = dir * SPEED
	move_and_slide()


func set_hp_from_save(new_hp: int, new_max: int) -> void:
	if new_max > 0:
		max_hp = new_max
	hp = clampi(new_hp, 0, max_hp)
