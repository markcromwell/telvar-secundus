extends Node

## Autoload: dialogue tree lookup, global story flags, and DialogueBox UI.

var _flags: Dictionary = {}
var _active_npc_id: String = ""
var _nodes_by_id: Dictionary = {}
var _current_node: Dictionary = {}
var _dialogue_box: Node = null


func set_flag(key: String, value) -> void:
	_flags[key] = value


func get_flag(key: String):
	return _flags.get(key)


func show_dialogue(npc_id: String, dialogue_json) -> void:
	_active_npc_id = npc_id
	_nodes_by_id.clear()
	_current_node = {}

	var nodes = dialogue_json
	if nodes is String:
		var parsed = JSON.parse_string(nodes)
		if parsed != null:
			nodes = parsed

	if nodes is Array:
		for item in nodes:
			if item is Dictionary and item.has("id"):
				_nodes_by_id[str(item["id"])] = item

	var start_id := "start"
	if _nodes_by_id.has(start_id):
		_current_node = _nodes_by_id[start_id]

	if _dialogue_box != null and is_instance_valid(_dialogue_box):
		_dialogue_box.queue_free()
		_dialogue_box = null

	var dialogue_scene: PackedScene = load("res://scenes/DialogueBox.tscn") as PackedScene
	if dialogue_scene == null:
		push_error("DialogueManager: failed to load res://scenes/DialogueBox.tscn")
		return

	var box: Node = dialogue_scene.instantiate()
	_dialogue_box = box
	get_tree().root.add_child(box)

	var speaker := str(_current_node.get("speaker", ""))
	var line := str(_current_node.get("text", ""))
	var choices: Array = []
	if _current_node.get("choices") is Array:
		choices = _current_node["choices"] as Array

	if box.has_method("populate"):
		box.call("populate", speaker, line, choices)
