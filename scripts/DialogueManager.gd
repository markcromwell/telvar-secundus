extends Node

const DIALOGUE_BOX_SCENE := preload("res://scenes/DialogueBox.tscn")

signal dialogue_choice_selected(npc_id: String, choice_index: int)

var _flags: Dictionary = {}
var _ui_layer: CanvasLayer
var _box: Control
var _current_npc_id: String = ""


func _ready() -> void:
	_ui_layer = CanvasLayer.new()
	_ui_layer.layer = 128
	add_child(_ui_layer)
	_box = DIALOGUE_BOX_SCENE.instantiate() as Control
	_ui_layer.add_child(_box)
	_box.choice_selected.connect(_on_box_choice_selected)


func set_flag(key: String, value: Variant) -> void:
	_flags[key] = value


func get_flag(key: String) -> Variant:
	return _flags.get(key)


func hide_dialogue() -> void:
	if _box and _box.has_method("hide_dialogue"):
		_box.hide_dialogue()


func show_dialogue(npc_id: String, dialogue_json: Variant) -> void:
	var entries: Array = _coerce_dialogue_array(dialogue_json)
	if entries.is_empty():
		push_warning("DialogueManager.show_dialogue: empty or invalid dialogue for '%s'" % npc_id)
		return
	_current_npc_id = npc_id
	var entry: Variant = _find_entry_by_id(entries, "start")
	if entry == null and entries.size() > 0:
		entry = entries[0]
	if entry is not Dictionary:
		push_warning("DialogueManager.show_dialogue: no valid entry for '%s'" % npc_id)
		return
	var dict: Dictionary = _entry_to_show_dict(entry as Dictionary, npc_id)
	if _box and _box.has_method("show_dialogue"):
		_box.show_dialogue(dict)


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


func _entry_to_show_dict(entry: Dictionary, npc_id: String) -> Dictionary:
	var out: Dictionary = {
		"text": str(entry.get("text", "")),
		"speaker": str(entry.get("speaker", "")),
		"choices": entry.get("choices", []),
	}
	var portrait_path := "res://assets/portraits/%s.png" % npc_id
	if ResourceLoader.exists(portrait_path):
		out["portrait"] = portrait_path
	return out


func _on_box_choice_selected(index: int) -> void:
	dialogue_choice_selected.emit(_current_npc_id, index)
