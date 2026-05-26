extends Control

## One-shot floating damage number: plays `float_up` then frees itself.

@onready var _label: Label = $DamageLabel
@onready var _anim: AnimationPlayer = $AnimationPlayer


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	_anim.animation_finished.connect(_on_float_finished, CONNECT_ONE_SHOT)


func play_damage(amount: int) -> void:
	_label.text = "-%d" % amount
	_anim.play("float_up")


func _on_float_finished(_anim_name: StringName) -> void:
	queue_free()
