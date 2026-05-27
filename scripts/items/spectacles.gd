extends Area2D

## Timon's spectacles pickup in the library stacks. Completes the matching quest objective.

const QUEST_ID := "timons_spectacles"
const OBJECTIVE_ID := "find_spectacles"


func _ready() -> void:
	monitoring = true
	body_entered.connect(_on_body_entered)


func _on_body_entered(body: Node) -> void:
	if not _is_player(body):
		return
	_pickup()


func _is_player(body: Node) -> bool:
	return body.is_in_group("player") or body.name == "Player"


func _pickup() -> void:
	QuestManager.complete_objective(QUEST_ID, OBJECTIVE_ID)
	queue_free()
