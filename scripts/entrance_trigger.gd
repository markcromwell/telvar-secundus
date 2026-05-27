class_name EntranceTrigger
extends Area2D

## Path to the interior scene (res://...) shown in the inspector.
@export var target_scene: String = ""
## Spawn marker id consumed by interior/transition wiring in sibling phases.
@export var spawn_point_id: String = ""


func _ready() -> void:
	body_entered.connect(_on_body_entered)
	body_exited.connect(_on_body_exited)


func _on_body_entered(body: Node2D) -> void:
	if not body.is_in_group("player"):
		return
	if body.has_method("set_current_entrance"):
		body.set_current_entrance(self)


func _on_body_exited(body: Node2D) -> void:
	if not body.is_in_group("player"):
		return
	if body.has_method("clear_current_entrance"):
		body.clear_current_entrance(self)
