extends CharacterBody2D

## City guard: interact to open dialogue JSON keyed by dialogue_id.

@export var dialogue_id: String = "city_guard"

var _player_in_range: bool = false
var _json_cache: Variant = null

@onready var _interaction_zone: Area2D = $InteractionZone
@onready var _prompt: Label = $PromptLabel


func _ready() -> void:
	_interaction_zone.body_entered.connect(_show_prompt)
	_interaction_zone.body_exited.connect(_hide_prompt)


func _show_prompt(_body: Node2D) -> void:
	_player_in_range = true
	_prompt.visible = true


func _hide_prompt(_body: Node2D) -> void:
	_player_in_range = false
	_prompt.visible = false


func _get_dialogue() -> Variant:
	if _json_cache != null:
		return _json_cache
	var path := "res://assets/dialogue/%s.json" % dialogue_id
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		push_error("NPC: missing dialogue file %s" % path)
		return []
	var parsed := JSON.parse_string(f.get_as_text())
	_json_cache = parsed
	return parsed


func _process(_delta: float) -> void:
	if not _player_in_range:
		return
	if not Input.is_action_just_pressed("ui_accept"):
		return
	var payload := _get_dialogue()
	DialogueManager.show_dialogue(dialogue_id, payload)
