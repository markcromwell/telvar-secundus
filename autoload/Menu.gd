# autoload/Menu.gd
# 2026-06-08 LIVE-FIX: previous version emitted *_requested signals but
# nothing in the codebase listened for them, so every MainMenu button
# click was silently a no-op. The MVP-7 polish phase (#1540) wired the
# button signals -> request_* functions but the decomposer never gave
# any phase responsibility for actually handling those requests.
# This file now performs the scene transitions itself so the menu is
# usable end-to-end. Signals are still emitted in case other systems
# want to react.
extends Node

const GAME_WORLD_SCENE := "res://game_world.tscn"
const SETTINGS_SCENE   := "res://settings_menu.tscn"
const CREDITS_SCENE    := "res://Credits.tscn"
const LOAD_DIALOG_SCENE := "res://ui/save_dialog.tscn"

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
	# Defer to scene_manager's existing save/load dialog (F5 also opens it).
	# If save_dialog supports a "load" mode it will branch on its own.
	if has_node("/root/SceneManager") and SceneManager.has_method("open_save_dialog"):
		SceneManager.open_save_dialog()
	else:
		_change_scene_safe(LOAD_DIALOG_SCENE)


func request_settings() -> void:
	emit_signal("settings_requested")
	_change_scene_safe(SETTINGS_SCENE)


func request_credits() -> void:
	emit_signal("credits_requested")
	_change_scene_safe(CREDITS_SCENE)
