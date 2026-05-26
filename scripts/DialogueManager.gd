extends Node

var _flags: Dictionary = {}
var current_npc_id: String = ""
var current_dialogue_json: String = ""
var is_dialogue_active: bool = false

func show_dialogue(npc_id: String, json_path: String) -> void:
	current_npc_id = npc_id
	current_dialogue_json = json_path
	is_dialogue_active = true

func set_flag(key: String, val: Variant) -> void:
	_flags[key] = val

func get_flag(key: String) -> Variant:
	return _flags.get(key, null)
