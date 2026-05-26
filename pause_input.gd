extends Node
## Always processes so ESC opens the pause UI even when the game tree is not paused.

@onready var _pause_layer: CanvasLayer = $"../PauseLayer"


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS


func _unhandled_input(event: InputEvent) -> void:
	if not event.is_action_pressed("ui_cancel"):
		return
	if _pause_layer.is_settings_open():
		_pause_layer.close_settings()
	elif _pause_layer.visible:
		_pause_layer.resume()
	else:
		_pause_layer.open_pause()
	get_viewport().set_input_as_handled()
