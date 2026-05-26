extends Node

## Autoload: dialogue tree lookup and global story flags.
## DialogueBox wiring consumes resolved nodes in a later phase.

var _flags: Dictionary = {}
var _active_npc_id: String = ""
var _nodes_by_id: Dictionary = {}
var _current_node: Dictionary = {}


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
