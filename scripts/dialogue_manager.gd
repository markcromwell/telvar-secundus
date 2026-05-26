extends Node
## Loads `assets/dialogue/{npc_id}.json` arrays and drives DialogueBox.
## Handles `next`, `choices`, and `outcome` keys used by Myramar confront flow.

const DIALOGUE_BOX_SCENE := preload("res://scenes/dialogue_box.tscn")
const GAME_OVER_SCENE := "res://scenes/game_over.tscn"
const WINGS_SCENE := "res://scenes/wings.tscn"

const FLAG_RESOLVED := "myramar_evidence_branch_resolved"

var _flags: Dictionary = {}
var _nodes_by_id: Dictionary = {}
var _current_node: Dictionary = {}
var _dialogue_layer: CanvasLayer
var _box: DialogueBox


func get_flag(key: String, default: Variant = false) -> Variant:
	return _flags.get(key, default)


func set_flag(key: String, value: Variant) -> void:
	_flags[key] = value


## If [param start_or_json] is a [String], it is the starting node id after loading
## `res://assets/dialogue/{npc_id}.json`. If it is an [Array], it is used as the tree
## (tests / tooling) and the third parameter must be the start id.
func show_dialogue(npc_id: String, start_or_json: Variant = "start", start_id_if_array: String = "start") -> void:
	_clear_dialogue_ui()
	var tree: Array = []
	var start_id := ""

	if typeof(start_or_json) == TYPE_ARRAY:
		tree = start_or_json as Array
		start_id = start_id_if_array
	else:
		start_id = str(start_or_json)
		var path := "res://assets/dialogue/%s.json" % npc_id
		if not FileAccess.file_exists(path):
			push_error("DialogueManager: missing dialogue file: %s" % path)
			return
		var raw := FileAccess.get_file_as_string(path)
		var parsed: Variant = JSON.parse_string(raw)
		if typeof(parsed) != TYPE_ARRAY:
			push_error("DialogueManager: dialogue root must be a JSON array: %s" % path)
			return
		tree = parsed as Array

	_build_index(tree)
	if not _nodes_by_id.has(start_id):
		push_error("DialogueManager: unknown start id: %s" % start_id)
		return

	_dialogue_layer = CanvasLayer.new()
	_dialogue_layer.layer = 100
	get_tree().root.add_child(_dialogue_layer)

	_box = DIALOGUE_BOX_SCENE.instantiate() as DialogueBox
	_dialogue_layer.add_child(_box)

	_box.continue_pressed.connect(_on_continue_pressed)
	_box.choice_pressed.connect(_on_choice_pressed)

	_show_node(start_id)


func _build_index(tree: Array) -> void:
	_nodes_by_id.clear()
	for item in tree:
		if typeof(item) != TYPE_DICTIONARY:
			continue
		var d := item as Dictionary
		if not d.has("id"):
			continue
		_nodes_by_id[str(d["id"])] = d


func _show_node(node_id: String) -> void:
	var node: Variant = _nodes_by_id.get(node_id)
	if typeof(node) != TYPE_DICTIONARY:
		push_error("DialogueManager: missing node: %s" % node_id)
		_clear_dialogue_ui()
		return
	_current_node = node as Dictionary
	if _box:
		_box.present_node(_current_node)


func _on_choice_pressed(next_id: String) -> void:
	_show_node(next_id)


func _on_continue_pressed() -> void:
	if _current_node.has("outcome"):
		_apply_outcome(str(_current_node["outcome"]))
		return
	if _current_node.has("next"):
		_show_node(str(_current_node["next"]))
		return
	_clear_dialogue_ui()


func _apply_outcome(outcome: String) -> void:
	match outcome:
		"game_over_save_prompt":
			set_flag(FLAG_RESOLVED, true)
			_clear_dialogue_ui()
			get_tree().change_scene_to_file(GAME_OVER_SCENE)
		"transition_wings":
			set_flag(FLAG_RESOLVED, true)
			_clear_dialogue_ui()
			get_tree().change_scene_to_file(WINGS_SCENE)
		_:
			push_warning("DialogueManager: unknown outcome: %s" % outcome)
			_clear_dialogue_ui()


func _clear_dialogue_ui() -> void:
	if is_instance_valid(_dialogue_layer):
		_dialogue_layer.queue_free()
	_dialogue_layer = null
	_box = null
	_current_node = {}
