extends Node2D
## Myramar's room: when the player returns with evidence, the post-evidence branch
## from `assets/dialogue/myramar.json` runs via DialogueManager (JSON tree loader).

const FLAG_EVIDENCE := "evidence_collected"
const _DialogueManagerScript := preload("res://scripts/dialogue_manager.gd")


func _ready() -> void:
	if DialogueManager.get_flag(FLAG_EVIDENCE) and not DialogueManager.get_flag(_DialogueManagerScript.FLAG_RESOLVED):
		call_deferred("_begin_post_evidence_dialogue")


func _begin_post_evidence_dialogue() -> void:
	DialogueManager.show_dialogue("myramar", "after_evidence_choice")
