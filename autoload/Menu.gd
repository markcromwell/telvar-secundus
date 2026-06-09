# autoload/Menu.gd
# 2026-06-08 LIVE-FIX v2: previous version referenced SceneManager which
# is NOT a registered autoload (only Menu, Settings, BuildVersion are).
# The parse error broke the WHOLE autoload, taking MainMenu.gd down with
# it. Replaced the SceneManager.has_method() call with a dynamic
# get_node_or_null() so the symbol is never resolved at parse time.
extends Node

const GAME_WORLD_SCENE   := "res://MainScene.tscn"
const SETTINGS_SCENE     := "res://settings_menu.tscn"
const CREDITS_SCENE      := "res://Credits.tscn"

signal new_game_requested()
signal load_game_requested()
signal settings_requested()
signal credits_requested()


func _change_scene_safe(path: String) -> void:
	if not ResourceLoader.exists(path):
		push_warning("Menu: scene not found: %s" % path)
		return
	get_tree().change_scene_to_file(path)


func request_new_game() -> void:
	emit_signal("new_game_requested")
	_change_scene_safe(GAME_WORLD_SCENE)


func request_load_game() -> void:
	emit_signal("load_game_requested")
	# scene_manager.gd is in autoload/ but NOT registered as an autoload
	# (see project.godot [autoload] section). Fall back to the credits-
	# style hard transition into a load-screen scene if it ever exists,
	# else just route to the game and let in-game save UI handle it.
	var sm = get_node_or_null("/root/SceneManager")
	if sm != null and sm.has_method("open_save_dialog"):
		sm.call("open_save_dialog")
	else:
		_change_scene_safe(GAME_WORLD_SCENE)


func request_settings() -> void:
	emit_signal("settings_requested")
	_change_scene_safe(SETTINGS_SCENE)


func request_credits() -> void:
	emit_signal("credits_requested")
	_change_scene_safe(CREDITS_SCENE)
