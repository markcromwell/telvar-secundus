extends Node

## Autoload: dialogue UI, flags, and input advance (ui_accept).

const DIALOGUE_BOX_SCENE := preload("res://scenes/DialogueBox.tscn")

var _flags: Dictionary = {}
var _dialogue_layer: CanvasLayer = null
var _dialogue_box: Control = null
var _npc_id: String = ""
var _dialogue_rows: Array = []
var _current_id: String = ""
var _awaiting_choice: bool = false


func set_flag(key: String, value: Variant) -> void:
	_flags[key] = value


func get_flag(key: String) -> Variant:
	return _flags.get(key, null)


func show_dialogue(npc_id: String, dialogue_json: Array) -> void:
	_end_dialogue_immediate()
	_npc_id = npc_id
	_dialogue_rows = dialogue_json.duplicate(true)
	_current_id = _resolve_start_id()

	_dialogue_layer = CanvasLayer.new()
	_dialogue_layer.layer = 100
	get_tree().root.add_child(_dialogue_layer)

	_dialogue_box = DIALOGUE_BOX_SCENE.instantiate() as Control
	_dialogue_layer.add_child(_dialogue_box)
	_refresh_display()


func _process(_delta: float) -> void:
	if _dialogue_box == null or _awaiting_choice:
		return
	if Input.is_action_just_pressed("ui_accept"):
		_advance_linear()


func _resolve_start_id() -> String:
	for row in _dialogue_rows:
		if row is Dictionary and str(row.get("id", "")) == "start":
			return "start"
	if not _dialogue_rows.is_empty() and _dialogue_rows[0] is Dictionary:
		return str(_dialogue_rows[0].get("id", "start"))
	return "start"


func _row_by_id(id: String) -> Dictionary:
	for row in _dialogue_rows:
		if row is Dictionary and str(row.get("id", "")) == id:
			return row
	return {}


func _refresh_display() -> void:
	var row := _row_by_id(_current_id)
	if row.is_empty():
		_end_dialogue_immediate()
		return

	var vbox: VBoxContainer = _dialogue_box.get_node("VBoxContainer") as VBoxContainer
	var name_label: Label = vbox.get_node("NameLabel") as Label
	var text_label: Label = vbox.get_node("TextLabel") as Label
	var choices: VBoxContainer = vbox.get_node("ChoicesContainer") as VBoxContainer

	name_label.text = str(row.get("speaker", _npc_id))
	text_label.text = str(row.get("text", ""))

	for c in choices.get_children():
		c.queue_free()

	var raw_choices = row.get("choices", null)
	if raw_choices is Array and not (raw_choices as Array).is_empty():
		_awaiting_choice = true
		for ch in raw_choices as Array:
			if ch is Dictionary:
				var btn := Button.new()
				btn.text = str(ch.get("text", "..."))
				var next_id: String = str(ch.get("next", ""))
				btn.pressed.connect(_on_choice_pressed.bind(next_id))
				choices.add_child(btn)
	else:
		_awaiting_choice = false


func _on_choice_pressed(next_id: String) -> void:
	_awaiting_choice = false
	if next_id.is_empty():
		_end_dialogue_immediate()
		return
	_current_id = next_id
	_refresh_display()


func _advance_linear() -> void:
	var row := _row_by_id(_current_id)
	if row.is_empty():
		_end_dialogue_immediate()
		return

	var nxt: String = str(row.get("next", ""))
	if nxt.is_empty():
		_end_dialogue_immediate()
	else:
		_current_id = nxt
		_refresh_display()


func _end_dialogue_immediate() -> void:
	_dialogue_rows.clear()
	_npc_id = ""
	_current_id = ""
	_awaiting_choice = false
	if is_instance_valid(_dialogue_layer):
		_dialogue_layer.queue_free()
	_dialogue_layer = null
	_dialogue_box = null
