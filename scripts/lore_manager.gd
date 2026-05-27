extends Node

const LORE_PATH := "res://assets/lore/lore_entries.json"
const TOAST_SECONDS := 3.0

var unlocked: Array[String] = []
var _toast_layer: CanvasLayer
var _toast_label: Label
var _toast_timer: Timer
var _titles_by_id: Dictionary = {}


func _ready() -> void:
	_load_lore_titles()


func _load_lore_titles() -> void:
	if not FileAccess.file_exists(LORE_PATH):
		return
	var raw := FileAccess.get_file_as_string(LORE_PATH)
	var parsed = JSON.parse_string(raw)
	if typeof(parsed) != TYPE_ARRAY:
		return
	for entry in parsed:
		if typeof(entry) != TYPE_DICTIONARY:
			continue
		var d: Dictionary = entry
		if d.has("id") and d.has("title"):
			_titles_by_id[str(d["id"])] = str(d["title"])


func unlock(entry_id: String) -> void:
	if entry_id.is_empty():
		return
	if entry_id in unlocked:
		return
	unlocked.append(entry_id)
	var title: String = str(_titles_by_id.get(entry_id, entry_id))
	_show_toast("Lore unlocked: %s" % title)


func is_unlocked(id: String) -> bool:
	return id in unlocked


func _ensure_toast_ui() -> void:
	if is_instance_valid(_toast_layer):
		return
	_toast_layer = CanvasLayer.new()
	_toast_layer.layer = 90
	add_child(_toast_layer)
	_toast_label = Label.new()
	_toast_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_toast_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_toast_label.position = Vector2(40, 80)
	_toast_label.size = Vector2(400, 32)
	_toast_label.visible = false
	_toast_layer.add_child(_toast_label)
	_toast_timer = Timer.new()
	_toast_timer.one_shot = true
	_toast_timer.timeout.connect(_on_toast_timeout)
	add_child(_toast_timer)


func _show_toast(message: String) -> void:
	_ensure_toast_ui()
	_toast_label.text = message
	_toast_label.visible = true
	_toast_timer.start(TOAST_SECONDS)


func _on_toast_timeout() -> void:
	if is_instance_valid(_toast_label):
		_toast_label.visible = false
