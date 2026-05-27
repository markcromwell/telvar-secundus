extends Node
## Minimal dialogue + story flags for Veneficturis scenes (Godot 4.3).

const DIALOGUE_GROUP := "dialogue_ui_root"

var flags: Dictionary = {}

var _layer: CanvasLayer
var _panel: PanelContainer
var _name_label: Label
var _text_label: Label
var _next_button: Button
var _queue: Array = []
var _queue_index: int = 0
var _on_closed: Callable = Callable()


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	_build_ui()


func set_flag(key: StringName, value: Variant) -> void:
	flags[key] = value


func get_flag(key: StringName, default_value: Variant = null) -> Variant:
	return flags[key] if flags.has(key) else default_value


func show_message(text: String, speaker: String = "Narrator", on_closed: Callable = Callable()) -> void:
	_on_closed = on_closed
	_queue = [{"speaker": speaker, "text": text}]
	_queue_index = 0
	_show_panel()


## Loads JSON from [param dialogue_path], walks [param start_id] via "next" links.
func show_dialogue(_npc_id: String, dialogue_path: String, start_id: String = "start") -> void:
	_on_closed = Callable()
	var raw := FileAccess.get_file_as_string(dialogue_path)
	if raw.is_empty() and not FileAccess.file_exists(dialogue_path):
		push_error("DialogueManager: missing file %s" % dialogue_path)
		return
	var parsed: Variant = JSON.parse_string(raw)
	if typeof(parsed) != TYPE_ARRAY:
		push_error("DialogueManager: dialogue root must be an array")
		return
	var by_id: Dictionary = {}
	for item in parsed:
		if typeof(item) != TYPE_DICTIONARY:
			continue
		var d: Dictionary = item
		if d.has("id"):
			by_id[String(d["id"])] = d
	_queue = _linearize(by_id, start_id)
	_queue_index = 0
	if _queue.is_empty():
		push_error("DialogueManager: no entries from %s" % start_id)
		return
	_show_panel()


func _linearize(by_id: Dictionary, start_id: String) -> Array:
	var out: Array = []
	var cur := start_id
	var guard := 0
	while cur != "" and by_id.has(cur) and guard < 64:
		var entry: Dictionary = by_id[cur]
		out.append(entry)
		var nxt: Variant = entry.get("next", "")
		cur = String(nxt) if nxt != null else ""
		guard += 1
	return out


func _build_ui() -> void:
	_layer = CanvasLayer.new()
	_layer.layer = 120
	add_child(_layer)
	var root := Control.new()
	root.set_anchors_preset(Control.PRESET_FULL_RECT)
	root.add_to_group(DIALOGUE_GROUP)
	_layer.add_child(root)
	_panel = PanelContainer.new()
	_panel.visible = false
	_panel.set_anchors_preset(Control.PRESET_CENTER)
	_panel.offset_left = -420.0
	_panel.offset_top = -160.0
	_panel.offset_right = 420.0
	_panel.offset_bottom = 160.0
	root.add_child(_panel)
	var vbox := VBoxContainer.new()
	_panel.add_child(vbox)
	_name_label = Label.new()
	_name_label.add_theme_font_size_override("font_size", 18)
	vbox.add_child(_name_label)
	_text_label = Label.new()
	_text_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_text_label.custom_minimum_size = Vector2(780, 0)
	_text_label.add_theme_font_size_override("font_size", 16)
	vbox.add_child(_text_label)
	_next_button = Button.new()
	_next_button.text = "Continue"
	_next_button.focus_mode = Control.FOCUS_ALL
	vbox.add_child(_next_button)
	_next_button.pressed.connect(_on_next_pressed)


func _show_panel() -> void:
	_panel.visible = true
	_refresh_line()
	get_tree().paused = true


func _refresh_line() -> void:
	if _queue_index >= _queue.size():
		_close_panel()
		return
	var entry: Dictionary = _queue[_queue_index]
	_name_label.text = String(entry.get("speaker", ""))
	_text_label.text = String(entry.get("text", ""))
	var has_next := _queue_index < _queue.size() - 1
	_next_button.text = "Continue" if has_next else "Close"


func _on_next_pressed() -> void:
	_queue_index += 1
	if _queue_index >= _queue.size():
		_close_panel()
	else:
		_refresh_line()


func _close_panel() -> void:
	_panel.visible = false
	_queue.clear()
	_queue_index = 0
	if get_tree() != null:
		get_tree().paused = false
	var cb := _on_closed
	_on_closed = Callable()
	if cb.is_valid():
		cb.call()
