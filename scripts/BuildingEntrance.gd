extends Area2D

## Entrance trigger: shows a prompt label while the player overlaps this area.
@export var building_label: String = ""

var _prompt: Label


func _ready() -> void:
	_prompt = get_node_or_null("Label") as Label
	body_entered.connect(_on_body_entered)
	body_exited.connect(_on_body_exited)
	if _prompt:
		_prompt.text = "Press E to enter"
		_prompt.visible = false


func _on_body_entered(_body: Node2D) -> void:
	if _prompt:
		_prompt.visible = true


func _on_body_exited(_body: Node2D) -> void:
	if _prompt:
		_prompt.visible = false
