extends Area2D

## Triggers a scene change when a CharacterBody2D enters the door volume.
@export var target_scene: String = ""


func _ready() -> void:
	body_entered.connect(_on_body_entered)


func _on_body_entered(body: Node) -> void:
	if not (body is CharacterBody2D):
		return
	if target_scene.is_empty():
		return
	get_tree().change_scene_to_file(target_scene)
