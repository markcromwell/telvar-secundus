extends Node
## Autoload: dialogue from JSON arrays (see assets/dialogue/*.json).

signal dialogue_closed(npc_id: String)

const CHOICE_FONT_SIZE := 16

var _flags: Dictionary = {}
var _layer: CanvasLayer
var _panel: PanelContainer
var _name_label: Label
var _text_label: Label
var _choices_container: VBoxContainer
var _continue_button: Button
var _npc_id: String = ""
var _nodes_by_id: Dictionary = {}
var _current: Dictionary = {}


func set_flag(key: String, value: Variant) -> void:
	_flags[key] = value


func get_flag(key: String, default: Variant = null) -> Variant:
	return _flags.get(key, default)


func is_dialogue_open() -> bool:
	return _npc_id != ""


func show_dialogue(npc_id: String, dialogue_json: Variant) -> void:
	_npc_id = npc_id
	_nodes_by_id.clear()
	var arr: Array = _coerce_dialogue_array(dialogue_json)
	for item in arr:
		if typeof(item) != TYPE_DICTIONARY:
			continue
		var d: Dictionary = item
		if d.has("id"):
			_nodes_by_id[str(d["id"])] = d
	_ensure_ui()
	_show_node(_nodes_by_id.get("start", {}))


func _coerce_dialogue_array(dialogue_json: Variant) -> Array:
	if typeof(dialogue_json) == TYPE_ARRAY:
		return dialogue_json
	if typeof(dialogue_json) == TYPE_STRING:
		var path := str(dialogue_json)
		if not FileAccess.file_exists(path):
			push_error("DialogueManager: missing file %s" % path)
			return []
		var raw := FileAccess.get_file_as_string(path)
		var parsed = JSON.parse_string(raw)
		if typeof(parsed) != TYPE_ARRAY:
			push_error("DialogueManager: JSON root must be an array in %s" % path)
			return []
		return parsed
	push_error("DialogueManager: dialogue_json must be Array or path String")
	return []


func _ensure_ui() -> void:
	if is_instance_valid(_layer):
		return
	_layer = CanvasLayer.new()
	_layer.layer = 50
	add_child(_layer)
	_panel = PanelContainer.new()
	_panel.set_anchors_preset(Control.PRESET_CENTER)
	_panel.offset_left = -320.0
	_panel.offset_top = -180.0
	_panel.offset_right = 320.0
	_panel.offset_bottom = 180.0
	_layer.add_child(_panel)
	var outer := VBoxContainer.new()
	_panel.add_child(outer)
	_name_label = Label.new()
	_name_label.add_theme_font_size_override("font_size", 18)
	outer.add_child(_name_label)
	_text_label = Label.new()
	_text_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_text_label.custom_minimum_size = Vector2(560, 120)
	_text_label.size_flags_vertical = Control.SIZE_EXPAND_FILL
	outer.add_child(_text_label)
	_choices_container = VBoxContainer.new()
	outer.add_child(_choices_container)
	_continue_button = Button.new()
	_continue_button.text = "Continue"
	_continue_button.pressed.connect(_on_continue_pressed)
	outer.add_child(_continue_button)
	_layer.visible = false


func _show_node(node: Dictionary) -> void:
	if node.is_empty():
		_close_dialogue()
		return
	_apply_node_flags(node)
	_current = node
	_layer.visible = true
	_name_label.text = str(node.get("speaker", ""))
	_text_label.text = str(node.get("text", ""))
	for c in _choices_container.get_children():
		_choices_container.remove_child(c)
		c.queue_free()
	_continue_button.visible = false
	if node.has("choices") and typeof(node["choices"]) == TYPE_ARRAY:
		var choices: Array = node["choices"]
		for ch in choices:
			if typeof(ch) != TYPE_DICTIONARY:
				continue
			var cd: Dictionary = ch
			var btn := Button.new()
			btn.text = str(cd.get("text", "?"))
			btn.add_theme_font_size_override("font_size", CHOICE_FONT_SIZE)
			var nxt := str(cd.get("next", ""))
			btn.pressed.connect(func(): _show_node(_nodes_by_id.get(nxt, {})))
			_choices_container.add_child(btn)
	elif node.get("end", false) == true:
		_continue_button.visible = true
	elif node.has("next"):
		_continue_button.visible = true
	else:
		_continue_button.visible = true


func _apply_node_flags(node: Dictionary) -> void:
	if not node.has("set_flag"):
		return
	var sf = node["set_flag"]
	if typeof(sf) != TYPE_DICTIONARY:
		return
	for k in sf.keys():
		set_flag(str(k), sf[k])


func _on_continue_pressed() -> void:
	if _current.get("end", false) == true:
		_close_dialogue()
		return
	if _current.has("next"):
		var nxt := str(_current["next"])
		_show_node(_nodes_by_id.get(nxt, {}))
	else:
		_close_dialogue()


func _close_dialogue() -> void:
	if is_instance_valid(_layer):
		_layer.visible = false
	var id := _npc_id
	_npc_id = ""
	dialogue_closed.emit(id)
