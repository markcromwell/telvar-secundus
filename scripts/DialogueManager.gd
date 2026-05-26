extends Node

const DIALOGUE_BOX_SCENE := preload("res://scenes/DialogueBox.tscn")

signal dialogue_choice_selected(npc_id: String, choice_index: int)

var _flags: Dictionary = {}
var _ui_layer: CanvasLayer
var _box: Control
var _current_npc_id: String = ""
var _entries: Array = []
var _current_entry_id: String = ""


func _ready() -> void:
	_ui_layer = CanvasLayer.new()
	_ui_layer.layer = 10
	add_child(_ui_layer)
	_box = DIALOGUE_BOX_SCENE.instantiate() as Control
	_box.visible = false
	_ui_layer.add_child(_box)
	_box.choice_selected.connect(_on_box_choice_selected)


func set_flag(key: String, value: Variant) -> void:
	_flags[key] = value


func get_flag(key: String, default: Variant = null) -> Variant:
	return _flags.get(key, default)


func hide_dialogue() -> void:
	_end_dialogue_session()


func show_dialogue(npc_id: String, dialogue_json: Variant) -> void:
	var entries: Array = _coerce_dialogue_array(dialogue_json)
	if entries.is_empty():
		push_warning("DialogueManager.show_dialogue: empty or invalid dialogue for '%s'" % npc_id)
		return
	_current_npc_id = npc_id
	_entries = entries
	var entry: Variant = _find_entry_by_id(entries, "start")
	if entry == null and entries.size() > 0:
		entry = entries[0]
	if entry is not Dictionary:
		push_warning("DialogueManager.show_dialogue: no valid entry for '%s'" % npc_id)
		_entries.clear()
		return
	_current_entry_id = str((entry as Dictionary).get("id", ""))
	_push_entry_to_ui(entry as Dictionary)


func _coerce_dialogue_array(dialogue_json: Variant) -> Array:
	if dialogue_json is String:
		var parsed: Variant = JSON.parse_string(dialogue_json)
		return parsed if parsed is Array else []
	if dialogue_json is Array:
		return dialogue_json
	return []


func _find_entry_by_id(entries: Array, want_id: String) -> Variant:
	for e in entries:
		if e is Dictionary and str((e as Dictionary).get("id", "")) == want_id:
			return e
	return null


func _entry_to_ui_dict(entry: Dictionary, npc_id: String) -> Dictionary:
	var out: Dictionary = {
		"text": str(entry.get("text", "")),
		"speaker": str(entry.get("speaker", "")),
		"choices": entry.get("choices", []),
	}
	var portrait_path := "res://assets/portraits/%s.png" % npc_id
	if ResourceLoader.exists(portrait_path):
		out["portrait"] = portrait_path
	return out


func _push_entry_to_ui(entry: Dictionary) -> void:
	if _box and _box.has_method("show_dialogue"):
		_box.show_dialogue(_entry_to_ui_dict(entry, _current_npc_id))


func _advance_to_id(next_id: String) -> void:
	if next_id.is_empty():
		_end_dialogue_session()
		return
	var entry: Variant = _find_entry_by_id(_entries, next_id)
	if entry is not Dictionary:
		push_warning("DialogueManager: missing dialogue id '%s'" % next_id)
		_end_dialogue_session()
		return
	_current_entry_id = str((entry as Dictionary).get("id", next_id))
	_push_entry_to_ui(entry as Dictionary)


func _end_dialogue_session() -> void:
	_entries.clear()
	_current_entry_id = ""
	if _box and _box.has_method("hide_dialogue"):
		_box.hide_dialogue()


func _unhandled_input(event: InputEvent) -> void:
	if not _session_active():
		return
	if event.is_action_pressed("dialogue_skip"):
		_try_advance_linear()


func _session_active() -> bool:
	return _box != null and _box.visible and not _entries.is_empty()


func _try_advance_linear() -> void:
	if not (_box.get("_typing_complete") == true):
		return
	var entry: Variant = _find_entry_by_id(_entries, _current_entry_id)
	if entry is not Dictionary:
		return
	var d: Dictionary = entry
	if _entry_has_choice_buttons(d):
		return
	var next_id: String = str(d.get("next", ""))
	get_viewport().set_input_as_handled()
	if next_id.is_empty():
		_end_dialogue_session()
	else:
		_advance_to_id(next_id)


func _entry_has_choice_buttons(entry: Dictionary) -> bool:
	var choices: Variant = entry.get("choices", [])
	if choices is not Array:
		return false
	var arr: Array = choices
	if arr.is_empty():
		return false
	for ch in arr:
		if ch is Dictionary:
			return true
	return false


func _on_box_choice_selected(index: int) -> void:
	dialogue_choice_selected.emit(_current_npc_id, index)
	var next_id := _choice_next_id(index)
	call_deferred("_advance_after_choice", next_id)


func _choice_next_id(index: int) -> String:
	var entry: Variant = _find_entry_by_id(_entries, _current_entry_id)
	if entry is not Dictionary:
		return ""
	var choices: Variant = (entry as Dictionary).get("choices", [])
	if choices is not Array:
		return ""
	var arr: Array = choices
	if index < 0 or index >= arr.size():
		return ""
	var ch: Variant = arr[index]
	if ch is not Dictionary:
		return ""
	return str((ch as Dictionary).get("next", ""))


func _advance_after_choice(next_id: String) -> void:
	_advance_to_id(next_id)
