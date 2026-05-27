extends Node

const UI_LAYER_NAME := "_DialogueManagerLayer"

var _flags: Dictionary = {}

var _nodes: Dictionary = {}
var _current_id: String = ""
var _npc_id: String = ""
var _active: bool = false

var _layer: CanvasLayer
var _name_label: Label
var _text_label: Label
var _choices_container: VBoxContainer


func _ready() -> void:
	set_process_unhandled_input(false)


func set_flag(key: String, value: Variant) -> void:
	if key.is_empty():
		return
	_flags[key] = value


func get_flag(key: String) -> Variant:
	return _flags.get(key, null)


func show_dialogue(npc_id: String, dialogue_json: Array) -> void:
	_npc_id = npc_id
	_nodes.clear()
	for item in dialogue_json:
		if item is Dictionary and (item as Dictionary).has("id"):
			var d: Dictionary = item as Dictionary
			_nodes[str(d["id"])] = d
	if _nodes.is_empty():
		push_warning("DialogueManager.show_dialogue: empty or invalid dialogue_json for npc '%s'" % npc_id)
		return
	if _nodes.has("start"):
		_current_id = "start"
	else:
		var first: Dictionary = dialogue_json[0] as Dictionary
		_current_id = str(first["id"])
	_ensure_ui()
	_layer.show()
	_active = true
	set_process_unhandled_input(true)
	_refresh_ui()


func _ensure_ui() -> void:
	if _layer and is_instance_valid(_layer):
		return
	_layer = CanvasLayer.new()
	_layer.name = UI_LAYER_NAME
	_layer.layer = 120
	get_tree().root.add_child(_layer)

	var panel := PanelContainer.new()
	panel.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	panel.offset_top = -180.0
	panel.offset_bottom = 0.0
	panel.offset_left = 40.0
	panel.offset_right = -40.0
	_layer.add_child(panel)

	var outer := MarginContainer.new()
	outer.add_theme_constant_override("margin_left", 12)
	outer.add_theme_constant_override("margin_right", 12)
	outer.add_theme_constant_override("margin_top", 8)
	outer.add_theme_constant_override("margin_bottom", 8)
	panel.add_child(outer)

	var vbox := VBoxContainer.new()
	outer.add_child(vbox)

	_name_label = Label.new()
	_name_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	vbox.add_child(_name_label)

	_text_label = Label.new()
	_text_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	vbox.add_child(_text_label)

	_choices_container = VBoxContainer.new()
	vbox.add_child(_choices_container)


func _refresh_ui() -> void:
	if not _layer or not is_instance_valid(_layer):
		return
	var node: Dictionary = _nodes.get(_current_id, {}) as Dictionary
	var speaker := str(node.get("speaker", _npc_id))
	var text := str(node.get("text", ""))
	_name_label.text = speaker
	_text_label.text = text
	for c in _choices_container.get_children():
		c.queue_free()
	if node.has("choices") and node["choices"] is Array:
		var idx := 0
		for ch in node["choices"] as Array:
			if ch is Dictionary:
				var btn := Button.new()
				btn.text = str((ch as Dictionary).get("text", "..."))
				btn.pressed.connect(_on_choice_pressed.bind(idx))
				_choices_container.add_child(btn)
			idx += 1


func _on_choice_pressed(choice_index: int) -> void:
	var node: Dictionary = _nodes.get(_current_id, {}) as Dictionary
	var choices: Array = node.get("choices", []) as Array
	if choice_index < 0 or choice_index >= choices.size():
		return
	var choice: Dictionary = choices[choice_index] as Dictionary
	var nxt: Variant = choice.get("next")
	_apply_exit_actions(node)
	if nxt == null:
		_close_dialogue()
	else:
		_current_id = str(nxt)
		_refresh_ui()


func _unhandled_input(event: InputEvent) -> void:
	if not _active:
		return
	if event.is_action_pressed("ui_accept"):
		var node: Dictionary = _nodes.get(_current_id, {}) as Dictionary
		if node.has("choices") and node["choices"] is Array and (node["choices"] as Array).size() > 0:
			return
		_advance_linear()


func _advance_linear() -> void:
	var node: Dictionary = _nodes.get(_current_id, {}) as Dictionary
	var nxt: Variant = node.get("next")
	if nxt == null:
		_apply_exit_actions(node)
		_close_dialogue()
		return
	_apply_exit_actions(node)
	_current_id = str(nxt)
	_refresh_ui()


func _apply_exit_actions(node: Dictionary) -> void:
	if str(node.get("action", "")) == "assign_quest":
		var qid := str(node.get("quest_id", ""))
		if not qid.is_empty():
			QuestManager.assign_quest(qid)


func _close_dialogue() -> void:
	_active = false
	set_process_unhandled_input(false)
	if _layer and is_instance_valid(_layer):
		_layer.hide()
	_name_label.text = ""
	_text_label.text = ""
	for c in _choices_container.get_children():
		c.queue_free()
	_nodes.clear()
	_current_id = ""
	_npc_id = ""
