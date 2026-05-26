extends CanvasLayer

signal intro_finished

@onready var _label: Label = %IntroLabel


func play_intro() -> void:
	_label.text = "Secundus. The greatest city in Medias..."
	_label.modulate = Color(1, 1, 1, 1)
	var tw := create_tween()
	tw.tween_interval(1.5)
	tw.tween_property(_label, "modulate:a", 0.0, 2.0)
	tw.tween_callback(func() -> void:
		intro_finished.emit()
		queue_free()
	)
