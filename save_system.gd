extends Node
## Persists game state to ``user://save_slot_{n}.json`` (JSON).
## Slot 0 is reserved for autosave; slots 1–3 are manual slots.
## Unknown keys from older saves are preserved; new fields come from defaults.

const AUTOSAVE_SLOT: int = 0
const MIN_MANUAL_SLOT: int = 1
const MAX_MANUAL_SLOT: int = 3

const _SAVE_FILE_PATTERN: String = "user://save_slot_%d.json"

var last_save_error: String = ""
var last_load_error: String = ""


func _slot_path(slot: int) -> String:
	return _SAVE_FILE_PATTERN % slot


func is_slot_valid(slot: int) -> bool:
	return slot >= AUTOSAVE_SLOT and slot <= MAX_MANUAL_SLOT


func get_default_save_data() -> Dictionary:
	return {
		"schema_version": 1,
		"player_pos": {"x": 0.0, "y": 0.0},
		"quest_flags": {},
		"lore_unlocked": [],
		"inventory": [],
		"current_scene": "",
		"play_time": 0.0,
		"game_complete": false,
		"dark_robe_unlocked": false,
	}


func merge_with_defaults(partial: Dictionary) -> Dictionary:
	var merged: Dictionary = get_default_save_data()
	for key in partial:
		merged[key] = partial[key]
	return merged


func _validate_payload(payload: Dictionary) -> String:
	if payload.has("play_time"):
		var pt: Variant = payload["play_time"]
		var t: int = typeof(pt)
		if t != TYPE_FLOAT and t != TYPE_INT:
			return "Invalid play_time type."
	if payload.has("game_complete") and typeof(payload["game_complete"]) != TYPE_BOOL:
		return "Invalid game_complete type."
	if payload.has("dark_robe_unlocked") and typeof(payload["dark_robe_unlocked"]) != TYPE_BOOL:
		return "Invalid dark_robe_unlocked type."
	if payload.has("player_pos") and typeof(payload["player_pos"]) != TYPE_DICTIONARY:
		return "Invalid player_pos type."
	if payload.has("quest_flags") and typeof(payload["quest_flags"]) != TYPE_DICTIONARY:
		return "Invalid quest_flags type."
	if payload.has("lore_unlocked") and typeof(payload["lore_unlocked"]) != TYPE_ARRAY:
		return "Invalid lore_unlocked type."
	if payload.has("inventory") and typeof(payload["inventory"]) != TYPE_ARRAY:
		return "Invalid inventory type."
	if payload.has("current_scene") and typeof(payload["current_scene"]) != TYPE_STRING:
		return "Invalid current_scene type."
	return ""


func save_to_slot(slot: int, data: Dictionary) -> bool:
	last_save_error = ""
	if not is_slot_valid(slot):
		last_save_error = "Invalid save slot index."
		push_warning(last_save_error)
		return false
	var merged: Dictionary = merge_with_defaults(data)
	var err: String = _validate_payload(merged)
	if err != "":
		last_save_error = err
		push_warning(last_save_error)
		return false
	var path: String = _slot_path(slot)
	var json_text: String = JSON.stringify(merged, "\t")
	var file = FileAccess.open(path, FileAccess.WRITE)
	if file == null:
		last_save_error = "Could not open save file for writing: %s" % path
		push_warning(last_save_error)
		return false
	file.store_string(json_text)
	file.flush()
	return true


func load_from_slot(slot: int) -> Dictionary:
	last_load_error = ""
	if not is_slot_valid(slot):
		last_load_error = "Invalid save slot index."
		push_warning(last_load_error)
		return get_default_save_data()
	var path: String = _slot_path(slot)
	if not FileAccess.file_exists(path):
		return get_default_save_data()
	var file = FileAccess.open(path, FileAccess.READ)
	if file == null:
		last_load_error = "Could not open save file for reading."
		push_warning(last_load_error)
		return get_default_save_data()
	var text: String = file.get_as_text()
	var parsed: Variant = JSON.parse_string(text)
	if parsed == null:
		last_load_error = "Save file is corrupted or not valid JSON."
		push_warning(last_load_error)
		return get_default_save_data()
	if typeof(parsed) != TYPE_DICTIONARY:
		last_load_error = "Save file root must be a JSON object."
		push_warning(last_load_error)
		return get_default_save_data()
	var as_dict: Dictionary = parsed
	var err: String = _validate_payload(as_dict)
	if err != "":
		last_load_error = err
		push_warning(last_load_error)
		return get_default_save_data()
	return merge_with_defaults(as_dict)
