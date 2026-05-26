extends Node

## Autoload: dialogue state, flags, and choice-time script hooks (quest HUD, etc.).

var _flags: Dictionary = {}

var _dialogue_nodes: Dictionary = {}  # id -> Dictionary
var _active_node_id: String = ""

signal dialogue_started(npc_id: String)
signal shop_open_requested()
signal lore_unlock_requested(lore_key: String)

var _hud_layer: CanvasLayer
var _hud_label: Label
var _hud_timer: Timer

var _flag_regex: RegEx


func _ready() -> void:
	_flag_regex = RegEx.new()
	_flag_regex.compile(
		"\\[(quest_give|quest_complete|shop_open|lore_unlock)(?::([^\\]]+))?\\]"
	)
	_setup_hud()


func _setup_hud() -> void:
	_hud_layer = CanvasLayer.new()
	_hud_layer.layer = 100
	add_child(_hud_layer)
	var root := Control.new()
	root.set_anchors_preset(Control.PRESET_FULL_RECT)
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_hud_layer.add_child(root)
	_hud_label = Label.new()
	_hud_label.text = "New Quest!"
	_hud_label.visible = false
	_hud_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_hud_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_hud_label.anchor_left = 0.5
	_hud_label.anchor_right = 0.5
	_hud_label.anchor_top = 0.0
	_hud_label.offset_left = -240.0
	_hud_label.offset_right = 240.0
	_hud_label.offset_top = 12.0
	_hud_label.offset_bottom = 52.0
	_hud_label.add_theme_font_size_override("font_size", 28)
	root.add_child(_hud_label)
	_hud_timer = Timer.new()
	_hud_timer.one_shot = true
	_hud_timer.wait_time = 2.0
	_hud_timer.timeout.connect(_hide_hud_notification)
	add_child(_hud_timer)


func _hide_hud_notification() -> void:
	_hud_label.visible = false


func set_flag(key: String, value: Variant) -> void:
	_flags[key] = value


func get_flag(key: String) -> Variant:
	return _flags.get(key, null)


func show_dialogue(npc_id: String, dialogue_json: Variant) -> void:
	var arr: Array = _coerce_dialogue_array(dialogue_json)
	_dialogue_nodes.clear()
	for item in arr:
		if typeof(item) != TYPE_DICTIONARY:
			continue
		var node: Dictionary = item
		var nid := str(node.get("id", ""))
		if nid.is_empty():
			continue
		_dialogue_nodes[nid] = node
	_active_node_id = _pick_start_node_id(arr)
	dialogue_started.emit(npc_id)


func select_choice_index(choice_index: int) -> void:
	if _active_node_id.is_empty():
		return
	if not _dialogue_nodes.has(_active_node_id):
		return
	var node: Dictionary = _dialogue_nodes[_active_node_id]
	var choices: Array = node.get("choices", [])
	if choice_index < 0 or choice_index >= choices.size():
		return
	if typeof(choices[choice_index]) != TYPE_DICTIONARY:
		return
	var choice: Dictionary = choices[choice_index]
	_process_choice_effects(choice)
	var next_id := str(choice.get("next", ""))
	if next_id.is_empty() or not _dialogue_nodes.has(next_id):
		_active_node_id = ""
	else:
		_active_node_id = next_id


func _process_choice_effects(choice: Dictionary) -> void:
	var blob_parts: Array[String] = []
	if choice.has("flags") and typeof(choice.get("flags")) == TYPE_ARRAY:
		for f in choice.get("flags", []):
			blob_parts.append(str(f))
	blob_parts.append(str(choice.get("text", "")))
	var combined := ""
	for i in blob_parts.size():
		if i > 0:
			combined += " "
		combined += blob_parts[i]
	_run_flag_tokens(combined)


func _run_flag_tokens(blob: String) -> void:
	var results := _flag_regex.search_all(blob)
	for m in results:
		var kind := m.get_string(1)
		var payload := m.get_string(2)
		match kind:
			"quest_give":
				var qid := payload.strip_edges()
				if qid.is_empty():
					push_warning("DialogueManager: [quest_give] needs :quest_id after the tag")
					continue
				QuestManager.start_quest(qid)
				_show_hud_notification("New Quest!")
			"quest_complete":
				var parts := payload.split(":", true, 1)
				if parts.size() < 2:
					push_warning(
						"DialogueManager: [quest_complete] needs :quest_id:objective_id payload"
					)
					continue
				QuestManager.complete_objective(parts[0].strip_edges(), parts[1].strip_edges())
			"shop_open":
				shop_open_requested.emit()
			"lore_unlock":
				lore_unlock_requested.emit(payload.strip_edges())


func _show_hud_notification(message: String) -> void:
	_hud_label.text = message
	_hud_label.visible = true
	_hud_timer.stop()
	_hud_timer.start()


func _coerce_dialogue_array(dialogue_json: Variant) -> Array:
	if typeof(dialogue_json) == TYPE_ARRAY:
		return dialogue_json.duplicate(true)
	if typeof(dialogue_json) == TYPE_STRING:
		var json := JSON.new()
		var err := json.parse(str(dialogue_json))
		if err != OK:
			push_error("DialogueManager: invalid dialogue JSON string")
			return []
		var data = json.get_data()
		if typeof(data) != TYPE_ARRAY:
			push_error("DialogueManager: dialogue JSON root must be an array")
			return []
		return data
	push_error("DialogueManager: dialogue_json must be Array or JSON string")
	return []


func _pick_start_node_id(arr: Array) -> String:
	for item in arr:
		if typeof(item) != TYPE_DICTIONARY:
			continue
		var nid := str(item.get("id", ""))
		if nid == "start":
			return "start"
	for item in arr:
		if typeof(item) != TYPE_DICTIONARY:
			continue
		var nid := str(item.get("id", ""))
		if not nid.is_empty():
			return nid
	return ""
