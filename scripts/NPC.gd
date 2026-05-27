extends StaticBody2D

@export var dialogue_id: String = ""

@onready var _interaction_zone: Area2D = $InteractionZone
@onready var _prompt: Label = $InteractPrompt

var _bodies_in_zone: int = 0


func _ready() -> void:
	_interaction_zone.body_entered.connect(_on_interaction_zone_body_entered)
	_interaction_zone.body_exited.connect(_on_interaction_zone_body_exited)
	_prompt.visible = false


func _on_interaction_zone_body_entered(_body: Node2D) -> void:
	_bodies_in_zone += 1
	_prompt.visible = _bodies_in_zone > 0


func _on_interaction_zone_body_exited(_body: Node2D) -> void:
	_bodies_in_zone = maxi(_bodies_in_zone - 1, 0)
	_prompt.visible = _bodies_in_zone > 0


func _process(_delta: float) -> void:
	if _bodies_in_zone <= 0:
		return
	if dialogue_id.is_empty():
		return
	if not Input.is_action_just_pressed("ui_accept"):
		return
	var json_path := "res://assets/dialogue/%s.json" % dialogue_id
	DialogueManager.show_dialogue(dialogue_id, json_path)
