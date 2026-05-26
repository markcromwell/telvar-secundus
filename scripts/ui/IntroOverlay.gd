extends CanvasLayer

## Full-screen intro copy + movement hint; tweens opacity then signals completion.
signal intro_finished

@onready var _intro: Label = %IntroLabel
@onready var _hint: Label = %HintLabel


func _ready() -> void:
	layer = 10
	_intro.modulate.a = 0.0
	_hint.modulate.a = 0.0
	_play_sequence()


func _play_sequence() -> void:
	var t := create_tween()
	t.tween_property(_intro, "modulate:a", 1.0, 1.0)
	await t.finished
	await get_tree().create_timer(2.0).timeout
	t = create_tween()
	t.tween_property(_intro, "modulate:a", 0.0, 1.0)
	await t.finished
	t = create_tween()
	t.tween_property(_hint, "modulate:a", 1.0, 0.8)
	await t.finished
	await get_tree().create_timer(2.0).timeout
	t = create_tween()
	t.tween_property(_hint, "modulate:a", 0.0, 1.0)
	await t.finished
	intro_finished.emit()
