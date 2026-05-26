extends Node


@onready var _spell_panel: Node = $CanvasLayer/CastSpellPanel
@onready var _victory_label: Label = $VictoryCanvas/Center/VictoryLabel
@onready var _victory_sfx: AudioStreamPlayer = $VictoryCanvas/VictorySFX
@onready var _victory_timer: Timer = $VictoryCanvas/VictoryTimer
@onready var _defeat_fade: ColorRect = $DefeatCanvas/DefeatFadeRect


func _ready() -> void:
	add_to_group(&"thug_victory_fanfare")
	add_to_group(&"defeat_respawn_handler")
	_victory_timer.timeout.connect(_on_victory_timer_timeout)
	SpellBook.record_last_save_point(Vector2.ZERO, get_scene_file_path())
	if SpellBook.consume_post_defeat_fade_from_black():
		_defeat_fade.modulate.a = 1.0
		var out_tw := create_tween()
		out_tw.tween_property(_defeat_fade, "modulate:a", 0.0, 0.65)


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_just_pressed(&"toggle_cast_spell"):
		_spell_panel.toggle_visible()
		get_viewport().set_input_as_handled()


## Called when combat ends in a win vs a Thug: fanfare, loot, UI. Other systems
## can invoke this via ``get_tree().call_group("thug_victory_fanfare", "play_thug_victory_fanfare")``.
func play_thug_victory_fanfare() -> void:
	var gained: int = SpellCombat.roll_thug_victory_copper()
	SpellBook.grant_copper(gained)
	_victory_label.text = "Victory!\nThug defeated.\n+%d copper" % gained
	_victory_label.visible = true
	if _victory_sfx.stream != null:
		_victory_sfx.play()
	_victory_timer.start()


func _on_victory_timer_timeout() -> void:
	_victory_label.visible = false


## Fade to black, restore HP to 15, then load the last save scene (same scene reloads here).
## Combat or other systems: ``get_tree().call_group("defeat_respawn_handler", "play_defeat_fade_and_respawn")``.
func play_defeat_fade_and_respawn() -> void:
	var tw := create_tween()
	tw.tween_property(_defeat_fade, "modulate:a", 1.0, 0.75)
	tw.tween_callback(_finish_defeat_respawn)


func _finish_defeat_respawn() -> void:
	SpellBook.apply_defeat_respawn_state()
	var target := SpellBook.last_save_scene_path
	if target.is_empty():
		target = get_scene_file_path()
	if target == get_scene_file_path():
		get_tree().call_deferred(&"reload_current_scene")
	else:
		get_tree().call_deferred(&"change_scene_to_file", target)
