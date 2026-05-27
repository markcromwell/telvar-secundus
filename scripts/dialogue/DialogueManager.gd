extends Node

signal dialogue_started(npc_id: String, dialogue: Variant)

var _flags: Dictionary = {}


func set_flag(key: String, value: Variant) -> void:
	_flags[key] = value


func get_flag(key: String) -> Variant:
	return _flags.get(key)


func show_dialogue(npc_id: String, dialogue_json: Variant) -> void:
	dialogue_started.emit(npc_id, dialogue_json)
