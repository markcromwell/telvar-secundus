extends Area2D


func _ready() -> void:
	body_entered.connect(_on_body_entered)


func _on_body_entered(body: Node2D) -> void:
	if body == null:
		return
	if body is CharacterBody2D or body.is_in_group("player"):
		LoreManager.show("order_lore")
