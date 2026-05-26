extends Node

## Tracks active quests loaded from `res://assets/quests/{id}.json`.
## Each entry: quest_id → { id, title, status, objectives } where objectives
## is an Array of { id, desc, complete }.

var quests: Dictionary = {}

signal quest_updated(quest_id: String)
signal objective_completed(quest_id: String, objective_id: String)


func start_quest(id: String) -> void:
	if quests.has(id):
		return
	var path: String = "res://assets/quests/%s.json" % id
	if not FileAccess.file_exists(path):
		push_error("QuestManager: missing quest file: %s" % path)
		return
	var file := FileAccess.open(path, FileAccess.READ)
	if file == null:
		push_error("QuestManager: could not open: %s" % path)
		return
	var text := file.get_as_text()
	var json := JSON.new()
	var parse_err := json.parse(text)
	if parse_err != OK:
		push_error("QuestManager: invalid JSON in %s (error %s)" % [path, parse_err])
		return
	var data = json.get_data()
	if typeof(data) != TYPE_DICTIONARY:
		push_error("QuestManager: quest root must be an object: %s" % path)
		return
	var raw_objectives: Array = data.get("objectives", [])
	var objectives: Array = []
	for item in raw_objectives:
		if typeof(item) != TYPE_DICTIONARY:
			continue
		var obj: Dictionary = item
		if not obj.has("id"):
			continue
		objectives.append({
			"id": str(obj["id"]),
			"desc": str(obj.get("desc", "")),
			"complete": false,
		})
	quests[id] = {
		"id": str(data.get("id", id)),
		"title": str(data.get("title", "")),
		"status": "active",
		"objectives": objectives,
	}
	quest_updated.emit(id)


func complete_objective(quest_id: String, obj_id: String) -> void:
	if not quests.has(quest_id):
		return
	var quest: Dictionary = quests[quest_id]
	var list: Array = quest["objectives"]
	for i in list.size():
		var entry: Dictionary = list[i]
		if str(entry.get("id", "")) != obj_id:
			continue
		if entry.get("complete", false):
			return
		entry["complete"] = true
		list[i] = entry
		objective_completed.emit(quest_id, obj_id)
		if is_complete(quest_id):
			quest["status"] = "complete"
		quest_updated.emit(quest_id)
		return


func is_complete(quest_id: String) -> bool:
	if not quests.has(quest_id):
		return false
	var list: Array = quests[quest_id]["objectives"]
	if list.is_empty():
		return true
	for entry in list:
		if typeof(entry) != TYPE_DICTIONARY:
			continue
		var done: bool = bool(entry.get("complete", false))
		if not done:
			return false
	return true
