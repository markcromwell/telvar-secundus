extends Node
## Autoload: loads quest JSON from res://assets/quests/ and tracks objectives.

signal quest_updated(quest_id: String)
signal objective_completed(quest_id: String, objective_id: String)

# quest_id -> { "title": String, "status": String, "objectives": { obj_id -> bool } }
var quests: Dictionary = {}


func start_quest(id: String) -> void:
	if quests.has(id):
		return
	var path := "res://assets/quests/%s.json" % id
	if not FileAccess.file_exists(path):
		push_warning("QuestManager: missing quest file %s" % path)
		return
	var f := FileAccess.open(path, FileAccess.READ)
	var parsed = JSON.parse_string(f.get_as_text())
	if typeof(parsed) != TYPE_DICTIONARY:
		push_warning("QuestManager: invalid quest JSON %s" % path)
		return
	var d: Dictionary = parsed
	var objectives: Dictionary = {}
	for item in d.get("objectives", []):
		if typeof(item) != TYPE_DICTIONARY:
			continue
		var oid := String(item.get("id", ""))
		if oid.is_empty():
			continue
		objectives[oid] = false
	quests[id] = {
		"title": String(d.get("title", id)),
		"status": "active",
		"objectives": objectives,
	}
	quest_updated.emit(id)


func complete_objective(quest_id: String, obj_id: String) -> void:
	if not quests.has(quest_id):
		return
	var q: Dictionary = quests[quest_id]
	var objs: Dictionary = q["objectives"]
	if not objs.has(obj_id) or objs[obj_id]:
		return
	objs[obj_id] = true
	objective_completed.emit(quest_id, obj_id)
	quest_updated.emit(quest_id)
	if is_complete(quest_id):
		q["status"] = "complete"
		quest_updated.emit(quest_id)


func is_complete(quest_id: String) -> bool:
	if not quests.has(quest_id):
		return false
	var objs: Dictionary = quests[quest_id]["objectives"]
	for k in objs.keys():
		if not bool(objs[k]):
			return false
	return true
