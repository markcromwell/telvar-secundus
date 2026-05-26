extends Node

## Autoload: persists QuestManager and LoreManager state to user:// JSON.

const SAVE_PATH := "user://save_game.json"


func save_game() -> void:
	var payload := {
		"quests": QuestManager.quests,
		"lore_unlocked": LoreManager.unlocked.duplicate(),
	}
	var json_text := JSON.stringify(payload)
	var file := FileAccess.open(SAVE_PATH, FileAccess.WRITE)
	if file == null:
		push_error("SaveManager: could not open %s for write" % SAVE_PATH)
		return
	file.store_string(json_text)
	file.close()


func load_game() -> void:
	if not FileAccess.file_exists(SAVE_PATH):
		return
	var file := FileAccess.open(SAVE_PATH, FileAccess.READ)
	if file == null:
		push_error("SaveManager: could not open %s for read" % SAVE_PATH)
		return
	var text := file.get_as_text()
	file.close()
	var parsed: Variant = JSON.parse_string(text)
	if typeof(parsed) != TYPE_DICTIONARY:
		return
	var data: Dictionary = parsed
	if data.has("quests") and typeof(data["quests"]) == TYPE_DICTIONARY:
		QuestManager.quests = data["quests"]
	var lore_raw: Variant = data.get("lore_unlocked", [])
	LoreManager.unlocked.clear()
	if lore_raw is Array:
		var ids: Array[String] = []
		for item in lore_raw:
			ids.append(String(item))
		LoreManager.unlocked.append_array(ids)
