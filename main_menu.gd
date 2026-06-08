extends Control


@onready var _main_panel: Control = $MainPanel
@onready var _settings_host: Control = $SettingsHost
@onready var _settings_menu: Control = $SettingsHost/SettingsMenu


func _ready() -> void:
	_settings_host.visible = false
	_settings_menu.back_pressed.connect(_on_back_from_settings_pressed)


func _on_settings_pressed() -> void:
	_main_panel.visible = false
	_settings_host.visible = true


func _on_back_from_settings_pressed() -> void:
	_settings_host.visible = false
	_main_panel.visible = true


func _on_play_pressed() -> void:
	get_tree().change_scene_to_file("res://game_world.tscn")


func _on_quit_pressed() -> void:
	get_tree().quit()
