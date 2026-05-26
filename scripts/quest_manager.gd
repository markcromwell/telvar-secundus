extends Node

## Autoload singleton: active/completed quests, per-objective booleans, and lore keys.
## Persists for the session across scene changes (autoload lifetime).

signal quest_updated(quest_id: String)
signal objective_completed(quest_id: String, obj_id: String)

## quest_id -> { "status": String, "objectives": Dictionary } — objectives maps obj_id -> bool
var quests: Dictionary = {}

## Unlocked lore identifiers (e.g. from dialogue flags).
var lore_keys: Array = []


func start_quest(id: String) -> void:
	if quests.has(id):
		return

	var objectives: Dictionary = {}
	var path := "res://assets/quests/%s.json" % id
	if FileAccess.file_exists(path):
		var file := FileAccess.open(path, FileAccess.READ)
		if file:
			var text := file.get_as_text()
			var json := JSON.new()
			if json.parse(text) == OK and typeof(json.data) == TYPE_DICTIONARY:
				var data: Dictionary = json.data
				for item in data.get("objectives", []):
					if typeof(item) == TYPE_DICTIONARY:
						var d: Dictionary = item
						if d.has("id"):
							objectives[str(d["id"])] = false

	quests[id] = {"status": "active", "objectives": objectives}
	quest_updated.emit(id)


func complete_objective(quest_id: String, obj_id: String) -> void:
	if not quests.has(quest_id):
		return
	var q: Dictionary = quests[quest_id]
	var objs: Dictionary = q.get("objectives", {})
	if not objs.has(obj_id):
		return
	if objs[obj_id]:
		return
	objs[obj_id] = true
	objective_completed.emit(quest_id, obj_id)
	quest_updated.emit(quest_id)
	if _all_objectives_done(objs):
		q["status"] = "completed"
		quest_updated.emit(quest_id)


func is_complete(id: String) -> bool:
	if not quests.has(id):
		return false
	var q: Dictionary = quests[id]
	if str(q.get("status", "")) == "completed":
		return true
	return _all_objectives_done(q.get("objectives", {}))


func lore_unlock(key: String) -> void:
	if key.is_empty():
		return
	if lore_keys.has(key):
		return
	lore_keys.append(key)


func get_lore_keys() -> Array:
	return lore_keys.duplicate()


func serialize() -> Dictionary:
	return {
		"quests": quests.duplicate(true),
		"lore_keys": lore_keys.duplicate(),
	}


func deserialize(data: Dictionary) -> void:
	quests.clear()
	lore_keys.clear()
	if data.has("quests") and typeof(data["quests"]) == TYPE_DICTIONARY:
		quests = data["quests"].duplicate(true)
	if data.has("lore_keys") and typeof(data["lore_keys"]) == TYPE_ARRAY:
		lore_keys.assign(data["lore_keys"])


func _all_objectives_done(objs: Dictionary) -> bool:
	if objs.is_empty():
		return false
	for k in objs:
		if not objs[k]:
			return false
	return true
