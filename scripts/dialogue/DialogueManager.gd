extends Node

## Autoload singleton: present dialogue UI, track story flags.
signal dialogue_started(npc_id: String)

const BOX_SCENE := preload("res://scenes/ui/DialogueBox.tscn")

var _flags: Dictionary = {}

var _canvas: CanvasLayer
var _active_box: Control
var _by_id: Dictionary = {}
var _current_id: String = ""

func _ready() -> void:
	_canvas = CanvasLayer.new()
	_canvas.layer = 128
	add_child(_canvas)


func set_flag(key: String, value: Variant) -> void:
	_flags[key] = value


func get_flag(key: String) -> Variant:
	return _flags.get(key, null)


func show_dialogue(npc_id: String, dialogue_json: Variant) -> void:
	if typeof(dialogue_json) != TYPE_ARRAY:
		push_error("DialogueManager.show_dialogue: dialogue_json must be an Array")
		return
	_close_active()
	dialogue_started.emit(npc_id)
	_by_id.clear()
	for item in dialogue_json:
		if typeof(item) != TYPE_DICTIONARY:
			continue
		var d: Dictionary = item
		var entry_id := str(d.get("id", ""))
		if entry_id.is_empty():
			continue
		_by_id[entry_id] = d
	if not _by_id.has("start"):
		push_error("DialogueManager.show_dialogue: missing entry with id 'start'")
		return
	_current_id = "start"
	var box: Control = BOX_SCENE.instantiate()
	_canvas.add_child(box)
	_active_box = box
	_render_step()


func _close_active() -> void:
	if _active_box != null and is_instance_valid(_active_box):
		_active_box.queue_free()
	_active_box = null
	_by_id.clear()
	_current_id = ""


func _render_step() -> void:
	if _active_box == null or not is_instance_valid(_active_box):
		return
	var entry: Dictionary = _by_id.get(_current_id, {})
	var vbox: VBoxContainer = _active_box.get_node("VBoxContainer") as VBoxContainer
	var name_l: Label = vbox.get_node("NameLabel") as Label
	var text_l: Label = vbox.get_node("TextLabel") as Label
	var choices_c: VBoxContainer = vbox.get_node("ChoicesContainer") as VBoxContainer
	for c in choices_c.get_children():
		c.queue_free()
	name_l.text = str(entry.get("speaker", ""))
	text_l.text = str(entry.get("text", ""))
	var raw_choices = entry.get("choices")
	if raw_choices is Array:
		for ch in raw_choices:
			if typeof(ch) != TYPE_DICTIONARY:
				continue
			var cd: Dictionary = ch
			var label := str(cd.get("text", "..."))
			var nxt := str(cd.get("next", ""))
			var btn := Button.new()
			btn.text = label
			btn.pressed.connect(_on_choice_pressed.bind(nxt))
			choices_c.add_child(btn)
	else:
		var next_id := str(entry.get("next", ""))
		var btn := Button.new()
		if next_id.is_empty():
			btn.text = "Close"
			btn.pressed.connect(_on_choice_pressed.bind(""))
		else:
			btn.text = "Continue"
			btn.pressed.connect(_on_choice_pressed.bind(next_id))
		choices_c.add_child(btn)


func _on_choice_pressed(next_id: String) -> void:
	if next_id.is_empty():
		_close_active()
		return
	if not _by_id.has(next_id):
		_close_active()
		return
	_current_id = next_id
	_render_step()
