extends StaticBody2D

const DIALOGUE_PATH := "res://assets/dialogue/%s.json"

@export var dialogue_id: String = ""

@onready var _interaction_zone: Area2D = $InteractionZone
@onready var _prompt: Label = $PromptLabel

var _player_in_range: bool = false
var _player_body: Node2D = null


func _ready() -> void:
	if _interaction_zone:
		_interaction_zone.body_entered.connect(_on_body_entered)
		_interaction_zone.body_exited.connect(_on_body_exited)
	if _prompt:
		_prompt.visible = false


func _on_body_entered(body: Node) -> void:
	if not _is_interactable_player(body):
		return
	_player_in_range = true
	_player_body = body as Node2D
	_update_prompt()


func _on_body_exited(body: Node) -> void:
	if body != _player_body:
		return
	_player_in_range = false
	_player_body = null
	_update_prompt()


func _update_prompt() -> void:
	if not _prompt:
		return
	var busy: bool = DialogueManager._active
	_prompt.visible = _player_in_range and not busy


func _is_interactable_player(body: Node) -> bool:
	if not (body is CharacterBody2D):
		return false
	if body.is_in_group("player"):
		return true
	return str(body.name) == "Player"


func _process(_delta: float) -> void:
	_update_prompt()
	if not _player_in_range:
		return
	if DialogueManager._active:
		return
	if not Input.is_action_just_pressed("ui_accept"):
		return
	var data: Array = _load_dialogue_json()
	if data.is_empty():
		return
	DialogueManager.show_dialogue(dialogue_id, data)


func _load_dialogue_json() -> Array:
	if dialogue_id.is_empty():
		push_warning("NPC: dialogue_id is empty on node '%s'" % name)
		return []
	var path: String = DIALOGUE_PATH % dialogue_id
	if not FileAccess.file_exists(path):
		push_warning("NPC: missing dialogue file: %s" % path)
		return []
	var text: String = FileAccess.get_file_as_string(path)
	var parsed: Variant = JSON.parse_string(text)
	if parsed == null:
		push_warning("NPC: invalid JSON in %s" % path)
		return []
	if typeof(parsed) != TYPE_ARRAY:
		return []
	return parsed as Array
