extends RefCounted
class_name AudioSettingsPersistence

## Loads and saves Master/Music/SFX levels (0–100) in user://settings.json.

const SETTINGS_PATH := "user://settings.json"

const DEFAULT_MASTER := 100
const DEFAULT_MUSIC := 100
const DEFAULT_SFX := 100


static func default_settings() -> Dictionary:
	return {
		"master": DEFAULT_MASTER,
		"music": DEFAULT_MUSIC,
		"sfx": DEFAULT_SFX,
	}


static func load_settings_from_disk() -> Dictionary:
	var merged: Dictionary = default_settings()
	if not FileAccess.file_exists(SETTINGS_PATH):
		return merged
	var f := FileAccess.open(SETTINGS_PATH, FileAccess.READ)
	if f == null:
		return merged
	var text := f.get_as_text()
	f.close()
	var parsed: Variant = JSON.parse_string(text)
	if typeof(parsed) != TYPE_DICTIONARY:
		return merged
	var data: Dictionary = parsed
	for key in merged.keys():
		if data.has(key):
			var v: Variant = data[key]
			if typeof(v) == TYPE_INT or typeof(v) == TYPE_FLOAT:
				merged[key] = clampi(int(v), 0, 100)
	return merged


static func _percent_to_linear(percent: int) -> float:
	return clampi(percent, 0, 100) / 100.0


static func apply_settings(data: Dictionary) -> void:
	var pairs: Array = [["master", "Master"], ["music", "Music"], ["sfx", "SFX"]]
	for pair in pairs:
		var key: String = pair[0]
		var bus_name: String = pair[1]
		var pct := int(data.get(key, 100))
		var linear := _percent_to_linear(pct)
		var idx := AudioServer.get_bus_index(bus_name)
		if idx >= 0:
			AudioServer.set_bus_volume_linear(idx, linear)


static func load_and_apply() -> void:
	apply_settings(load_settings_from_disk())


static func save_settings_to_disk(data: Dictionary) -> void:
	var to_save: Dictionary = default_settings()
	for key in to_save.keys():
		if data.has(key):
			var v: Variant = data[key]
			if typeof(v) == TYPE_INT or typeof(v) == TYPE_FLOAT:
				to_save[key] = clampi(int(v), 0, 100)
	var f := FileAccess.open(SETTINGS_PATH, FileAccess.WRITE)
	if f == null:
		push_warning("AudioSettingsPersistence: could not write %s" % SETTINGS_PATH)
		return
	f.store_string(JSON.stringify(to_save, "\t"))
	f.close()
