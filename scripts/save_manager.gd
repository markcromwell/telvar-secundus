extends RefCounted
class_name SaveManager

## Loads per-slot JSON save files. Missing or invalid files yield an empty slot
## dict without raising. Mirrors the JSON rules enforced in tests/save_manager_contract.py.

const SAVE_SLOT_VERSION := 1


static func empty_save_slot() -> Dictionary:
	return {"empty": true, "version": SAVE_SLOT_VERSION}


static func load_save_slot(path: String) -> Dictionary:
	if path.is_empty():
		return empty_save_slot()
	if not FileAccess.file_exists(path):
		return empty_save_slot()
	var text := FileAccess.get_file_as_string(path)
	if text.is_empty() and FileAccess.get_open_error() != OK:
		push_warning("SaveManager: could not read save file (treating as empty): %s" % path)
		return empty_save_slot()
	var json := JSON.new()
	var parse_err := json.parse(text)
	if parse_err != OK:
		push_warning(
			"SaveManager: corrupt save JSON (treating as empty): %s — %s"
			% [path, json.get_error_message()]
		)
		return empty_save_slot()
	var data = json.data
	if typeof(data) != TYPE_DICTIONARY:
		push_warning("SaveManager: save root is not an object (treating as empty): %s" % path)
		return empty_save_slot()
	return data
