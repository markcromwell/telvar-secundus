## SaveDataSchema — canonical save-game JSON shape for Telvar: Chronicles of Secundus.
##
## CI parity: tests/test_save_data_schema.py mirrors default_save_dict / merge_with_defaults /
## JSON round-trip; update both when changing serialization behavior.
##
## All fields are plain JSON-serializable values (Dictionary / Array / String / int / float / bool)
## so they can cross HTML5 (user://) and desktop builds without binary resources.
##
## Root object (Dictionary) keys and types:
##   version: int — schema revision; bump when migrating on load.
##   scene_path: String — res:// path of the active gameplay scene (or empty before first scene).
##   tile_coords: Dictionary — {"x": int, "y": int} player tile on the scene grid (16×16 logical tiles).
##   quest_state: Dictionary — quest_id (String) -> Variant (bool / int / String / Dictionary / Array).
##   lore_entries: Array — lore entry ids (String) in unlock order; duplicates allowed if gameplay adds them.
##   inventory: Dictionary — item_id (String) -> Variant; typically int count, may be nested for mods/tools.
##   hp: float — current hit points.
##   max_hp: float — maximum hit points (persisted so UI and caps stay consistent).
##   mana: float — current mana.
##   max_mana: float — maximum mana.
##   act_flags: Dictionary — act-scoped flag name (String) -> bool (other JSON types allowed if needed).
##   dialogue_flags: Dictionary — dialogue flag name (String) -> bool (or String/int for branching keys).
##   play_time_seconds: float — accumulated play time in seconds (monotonic from systems; not wall clock).
##
## File layout (user://, slots 1–3 + autosave):
##   user://save_slot_1.json … user://save_slot_3.json
##   user://save_autosave.json
##
## Usage (from gameplay code; read-only / copy patterns avoid accidental mutation):
##   var data := SaveDataSchema.default_save_dict()
##   data["scene_path"] = "res://maps/secundus_street.tscn"
##   data["tile_coords"] = {"x": 12, "y": 5}
##   SaveDataSchema.write_slot(1, data)
##   var loaded := SaveDataSchema.read_slot(1)
##
## Dictionary serialization (JSON-safe, nested dict/array deep-copied):
##   var snapshot := SaveDataSchema.export_state_to_dictionary(data)
##   var live: Dictionary = {}
##   SaveDataSchema.populate_state_from_dictionary(live, snapshot)
class_name SaveDataSchema
extends RefCounted

const SCHEMA_VERSION := 1

const SLOT_PATH_TEMPLATE := "user://save_slot_%d.json"
const AUTOSAVE_PATH := "user://save_autosave.json"


static func default_save_dict() -> Dictionary:
	return {
		"version": SCHEMA_VERSION,
		"scene_path": "",
		"tile_coords": {"x": 0, "y": 0},
		"quest_state": {},
		"lore_entries": [],
		"inventory": {},
		"hp": 1.0,
		"max_hp": 1.0,
		"mana": 0.0,
		"max_mana": 0.0,
		"act_flags": {},
		"dialogue_flags": {},
		"play_time_seconds": 0.0,
	}


static func user_slot_path(slot: int) -> String:
	assert(slot >= 1 and slot <= 3)
	return SLOT_PATH_TEMPLATE % slot


static func user_autosave_path() -> String:
	return AUTOSAVE_PATH


## Returns a deep-copied base document with all keys from `data` applied on top.
## `tile_coords` is key-merged so a partial `{"x": 3}` does not drop `y` from defaults.
## `quest_state`, `inventory`, and other container fields are taken from `data` as a whole when present,
## preserving nested content for round-trip fidelity. Unknown top-level keys are kept verbatim.
static func merge_with_defaults(data: Dictionary) -> Dictionary:
	var out := default_save_dict().duplicate(true)
	for k in data.keys():
		if k == "tile_coords" and typeof(data[k]) == TYPE_DICTIONARY:
			var merged: Dictionary = out["tile_coords"].duplicate()
			var incoming: Dictionary = data[k]
			for ck in incoming.keys():
				merged[ck] = incoming[ck]
			out["tile_coords"] = merged
		else:
			out[k] = data[k]
	return out


## Returns a deep-copied save document merged with defaults (nested quest_state / inventory / flags intact).
## Use before JSON.stringify or handing data to systems that must not see live references.
static func export_state_to_dictionary(state: Dictionary) -> Dictionary:
	return merge_with_defaults(state).duplicate(true)


## Replaces `target` contents with merge_with_defaults(source) using a deep copy (no shared nested refs).
static func populate_state_from_dictionary(target: Dictionary, source: Dictionary) -> void:
	var merged := merge_with_defaults(source).duplicate(true)
	target.clear()
	for k in merged.keys():
		target[k] = merged[k]


static func to_json_string(data: Dictionary, pretty: bool = false) -> String:
	var indent := "\t" if pretty else ""
	return JSON.stringify(data, indent)


static func from_json_string(text: String) -> Dictionary:
	if text.strip_edges().is_empty():
		return {}
	var parser := JSON.new()
	var err := parser.parse(text)
	if err != OK:
		push_warning("SaveDataSchema: JSON parse failed (%s)" % error_string(err))
		return {}
	var root: Variant = parser.data
	if typeof(root) != TYPE_DICTIONARY:
		push_warning("SaveDataSchema: root JSON value is not an object")
		return {}
	return (root as Dictionary).duplicate(true)


## Full structural round-trip through JSON (deep copy). Useful for verifying quest/inventory payloads.
static func round_trip(data: Dictionary) -> Dictionary:
	return from_json_string(to_json_string(data, false))


static func write_slot(slot: int, data: Dictionary) -> bool:
	assert(slot >= 1 and slot <= 3)
	return _write_text(user_slot_path(slot), to_json_string(merge_with_defaults(data), true))


static func write_autosave(data: Dictionary) -> bool:
	return _write_text(user_autosave_path(), to_json_string(merge_with_defaults(data), true))


static func read_slot(slot: int) -> Dictionary:
	assert(slot >= 1 and slot <= 3)
	return _read_save_file(user_slot_path(slot))


static func read_autosave() -> Dictionary:
	return _read_save_file(user_autosave_path())


static func _read_save_file(path: String) -> Dictionary:
	if not FileAccess.file_exists(path):
		return default_save_dict()
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		push_warning("SaveDataSchema: cannot open for read: %s (%s)" % [path, error_string(FileAccess.get_open_error())])
		return default_save_dict()
	var text := f.get_as_text()
	var parsed := from_json_string(text)
	if parsed.is_empty():
		return default_save_dict()
	return merge_with_defaults(parsed)


static func _write_text(path: String, text: String) -> bool:
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f == null:
		push_warning("SaveDataSchema: cannot open for write: %s (%s)" % [path, error_string(FileAccess.get_open_error())])
		return false
	f.store_string(text)
	return true
