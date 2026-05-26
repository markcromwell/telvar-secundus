## GdUnit4 unit tests for BuildingEntrance behaviour (Phase 2485).
## Instantiates Area2D + script + minimal EntranceTooltip child — no scene dependency.
extends "res://addons/gdUnit4/src/GdUnitTestSuite.gd"

const _ENTRANCE_SCRIPT: GDScript = preload("res://scripts/world/building_entrance.gd")


func _ui_accept_pressed() -> InputEventAction:
	var ev := InputEventAction.new()
	ev.action = &"ui_accept"
	ev.pressed = true
	return ev


func _spawn_player() -> CharacterBody2D:
	var player := CharacterBody2D.new()
	player.add_to_group(&"player")
	add_child(auto_free(player))
	return player


func _spawn_entrance() -> Area2D:
	var entrance := Area2D.new()
	var tooltip := CanvasLayer.new()
	tooltip.name = "EntranceTooltip"
	entrance.add_child(tooltip)
	entrance.set_script(_ENTRANCE_SCRIPT)
	entrance.building_name = "Test Shop"
	entrance.entrance_id = "front"
	return entrance


func test_body_entered_sets_player_in_range() -> void:
	var entrance := _spawn_entrance()
	add_child(auto_free(entrance))
	assert_bool(entrance.player_in_range).is_false()
	var player := _spawn_player()
	entrance.body_entered.emit(player)
	assert_bool(entrance.player_in_range).is_true()


func test_body_exited_clears_player_in_range() -> void:
	var entrance := _spawn_entrance()
	add_child(auto_free(entrance))
	var player := _spawn_player()
	entrance.body_entered.emit(player)
	assert_bool(entrance.player_in_range).is_true()
	entrance.body_exited.emit(player)
	assert_bool(entrance.player_in_range).is_false()


func test_e_press_while_in_range_emits_entered() -> void:
	var entrance := _spawn_entrance()
	add_child(entrance)
	monitor_signals(entrance)
	var player := _spawn_player()
	entrance.body_entered.emit(player)
	entrance._unhandled_input(_ui_accept_pressed())
	await assert_signal(entrance).is_emitted("entered", ["Test Shop", "front"])


func test_e_press_while_out_of_range_no_signal() -> void:
	var entrance := _spawn_entrance()
	add_child(entrance)
	monitor_signals(entrance)
	entrance._unhandled_input(_ui_accept_pressed())
	await assert_signal(entrance).wait_until(100).is_not_emitted(
		"entered", [any_string(), any_string()]
	)
