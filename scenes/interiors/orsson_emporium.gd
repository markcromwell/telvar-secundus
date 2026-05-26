extends Node2D

## Wires NPC `InteractionZone` Area2D nodes and the south `ExitDoor` Area2D.
## Expects child nodes: Sabatha, Orsson (instances of `scenes/npcs/*.tscn`), ExitDoor.


func _ready() -> void:
	_wire_npc_dialogue("Sabatha")
	_wire_npc_dialogue("Orsson")
	var exit_door := get_node_or_null("ExitDoor")
	if exit_door is Area2D:
		var area := exit_door as Area2D
		area.body_entered.connect(_on_exit_door_body_entered)


func _wire_npc_dialogue(npc_path: String) -> void:
	var npc := get_node_or_null(npc_path)
	if npc == null:
		return
	var zone := npc.get_node_or_null("InteractionZone")
	if not (zone is Area2D):
		return
	var raw_id: Variant = npc.get("dialogue_id")
	var dialogue_id: String = str(raw_id) if raw_id != null else ""
	if dialogue_id.is_empty():
		return
	var area := zone as Area2D
	area.body_entered.connect(_on_npc_zone_body_entered.bind(dialogue_id))


func _on_npc_zone_body_entered(body: Node2D, dialogue_id: String) -> void:
	if not _is_player_like_body(body):
		return
	DialogueManager.show_dialogue(dialogue_id)


func _on_exit_door_body_entered(body: Node2D) -> void:
	if not _is_player_like_body(body):
		return
	SceneTransition.fade_to("res://scenes/overworld/secundus.tscn", "orsson_emporium_entrance")


func _is_player_like_body(body: Node) -> bool:
	return body is CharacterBody2D or body is RigidBody2D
