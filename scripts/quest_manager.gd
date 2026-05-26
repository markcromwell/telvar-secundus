extends Node

## Autoload: tracks active quests, per-objective completion, and completion state.

signal quest_updated(id: String)
signal objective_completed(id: String, obj_id: String)

var quests: Dictionary = {}  # quest_id → { status, objectives }


func start_quest(id: String) -> void:
	var objectives_state: Dictionary = {}
	var quest_path := "res://assets/quests/%s.json" % id
	if FileAccess.file_exists(quest_path):
		var file := FileAccess.open(quest_path, FileAccess.READ)
		if file:
			var parsed: Variant = JSON.parse_string(file.get_as_text())
			if typeof(parsed) == TYPE_DICTIONARY:
				var raw_objectives: Array = parsed.get("objectives", [])
				for item in raw_objectives:
					if typeof(item) == TYPE_DICTIONARY and item.has("id"):
						objectives_state[String(item["id"])] = false

	quests[id] = {"status": "active", "objectives": objectives_state}
	quest_updated.emit(id)


func complete_objective(quest_id: String, obj_id: String) -> void:
	if not quests.has(quest_id):
		return
	var entry: Dictionary = quests[quest_id]
	var objs: Dictionary = entry["objectives"] if entry.has("objectives") else {}
	if not entry.has("objectives"):
		entry["objectives"] = objs
	objs[obj_id] = true

	var all_done := true
	for k in objs:
		if objs[k] != true:
			all_done = false
			break
	if all_done and not objs.is_empty():
		entry["status"] = "completed"

	objective_completed.emit(quest_id, obj_id)
	quest_updated.emit(quest_id)


func is_complete(id: String) -> bool:
	if not quests.has(id):
		return false
	var entry: Dictionary = quests[id]
	if String(entry.get("status", "")) == "completed":
		return true
	var objs: Dictionary = entry.get("objectives", {})
	if objs.is_empty():
		return false
	for k in objs:
		if objs[k] != true:
			return false
	return true
