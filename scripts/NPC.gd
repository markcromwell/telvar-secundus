extends CharacterBody2D
## Base NPC: interaction `Area2D`, optional "Press E" prompt, and dialogue via
## `DialogueManager` using JSON keyed by `dialogue_id` (basename under
## `res://assets/dialogue/`).

@export var dialogue_id: String = ""

var _interaction_zone: Area2D
var _prompt: Label
var _player_in_range: bool = false


func _ready() -> void:
	_interaction_zone = get_node_or_null("InteractionZone") as Area2D
	_prompt = get_node_or_null("PromptLabel") as Label
	if _prompt == null:
		_prompt = get_node_or_null("InteractionZone/PromptLabel") as Label

	if _interaction_zone == null:
		push_warning("NPC: add child Area2D named InteractionZone for player proximity.")
		return

	_interaction_zone.body_entered.connect(_on_body_entered)
	_interaction_zone.body_exited.connect(_on_body_exited)
	if _prompt:
		_prompt.visible = false


func _on_body_entered(body: Node2D) -> void:
	if not _is_player(body):
		return
	_player_in_range = true
	if _prompt:
		_prompt.text = "Press E"
		_prompt.visible = true


func _on_body_exited(body: Node2D) -> void:
	if not _is_player(body):
		return
	_player_in_range = false
	if _prompt:
		_prompt.visible = false


func _is_player(body: Node2D) -> bool:
	return body.is_in_group("player")


func _process(_delta: float) -> void:
	if not _player_in_range or dialogue_id.is_empty():
		return
	if Input.is_action_just_pressed("ui_interact"):
		DialogueManager.show_dialogue(dialogue_id)
