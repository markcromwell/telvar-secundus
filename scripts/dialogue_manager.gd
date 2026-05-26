extends Node

var _flags: Dictionary = {}

func show_dialogue(npc_id: String, dialogue_json: String) -> void:
	pass

func set_flag(key: String, value: Variant) -> void:
	_flags[key] = value

func get_flag(key: String) -> Variant:
	return _flags.get(key, null)
