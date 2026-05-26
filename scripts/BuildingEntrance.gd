extends Area2D

@export var building_label: String = ""

@onready var _prompt: Label = $EnterPrompt


func _ready() -> void:
	body_entered.connect(_on_body_entered)
	body_exited.connect(_on_body_exited)
	if _prompt:
		_prompt.text = "Press E to enter"
		_prompt.visible = false


func _on_body_entered(body: Node) -> void:
	if not _is_player_body(body):
		return
	if _prompt:
		_prompt.visible = true


func _on_body_exited(body: Node) -> void:
	if not _is_player_body(body):
		return
	if _prompt:
		_prompt.visible = false


func _is_player_body(body: Node) -> bool:
	return body.is_in_group("player") or body is CharacterBody2D
