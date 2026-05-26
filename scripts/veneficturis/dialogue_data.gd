extends Node

## Lightweight dialogue lines keyed by dialogue_id (extend or replace when a full dialogue system lands).

const PATH := "res://data/library_dialogue.json"

var _lines: Dictionary = {}


func _ready() -> void:
	if not FileAccess.file_exists(PATH):
		push_warning("Missing dialogue file: %s" % PATH)
		return
	var f := FileAccess.open(PATH, FileAccess.READ)
	if f == null:
		push_warning("Could not open dialogue file: %s" % PATH)
		return
	var parsed = JSON.parse_string(f.get_as_text())
	if typeof(parsed) == TYPE_DICTIONARY:
		_lines = parsed
	else:
		push_warning("library_dialogue.json must be a JSON object")


func get_line(dialogue_id: String) -> String:
	return str(_lines.get(dialogue_id, ""))
