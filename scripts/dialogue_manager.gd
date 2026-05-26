extends Node
## Minimal dialogue + flag autoload for JSON trees (array of objects with id/text/next).
## Advances on ui_accept while active. Awards inventory on entering the award node id.

const SEALED_WING_KEY_ITEM_ID := "sealed_wing_key"
const AWARD_NODE_ID := "award_sealed_wing_key"

var _flags: Dictionary = {}

var _dialogue_active := false
var _npc_id: String = ""
var _nodes: Array = []
var _current: Dictionary = {}

signal dialogue_started(npc_id: String)
signal dialogue_line(npc_id: String, line: Dictionary)
signal dialogue_finished(npc_id: String)


func get_flag(key: String, default_value = null):
	return _flags.get(key, default_value)


func set_flag(key: String, value) -> void:
	_flags[key] = value


func is_dialogue_active() -> bool:
	return _dialogue_active


func show_dialogue(npc_id: String, dialogue_data: Variant) -> void:
	_nodes = _coerce_dialogue(dialogue_data)
	if _nodes.is_empty():
		return
	_dialogue_active = true
	_npc_id = npc_id
	_current = _find_node_by_id("start")
	if _current.is_empty():
		_end_dialogue()
		return
	dialogue_started.emit(npc_id)
	_apply_node_enter_effects()
	dialogue_line.emit(npc_id, _current.duplicate())


func _unhandled_input(event: InputEvent) -> void:
	if not _dialogue_active:
		return
	if event.is_action_pressed("ui_accept"):
		get_viewport().set_input_as_handled()
		_advance()


func _advance() -> void:
	var next_id = _current.get("next")
	if next_id == null or str(next_id).is_empty():
		_end_dialogue()
		return
	_current = _find_node_by_id(str(next_id))
	if _current.is_empty():
		_end_dialogue()
		return
	_apply_node_enter_effects()
	dialogue_line.emit(_npc_id, _current.duplicate())


func _end_dialogue() -> void:
	var ended_npc := _npc_id
	_dialogue_active = false
	_current = {}
	_nodes.clear()
	dialogue_finished.emit(ended_npc)


func _apply_node_enter_effects() -> void:
	var id := str(_current.get("id", ""))
	if id == AWARD_NODE_ID:
		InventoryManager.add_item(SEALED_WING_KEY_ITEM_ID)


func _find_node_by_id(node_id: String) -> Dictionary:
	for n in _nodes:
		if typeof(n) == TYPE_DICTIONARY and str(n.get("id", "")) == node_id:
			return n
	return {}


func _coerce_dialogue(dialogue_data: Variant) -> Array:
	if dialogue_data is String:
		var path := str(dialogue_data)
		if not FileAccess.file_exists(path):
			return []
		var f := FileAccess.open(path, FileAccess.READ)
		if f == null:
			return []
		var parsed = JSON.parse_string(f.get_as_text())
		return parsed if typeof(parsed) == TYPE_ARRAY else []
	if dialogue_data is Array:
		return dialogue_data
	return []
