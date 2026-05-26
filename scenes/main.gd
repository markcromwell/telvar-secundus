extends Node


@onready var _spell_panel: Node = $CanvasLayer/CastSpellPanel
@onready var _victory_label: Label = $VictoryCanvas/Center/VictoryLabel
@onready var _victory_sfx: AudioStreamPlayer = $VictoryCanvas/VictorySFX
@onready var _victory_timer: Timer = $VictoryCanvas/VictoryTimer


func _ready() -> void:
	add_to_group(&"thug_victory_fanfare")
	_victory_timer.timeout.connect(_on_victory_timer_timeout)


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
