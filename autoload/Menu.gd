# autoload/Menu.gd
extends Node

signal new_game_requested()
signal load_game_requested()
signal settings_requested()
signal credits_requested()

func request_new_game():
	emit_signal("new_game_requested")

func request_load_game():
	emit_signal("load_game_requested")

func request_settings():
	emit_signal("settings_requested")

func request_credits():
	emit_signal("credits_requested")
