class_name AudioSettingsPersistence
extends RefCounted
## Loads and saves Master/Music/SFX volume (0–100 %) to user://settings.json
## and applies them via AudioServer. Call load_and_apply() once at game start;
## call save_and_apply() when slider values change.

const SETTINGS_PATH := "user://settings.json"

const _KEY_VERSION := "version"
const _KEY_MASTER := "master"
const _KEY_MUSIC := "music"
const _KEY_SFX := "sfx"

const _CURRENT_VERSION := 1


static func _default_dict() -> Dictionary:
	return {
		_KEY_VERSION: _CURRENT_VERSION,
		_KEY_MASTER: 100,
		_KEY_MUSIC: 100,
		_KEY_SFX: 100,
	}


static func percent_to_volume_db(percent: int) -> float:
	var p := clampi(percent, 0, 100)
	if p <= 0:
		return -80.0
	return linear_to_db(p / 100.0)


static func _coerce_percent(value: Variant, fallback: int) -> int:
	if typeof(value) == TYPE_FLOAT:
		return clampi(int(round(value as float)), 0, 100)
	if typeof(value) == TYPE_INT:
		return clampi(value as int, 0, 100)
	return fallback


static func _merge_with_defaults(data: Dictionary) -> Dictionary:
	var out := _default_dict()
	out[_KEY_MASTER] = _coerce_percent(data.get(_KEY_MASTER, out[_KEY_MASTER]), out[_KEY_MASTER])
	out[_KEY_MUSIC] = _coerce_percent(data.get(_KEY_MUSIC, out[_KEY_MUSIC]), out[_KEY_MUSIC])
	out[_KEY_SFX] = _coerce_percent(data.get(_KEY_SFX, out[_KEY_SFX]), out[_KEY_SFX])
	out[_KEY_VERSION] = _CURRENT_VERSION
	return out


static func load_settings_from_disk() -> Dictionary:
	if not FileAccess.file_exists(SETTINGS_PATH):
		return _default_dict()

	var json_text := FileAccess.get_file_as_string(SETTINGS_PATH)
	if FileAccess.get_open_error() != OK:
		return _default_dict()

	var parsed: Variant = JSON.parse_string(json_text)
	if typeof(parsed) != TYPE_DICTIONARY:
		return _default_dict()

	return _merge_with_defaults(parsed as Dictionary)


static func apply_settings(settings: Dictionary) -> void:
	var s := _merge_with_defaults(settings)
	_apply_bus(_KEY_MASTER, "Master", s)
	_apply_bus(_KEY_MUSIC, "Music", s)
	_apply_bus(_KEY_SFX, "SFX", s)


static func _apply_bus(key: String, bus_name: String, settings: Dictionary) -> void:
	var idx := AudioServer.get_bus_index(bus_name)
	if idx < 0:
		return
	var pct: int = int(settings[key])
	AudioServer.set_bus_mute(idx, pct <= 0)
	AudioServer.set_bus_volume_db(idx, percent_to_volume_db(pct))


static func load_and_apply() -> Dictionary:
	var s := load_settings_from_disk()
	apply_settings(s)
	return s


static func save_and_apply(master: int, music: int, sfx: int) -> Dictionary:
	var s := {
		_KEY_VERSION: _CURRENT_VERSION,
		_KEY_MASTER: clampi(master, 0, 100),
		_KEY_MUSIC: clampi(music, 0, 100),
		_KEY_SFX: clampi(sfx, 0, 100),
	}
	var json_text := JSON.stringify(s, "\t")
	var file := FileAccess.open(SETTINGS_PATH, FileAccess.WRITE)
	if file == null:
		push_error("AudioSettingsPersistence: could not open %s for write" % SETTINGS_PATH)
		apply_settings(s)
		return s
	file.store_string(json_text)
	file.close()
	apply_settings(s)
	return s
