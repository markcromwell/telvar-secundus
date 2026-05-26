extends StaticBody2D

## Reusable priest or static NPC: AnimatedSprite2D + Area2D interaction, dialogue via DialogueManager.

@export var dialogue_id: String = ""

@onready var _sprite: AnimatedSprite2D = $AnimatedSprite2D
@onready var _interaction_zone: Area2D = $InteractionArea

var _prompt: Label
var _player_near: bool = false


func _ready() -> void:
	_prompt = _make_prompt_label()
	add_child(_prompt)
	_prompt.visible = false
	_interaction_zone.body_entered.connect(_on_body_entered)
	_interaction_zone.body_exited.connect(_on_body_exited)


func _make_prompt_label() -> Label:
	var l := Label.new()
	l.name = "PressEPrompt"
	l.text = "Press E"
	l.z_index = 10
	l.position = Vector2(-36, -52)
	return l


func _on_body_entered(body: Node2D) -> void:
	if not _is_player_body(body):
		return
	_player_near = true
	_prompt.visible = true


func _on_body_exited(body: Node2D) -> void:
	if not _is_player_body(body):
		return
	_player_near = false
	_prompt.visible = false


func _is_player_body(body: Node2D) -> bool:
	if body == self:
		return false
	return body.is_in_group("player") or body is CharacterBody2D


func _process(_delta: float) -> void:
	if not _player_near:
		return
	if not Input.is_action_just_pressed("ui_accept"):
		return
	_open_dialogue()


func _open_dialogue() -> void:
	if dialogue_id.is_empty():
		push_warning("NPC: dialogue_id is empty on %s" % name)
		return
	var path := "res://assets/dialogue/%s.json" % dialogue_id
	if not FileAccess.file_exists(path):
		push_error("NPC: missing dialogue file %s" % path)
		return
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		push_error("NPC: could not open %s" % path)
		return
	var txt := f.get_as_text()
	f.close()
	var parsed: Variant = JSON.parse_string(txt)
	if parsed == null or typeof(parsed) != TYPE_ARRAY:
		push_error("NPC: dialogue JSON must be an array: %s" % path)
		return
	DialogueManager.show_dialogue(dialogue_id, parsed as Array)
