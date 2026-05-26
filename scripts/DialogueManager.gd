extends Node
## Autoload: loads `res://assets/dialogue/*.json`, parses branching nodes and
## bracket flags, and exposes dialogue + flag APIs for NPCs and UI.

signal dialogue_requested(npc_id: String, nodes: Dictionary, entry_id: String)

var _dialogues: Dictionary = {}  # npc_id -> { node_id -> node Dictionary }
var _dialogue_entry_id: Dictionary = {}  # npc_id -> first node id in file order
var _flags: Dictionary = {}

var _flag_regex: RegEx

func _init() -> void:
	_flag_regex = RegEx.new()
	var err := _flag_regex.compile("\\[([a-zA-Z0-9_]+)\\]")
	if err != OK:
		push_error("DialogueManager: failed to compile flag RegEx")


func _ready() -> void:
	_load_dialogue_files("res://assets/dialogue/")


func _load_dialogue_files(dir_path: String) -> void:
	var dir := DirAccess.open(dir_path)
	if dir == null:
		Log.warn("Dialogue directory missing or inaccessible: %s" % dir_path)
		return

	for file_name in dir.get_files():
		if not file_name.ends_with(".json"):
			continue

		var npc_id := file_name.get_basename()
		var file_path := dir_path.trim_suffix("/").path_join(file_name)

		if not FileAccess.file_exists(file_path):
			Log.warn("Dialogue file listed but missing on disk: %s" % file_path)
			continue

		var text := FileAccess.get_file_as_string(file_path)
		if text.is_empty():
			Log.warn("Dialogue file empty or unreadable: %s" % file_path)
			continue

		var json := JSON.new()
		var parse_err := json.parse(text)
		if parse_err != OK:
			Log.warn(
				"Invalid dialogue JSON in %s (JSON error %s at line %s)"
				% [file_path, json.get_error_message(), json.get_error_line()]
			)
			continue

		var data: Variant = json.get_data()
		if typeof(data) != TYPE_ARRAY:
			Log.warn("Dialogue root must be an array in %s" % file_path)
			continue

		var parsed: Dictionary = _parse_dialogue_array(data as Array)
		var graph: Dictionary = parsed.get("graph", {}) as Dictionary
		var entry: String = str(parsed.get("entry", ""))
		if graph.is_empty():
			Log.warn("No valid dialogue nodes in %s" % file_path)
			continue

		_dialogues[npc_id] = graph
		_dialogue_entry_id[npc_id] = entry


func _parse_dialogue_array(source: Array) -> Dictionary:
	var graph: Dictionary = {}
	var entry_id := ""

	for item in source:
		if not item is Dictionary:
			Log.warn("Dialogue entry is not an object; skipping.")
			continue

		var node_dict: Dictionary = (item as Dictionary).duplicate(true)
		var id: String = str(node_dict.get("id", ""))
		if id.is_empty():
			Log.warn("Dialogue entry missing id; skipping.")
			continue

		if entry_id.is_empty():
			entry_id = id

		var body: String = str(node_dict.get("text", ""))
		var flags: Array = _extract_flags(body)
		node_dict["flags"] = flags
		graph[id] = node_dict

	return {"graph": graph, "entry": entry_id}


func _extract_flags(text: String) -> Array:
	var out: Array = []
	var pos := 0
	while true:
		var m := _flag_regex.search(text, pos)
		if m == null:
			break
		out.append(m.get_string(1))
		pos = m.get_end()

	return out


func show_dialogue(npc_id: String, dialogue_json: Array = []) -> void:
	var graph: Dictionary = {}
	var entry_id := ""

	if dialogue_json.is_empty():
		graph = _dialogues.get(npc_id, {}) as Dictionary
		entry_id = str(_dialogue_entry_id.get(npc_id, ""))
	else:
		var parsed: Dictionary = _parse_dialogue_array(dialogue_json)
		graph = parsed.get("graph", {}) as Dictionary
		entry_id = str(parsed.get("entry", ""))

	if graph.is_empty():
		Log.warn("No dialogue available for NPC: %s" % npc_id)
		return

	if entry_id.is_empty() or not graph.has(entry_id):
		entry_id = _pick_fallback_entry(graph)

	dialogue_requested.emit(npc_id, graph, entry_id)


func _pick_fallback_entry(graph: Dictionary) -> String:
	if graph.has("start"):
		return "start"
	var keys := graph.keys()
	return str(keys[0]) if keys.size() > 0 else ""


func set_flag(key: String, value: Variant) -> void:
	_flags[key] = value


func get_flag(key: String, default: Variant = null) -> Variant:
	return _flags.get(key, default)
