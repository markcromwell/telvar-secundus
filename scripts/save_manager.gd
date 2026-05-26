extends Node

## Autoload: persists QuestManager and LoreManager state to a single JSON file.
## Register as SaveManager in project.godot (autoload) when integrating phases.

const SAVE_PATH := "user://telvar_save.json"


func save_game() -> bool:
	var file := FileAccess.open(SAVE_PATH, FileAccess.WRITE)
	if file == null:
		push_error("SaveManager: could not open %s for writing." % SAVE_PATH)
		return false
	var payload := {
		"quests": QuestManager.quests.duplicate(true),
		"lore_unlocked": LoreManager.unlocked.duplicate(),
	}
	var json_text := JSON.stringify(payload)
	if json_text.is_empty():
		push_error("SaveManager: JSON serialization produced empty output.")
		return false
	file.store_string(json_text)
	return true


func load_game() -> bool:
	if not FileAccess.file_exists(SAVE_PATH):
		return false
	var file := FileAccess.open(SAVE_PATH, FileAccess.READ)
	if file == null:
		push_error("SaveManager: could not open %s for reading." % SAVE_PATH)
		return false
	var parsed: Variant = JSON.parse_string(file.get_as_text())
	if typeof(parsed) != TYPE_DICTIONARY:
		push_error("SaveManager: save file is not a JSON object.")
		return false
	var data: Dictionary = parsed

	if data.has("quests") and typeof(data["quests"]) == TYPE_DICTIONARY:
		QuestManager.quests = data["quests"]
	else:
		QuestManager.quests = {}

	LoreManager.unlocked.clear()
	if data.has("lore_unlocked") and typeof(data["lore_unlocked"]) == TYPE_ARRAY:
		var raw_lore: Array = data["lore_unlocked"]
		var lore_ids: Array[String] = []
		for item in raw_lore:
			if typeof(item) == TYPE_STRING:
				lore_ids.append(String(item))
		LoreManager.unlocked.append_array(lore_ids)

	return true
