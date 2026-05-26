extends Node
## Persists game state. Autosave writes to user://save_autosave.json with no UI feedback.
## Use SaveManager.get_slot_display_name() in load menus so the autosave row reads "Autosave".

const AUTOSAVE_PATH := "user://save_autosave.json"
const AUTOSAVE_SLOT_LABEL := "Autosave"

var _last_autosave_error: String = ""


func get_slot_display_name(file_path: String) -> String:
	if file_path == AUTOSAVE_PATH:
		return AUTOSAVE_SLOT_LABEL
	var base := file_path.get_file()
	if base == "save_autosave.json":
		return AUTOSAVE_SLOT_LABEL
	return base.get_basename()


func is_autosave_path(file_path: String) -> bool:
	return file_path == AUTOSAVE_PATH or file_path.get_file() == "save_autosave.json"


func get_last_autosave_error() -> String:
	return _last_autosave_error


func build_save_payload() -> Dictionary:
	var scene_path := ""
	var cur: Node = get_tree().current_scene
	if cur:
		scene_path = str(cur.scene_file_path)
	return {
		"kind": "telvar_save",
		"version": 1,
		"saved_at_unix": Time.get_unix_time_from_system(),
		"current_scene": scene_path,
	}


## Writes autosave without dialogs, toasts, or pausing the tree.
func autosave_silent() -> bool:
	_last_autosave_error = ""
	var json_text := JSON.stringify(build_save_payload())
	var f := FileAccess.open(AUTOSAVE_PATH, FileAccess.WRITE)
	if f == null:
		_last_autosave_error = "failed to open %s (error %d)" % [AUTOSAVE_PATH, FileAccess.get_open_error()]
		return false
	f.store_string(json_text)
	return true
