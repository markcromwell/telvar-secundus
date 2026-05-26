extends Node
## Central quest copy; sealed wings post-rest line is driven by JSON for authoring/tests.

const SEALED_WINGS_QUEST_PATH := "res://data/quests/sealed_wings.json"

var sealed_wings_title: String = "The Sealed Wings"
var sealed_wings_objective: String = ""


func _ready() -> void:
	_load_sealed_wings_baseline()


func _load_sealed_wings_baseline() -> void:
	var f := FileAccess.open(SEALED_WINGS_QUEST_PATH, FileAccess.READ)
	if f == null:
		push_error("QuestLog: missing %s" % SEALED_WINGS_QUEST_PATH)
		return
	var data: Variant = JSON.parse_string(f.get_as_text())
	if typeof(data) != TYPE_DICTIONARY:
		push_error("QuestLog: invalid JSON in sealed wings quest file")
		return
	sealed_wings_title = str(data.get("title", sealed_wings_title))


func apply_sealed_wings_after_telvar_room_night() -> void:
	var f := FileAccess.open(SEALED_WINGS_QUEST_PATH, FileAccess.READ)
	if f == null:
		return
	var data: Variant = JSON.parse_string(f.get_as_text())
	if typeof(data) != TYPE_DICTIONARY:
		return
	var lines: Variant = data.get("objective_lines", {})
	if typeof(lines) != TYPE_DICTIONARY:
		return
	sealed_wings_objective = str(lines.get("after_telvar_room_rest_night", ""))
