extends CharacterBody2D

@export var npc_name: String = ""
@export var dialogue: PackedStringArray = []

var _dialogue_index: int = 0

signal dialogue_line_shown(line: String, speaker: String)


func show_dialogue() -> void:
	if dialogue.is_empty():
		return
	var line: String = dialogue[_dialogue_index]
	_dialogue_index = (_dialogue_index + 1) % dialogue.size()
	dialogue_line_shown.emit(line, npc_name)
