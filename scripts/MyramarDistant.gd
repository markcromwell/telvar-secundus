extends Node2D


func appear() -> void:
	modulate.a = 1.0
	await get_tree().create_timer(3.0).timeout
	var tween := create_tween()
	tween.tween_property(self, "modulate:a", 0.0, 0.4)
	await tween.finished
