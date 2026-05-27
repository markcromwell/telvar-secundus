extends Node2D


func _ready() -> void:
	_wire_npc("Sabatha")
	_wire_npc("Orsson")
	var exit_door := get_node_or_null("ExitDoor") as Area2D
	if exit_door:
		exit_door.body_entered.connect(_on_exit_body_entered)


func _wire_npc(npc_name: StringName) -> void:
	var npc := get_node_or_null(NodePath(String(npc_name)))
	if npc == null:
		return
	var zone := npc.get_node_or_null("InteractionZone") as Area2D
	if zone == null:
		return
	zone.body_entered.connect(_on_npc_zone_entered.bind(npc))


func _on_npc_zone_entered(body: Node2D, npc: Node) -> void:
	if not body.is_in_group("player"):
		return
	var key := str(npc.get("dialogue_id", ""))
	if key.is_empty():
		return
	DialogueManager.show_dialogue(key)


func _on_exit_body_entered(body: Node2D) -> void:
	if not body.is_in_group("player"):
		return
	SceneTransition.fade_to("res://scenes/overworld/secundus.tscn", "orsson_emporium_entrance")
