extends Area2D

## Area2D placed at interior exits. When the player enters, fades out, loads the
## stored overworld scene, restores `TransitionManager.return_position`, then fades in.

var _transitioning: bool = false


func _ready() -> void:
	body_entered.connect(_on_body_entered)


func _on_body_entered(body: Node2D) -> void:
	if _transitioning:
		return
	if not body.is_in_group("player"):
		return
	if not ("can_move" in body):
		return

	_transitioning = true
	body.can_move = false

	# Survive `change_scene` so we can re-enable movement after the overworld fade-in.
	var tree := get_tree()
	reparent(tree.root)

	await TransitionManager.return_to_overworld()

	var player := tree.get_first_node_in_group("player")
	if player and "can_move" in player:
		player.can_move = true

	_transitioning = false
	queue_free()
