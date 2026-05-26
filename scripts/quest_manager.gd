extends Node

## quest_id → { status, title, objectives }
signal quest_updated(quest_id: String)
signal objective_completed(quest_id: String, obj_id: String)

var quests: Dictionary = {}


func start_quest(id: String) -> void:
	if quests.has(id):
		return
	var raw := _load_quest_json(id)
	if raw.is_empty():
		return
	if str(raw.get("id", "")) != id:
		push_warning("Quest id mismatch in JSON: expected %s" % id)
		return
	var objs: Array = []
	for item in raw.get("objectives", []):
		if typeof(item) != TYPE_DICTIONARY:
			continue
		var d: Dictionary = item
		objs.append(
			{"id": str(d.get("id", "")), "desc": str(d.get("desc", "")), "done": false}
		)
	quests[id] = {
		"title": str(raw.get("title", "")),
		"status": "active",
		"objectives": objs,
	}
	quest_updated.emit(id)


func complete_objective(quest_id: String, obj_id: String) -> void:
	if not quests.has(quest_id):
		return
	var q: Dictionary = quests[quest_id]
	var list: Array = q.get("objectives", [])
	for i in list.size():
		var o: Dictionary = list[i]
		if str(o.get("id", "")) != obj_id:
			continue
		if o.get("done", false):
			return
		o["done"] = true
		list[i] = o
		q["objectives"] = list
		objective_completed.emit(quest_id, obj_id)
		quest_updated.emit(quest_id)
		if _all_objectives_done(q):
			q["status"] = "completed"
			quests[quest_id] = q
			quest_updated.emit(quest_id)
		return


func is_complete(id: String) -> bool:
	if not quests.has(id):
		return false
	var q: Dictionary = quests[id]
	return str(q.get("status", "")) == "completed" or _all_objectives_done(q)


func _all_objectives_done(q: Dictionary) -> bool:
	var list: Array = q.get("objectives", [])
	if list.is_empty():
		return false
	for o in list:
		if not (o as Dictionary).get("done", false):
			return false
	return true


func _load_quest_json(id: String) -> Dictionary:
	var path := "res://assets/quests/%s.json" % id
	if not FileAccess.file_exists(path):
		push_error("Quest file not found: %s" % path)
		return {}
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		push_error("Could not open quest file: %s" % path)
		return {}
	var txt := f.get_as_text()
	var data = JSON.parse_string(txt)
	if typeof(data) != TYPE_DICTIONARY:
		push_error("Invalid quest JSON for %s" % id)
		return {}
	return data
