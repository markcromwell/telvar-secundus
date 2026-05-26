extends Node

signal quest_updated(id)
signal objective_completed(quest_id, obj_id)

var quests: Dictionary = {}

func start_quest(id: String) -> void:
	if not quests.has(id):
		quests[id] = {
			"status": "active",
			"objectives": {}
		}
	quest_updated.emit(id)

func complete_objective(quest_id: String, obj_id: String) -> void:
	if quests.has(quest_id):
		quests[quest_id]["objectives"][obj_id] = true
		objective_completed.emit(quest_id, obj_id)

func is_complete(id: String) -> bool:
	if quests.has(id):
		return quests[id].get("status") == "complete"
	return false
