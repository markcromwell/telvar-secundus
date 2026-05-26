extends Node

const SAVE_PATH := "user://quest_state.cfg"

## Quest IDs that have been assigned (journal entries).
var _assigned: Dictionary = {}


func _ready() -> void:
	_load_state()


func assign_quest(quest_id: String) -> void:
	if quest_id.is_empty():
		return
	_assigned[quest_id] = true
	_save_state()


func get_journal() -> Array:
	var out: Array = []
	var ids: Array = _assigned.keys()
	ids.sort()
	for quest_id in ids:
		if _assigned.get(quest_id, false):
			out.append(_build_quest_entry(str(quest_id)))
	return out


func _build_quest_entry(quest_id: String) -> Dictionary:
	var path := "res://assets/quests/%s.json" % quest_id
	if FileAccess.file_exists(path):
		var file := FileAccess.open(path, FileAccess.READ)
		if file:
			var text := file.get_as_text()
			var parser := JSON.new()
			if parser.parse(text) == OK and parser.data is Dictionary:
				var data: Dictionary = (parser.data as Dictionary).duplicate(true)
				if not data.has("status") or str(data.get("status", "")) == "not_started":
					data["status"] = "active"
				return data
	return {
		"id": quest_id,
		"title": quest_id,
		"description": "",
		"status": "active",
	}


func _load_state() -> void:
	_assigned.clear()
	var cf := ConfigFile.new()
	if cf.load(SAVE_PATH) != OK:
		return
	var stored: Variant = cf.get_value("journal", "assigned", {})
	if stored is Dictionary:
		for k in (stored as Dictionary).keys():
			_assigned[str(k)] = bool((stored as Dictionary)[k])


func _save_state() -> void:
	var cf := ConfigFile.new()
	cf.set_value("journal", "assigned", _assigned.duplicate(true))
	cf.save(SAVE_PATH)
