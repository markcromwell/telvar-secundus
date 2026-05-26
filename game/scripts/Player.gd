extends CharacterBody2D

@export var speed: float = 128.0
@export var can_move: bool = true


func _physics_process(_delta: float) -> void:
	if can_move:
		var direction := Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")
		velocity = direction * speed
	else:
		velocity = Vector2.ZERO

	move_and_slide()
