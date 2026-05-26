extends Node

## Minimal quest state for world pickups and dialogue gating.
## Quest JSON lives under res://assets/quests/; runtime state is in `quests`.

signal quest_updated(quest_id: String)
signal objective_completed(quest_id: String, objective_id: String)

var quests: Dictionary = {}  # quest_id → { "status": String, "objectives": Dictionary }


func start_quest(id: String) -> void:
	if not quests.has(id):
		quests[id] = {"status": "active", "objectives": {}}
	quest_updated.emit(id)


func complete_objective(quest_id: String, obj_id: String) -> void:
	if not quests.has(quest_id):
		quests[quest_id] = {"status": "active", "objectives": {}}
	var q: Dictionary = quests[quest_id]
	var objectives: Dictionary = q.get("objectives", {}) as Dictionary
	objectives[obj_id] = true
	q["objectives"] = objectives
	objective_completed.emit(quest_id, obj_id)
	quest_updated.emit(quest_id)


func is_complete(id: String) -> bool:
	if not quests.has(id):
		return false
	var q: Dictionary = quests[id]
	return str(q.get("status", "")) == "completed"
