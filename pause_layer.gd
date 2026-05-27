extends CanvasLayer


@onready var _pause_panel: Control = $PausePanel
@onready var _settings_host: Control = $SettingsHost


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	hide()
	_settings_host.visible = false


func open_pause() -> void:
	show()
	_pause_panel.visible = true
	_settings_host.visible = false
	get_tree().paused = true


func resume() -> void:
	hide()
	get_tree().paused = false


func close_settings() -> void:
	_settings_host.visible = false
	_pause_panel.visible = true


func is_settings_open() -> bool:
	return _settings_host.visible


func _on_resume_pressed() -> void:
	resume()


func _on_settings_pressed() -> void:
	_pause_panel.visible = false
	_settings_host.visible = true


func _on_main_menu_pressed() -> void:
	get_tree().paused = false
	hide()
	get_tree().change_scene_to_file("res://main_menu.tscn")


func _on_back_from_settings_pressed() -> void:
	close_settings()
