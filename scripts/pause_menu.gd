extends CanvasLayer
## Pause overlay with Save entry wired to SceneManager.

@onready var _panel: Control = $Panel


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	_hide()
	$Panel/VBox/Resume.pressed.connect(_on_resume_pressed)
	$Panel/VBox/Save.pressed.connect(_on_save_pressed)


func _unhandled_input(event: InputEvent) -> void:
	if SceneManager.is_save_dialog_open():
		return
	if event.is_action_pressed("ui_cancel"):
		get_viewport().set_input_as_handled()
		if _panel.visible:
			_hide()
		else:
			_show()


func _on_save_pressed() -> void:
	SceneManager.open_save_dialog()


func _on_resume_pressed() -> void:
	_hide()


func _show() -> void:
	_panel.visible = true
	get_tree().paused = true


func _hide() -> void:
	_panel.visible = false
	get_tree().paused = false
