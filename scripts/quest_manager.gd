extends Node

## Autoload singleton: quest state, objectives, and progress (Godot 4.3).

signal quest_updated(id: String)
signal objective_completed(id: String, obj_id: String)

## quest_id -> { "status": "active"|"completed", "objectives": { obj_id -> { "desc", "completed" } } }
var quests: Dictionary = {}


func load_quest_definition(id: String) -> Dictionary:
	var path := "res://assets/quests/%s.json" % id
	var file := FileAccess.open(path, FileAccess.READ)
	if file == null:
		push_error("QuestManager: could not open quest file: %s" % path)
		return {}
	var text := file.get_as_text()
	file.close()
	var parsed: Variant = JSON.parse_string(text)
	if typeof(parsed) != TYPE_DICTIONARY:
		push_error("QuestManager: invalid JSON for quest id: %s" % id)
		return {}
	return parsed as Dictionary


func start_quest(id: String) -> void:
	if quests.has(id):
		return
	var def := load_quest_definition(id)
	if def.is_empty():
		return
	var objectives: Dictionary = {}
	var raw_objectives: Variant = def.get("objectives", [])
	if typeof(raw_objectives) == TYPE_ARRAY:
		for item in raw_objectives as Array:
			if typeof(item) != TYPE_DICTIONARY:
				continue
			var row := item as Dictionary
			var obj_id := str(row.get("id", ""))
			if obj_id.is_empty():
				continue
			objectives[obj_id] = {
				"desc": str(row.get("desc", "")),
				"completed": false,
			}
	quests[id] = {"status": "active", "objectives": objectives}
	quest_updated.emit(id)


func complete_objective(quest_id: String, obj_id: String) -> void:
	if not quests.has(quest_id):
		return
	var q: Dictionary = quests[quest_id]
	var objectives: Dictionary = q.get("objectives", {})
	if not objectives.has(obj_id):
		return
	var obj: Dictionary = objectives[obj_id]
	obj["completed"] = true
	objectives[obj_id] = obj
	q["objectives"] = objectives
	quests[quest_id] = q
	objective_completed.emit(quest_id, obj_id)
	_check_completion(quest_id)


func is_complete(id: String) -> bool:
	if not quests.has(id):
		return false
	var objectives: Dictionary = (quests[id] as Dictionary).get("objectives", {})
	if objectives.is_empty():
		return false
	for key in objectives:
		var obj: Dictionary = objectives[key] as Dictionary
		if not bool(obj.get("completed", false)):
			return false
	return true


func get_progress(quest_id: String) -> Dictionary:
	var done := 0
	var total := 0
	if not quests.has(quest_id):
		return {"done": done, "total": total}
	var objectives: Dictionary = (quests[quest_id] as Dictionary).get("objectives", {})
	total = objectives.size()
	for key in objectives:
		var obj: Dictionary = objectives[key] as Dictionary
		if bool(obj.get("completed", false)):
			done += 1
	return {"done": done, "total": total}


func _check_completion(quest_id: String) -> void:
	if not quests.has(quest_id):
		return
	var q: Dictionary = quests[quest_id]
	if str(q.get("status", "")) == "completed":
		return
	var objectives: Dictionary = q.get("objectives", {})
	if objectives.is_empty():
		return
	for key in objectives:
		var obj: Dictionary = objectives[key] as Dictionary
		if not bool(obj.get("completed", false)):
			return
	q["status"] = "completed"
	quests[quest_id] = q
	quest_updated.emit(quest_id)
