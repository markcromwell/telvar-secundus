extends CharacterBody2D
## Act 5 office meeting: auto-starts Myramar dialogue when the player enters the zone
## after Act 3 completion. Dialogue JSON awards the Sealed Wing Key (see DialogueManager).

const ACT3_COMPLETE_FLAG := "act_3_complete"
const DIALOGUE_NPC_ID := "myramar"
const DIALOGUE_JSON_PATH := "res://assets/dialogue/myramar.json"

@onready var _zone: Area2D = $InteractionZone

var _dialogue: Array = []
var _meeting_done := false


func _ready() -> void:
	_load_dialogue_json()
	_zone.body_entered.connect(_on_zone_body_entered)
	_zone.body_exited.connect(_on_zone_body_exited)
	if not DialogueManager.dialogue_finished.is_connected(_on_dialogue_finished):
		DialogueManager.dialogue_finished.connect(_on_dialogue_finished)


func _load_dialogue_json() -> void:
	if not FileAccess.file_exists(DIALOGUE_JSON_PATH):
		_dialogue = []
		return
	var f := FileAccess.open(DIALOGUE_JSON_PATH, FileAccess.READ)
	if f == null:
		_dialogue = []
		return
	var parsed = JSON.parse_string(f.get_as_text())
	_dialogue = parsed if typeof(parsed) == TYPE_ARRAY else []


func _on_zone_body_entered(body: Node2D) -> void:
	if not _is_player_body(body):
		return
	if _meeting_done:
		return
	if DialogueManager.is_dialogue_active():
		return
	if not bool(DialogueManager.get_flag(ACT3_COMPLETE_FLAG, false)):
		return
	if _dialogue.is_empty():
		return
	DialogueManager.show_dialogue(DIALOGUE_NPC_ID, _dialogue)


func _on_zone_body_exited(body: Node2D) -> void:
	if _is_player_body(body):
		pass


func _on_dialogue_finished(npc_id: String) -> void:
	if npc_id == DIALOGUE_NPC_ID:
		_meeting_done = true


func _is_player_body(body: Node2D) -> bool:
	if body == null:
		return false
	if body.is_in_group("player"):
		return true
	# Fallback if another phase has not yet added the group
	return body.name == "Player"
