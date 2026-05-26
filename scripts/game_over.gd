extends Control
## Full-screen game over state after a bad story outcome (e.g. Walk away).
## Offers loading the most recently written save among slots 0–3 (0 = autosave).

const SAVE_PATH_TMPL := "user://save_slot_%d.json"
const SAVE_SLOT_COUNT := 4  # 0 autosave + 3 manual slots

@onready var _error_label: Label = %ErrorLabel
@onready var _load_button: Button = %LoadLastSaveButton


func _ready() -> void:
	_error_label.visible = false
	if not _has_any_save():
		_load_button.disabled = true
		_show_error("No save data found. There is nothing to load.")


func _has_any_save() -> bool:
	for slot in SAVE_SLOT_COUNT:
		if FileAccess.file_exists(SAVE_PATH_TMPL % slot):
			return true
	return false


func _on_load_last_save_pressed() -> void:
	_error_label.visible = false
	var slot := _find_last_save_slot()
	if slot < 0:
		_show_error("No save data found.")
		return
	var path := SAVE_PATH_TMPL % slot
	if not FileAccess.file_exists(path):
		_show_error("Save file disappeared.")
		return
	var content := FileAccess.get_file_as_string(path)
	var err_msg := _validate_and_load_scene(content)
	if err_msg != "":
		_show_error(err_msg)


func _find_last_save_slot() -> int:
	var best_slot := -1
	var best_time := -1.0
	for slot in SAVE_SLOT_COUNT:
		var p := SAVE_PATH_TMPL % slot
		if not FileAccess.file_exists(p):
			continue
		var t := float(FileAccess.get_modified_time(p))
		if t > best_time or (is_equal_approx(t, best_time) and slot > best_slot):
			best_time = t
			best_slot = slot
	return best_slot


func _validate_and_load_scene(json_text: String) -> String:
	var json := JSON.new()
	var parse_result := json.parse(json_text)
	if parse_result != OK:
		return "Save file is corrupted or unreadable (JSON error)."
	var data = json.data
	if typeof(data) != TYPE_DICTIONARY:
		return "Save file is corrupted (invalid root)."
	if not data.has("current_scene"):
		return "Save file is corrupted (missing current_scene)."
	var scene_path: Variant = data["current_scene"]
	if typeof(scene_path) != TYPE_STRING:
		return "Save file is corrupted (invalid current_scene)."
	var s := str(scene_path)
	if not s.begins_with("res://"):
		return "Save file is corrupted (scene path must start with res://)."
	if not ResourceLoader.exists(s):
		return "Save file references a missing scene."
	var err := get_tree().change_scene_to_file(s)
	if err != OK:
		return "Could not load saved scene."
	return ""


func _show_error(msg: String) -> void:
	_error_label.text = msg
	_error_label.visible = true
