extends CharacterBody2D

@export var speed: float = 64.0  # pixels/sec (2 tiles at 32px)
@export var can_move: bool = true


func _physics_process(delta: float) -> void:
	if not can_move:
		return
	var dir := Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")
	velocity = dir * speed
	move_and_slide()


## Toggle the ceremony wrist band overlay (scales with this body via scene tree).
func set_wrist_band_visible(show: bool) -> void:
	var band := get_node_or_null("WristBand") as Sprite2D
	if band != null:
		band.visible = show
