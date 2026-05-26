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


## Paths under `user://` matching `save_*.json` (autosave first, then alphabetical).
func list_user_save_paths() -> PackedStringArray:
	var paths: Array[String] = []
	var dir := DirAccess.open("user://")
	if dir == null:
		return PackedStringArray()
	dir.list_dir_begin()
	var fn := dir.get_next()
	while fn != "":
		if not dir.current_is_dir() and fn.ends_with(".json") and fn.begins_with("save_"):
			paths.append("user://" + fn)
		fn = dir.get_next()
	dir.list_dir_end()
	paths.sort_custom(
		func(a: String, b: String) -> bool:
			var ae := is_autosave_path(a)
			var be := is_autosave_path(b)
			if ae != be:
				return ae
			return a < b
	)
	return PackedStringArray(paths)


## Restores `current_scene` from a save file without running transition autosave.
func load_save_from_path(file_path: String) -> Error:
	var json_text := FileAccess.get_file_as_string(file_path)
	if json_text.is_empty() and not FileAccess.file_exists(file_path):
		return ERR_FILE_NOT_FOUND
	var parsed: Variant = JSON.parse_string(json_text)
	if typeof(parsed) != TYPE_DICTIONARY:
		return ERR_INVALID_DATA
	var data: Dictionary = parsed
	if str(data.get("kind", "")) != "telvar_save":
		return ERR_INVALID_DATA
	var scene_path := str(data.get("current_scene", ""))
	if scene_path.is_empty() or not ResourceLoader.exists(scene_path):
		return ERR_FILE_MISSING
	return get_tree().change_scene_to_file(scene_path)


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
