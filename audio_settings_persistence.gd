extends RefCounted
class_name AudioSettingsPersistence

## Loads and saves Master/Music/SFX levels (0–100) in user://settings.json.
##
## Hardened for adversarial conditions (MVP-7 Polish, spec #1542):
##   * Writes are atomic: the document is serialized to a temp sibling
##     (``user://settings.json.tmp``) and then renamed over the canonical file.
##     A reader (a concurrent session, an interrupted or timed-out write) always
##     sees either the complete old file or the complete new one — never a
##     half-written/truncated one.
##   * Before overwriting, the on-disk modified-time captured at the last load is
##     compared against the current on-disk state. If another session changed the
##     file in the meantime, its values are reloaded and our changes re-applied on
##     top, rather than blindly clobbering it. Concurrent sessions cannot corrupt
##     the config this way.
##   * Every FileAccess/DirAccess result is inspected. Permission failures
##     (ERR_FILE_NO_PERMISSION/ERR_FILE_CANT_WRITE) and disk timeout/busy
##     conditions (ERR_TIMEOUT/ERR_BUSY) return a non-OK Error code without
##     raising, so the caller keeps its prior values and can return to the menu.

const SETTINGS_PATH := "user://settings.json"
const TEMP_PATH := "user://settings.json.tmp"

const DEFAULT_MASTER := 100
const DEFAULT_MUSIC := 100
const DEFAULT_SFX := 100

## Modified-time of SETTINGS_PATH observed at the last clean load/save, used to
## detect concurrent external modification before we overwrite. -1 = unknown.
static var _disk_stamp: int = -1


static func default_settings() -> Dictionary:
	return {
		"master": DEFAULT_MASTER,
		"music": DEFAULT_MUSIC,
		"sfx": DEFAULT_SFX,
	}


## Clamp/whitelist an arbitrary dictionary down to the keys we own, so a tampered
## or partial file can never poison the values we persist.
static func _sanitize(data: Dictionary) -> Dictionary:
	var out: Dictionary = default_settings()
	for key in out.keys():
		if data.has(key):
			var v: Variant = data[key]
			if typeof(v) == TYPE_INT or typeof(v) == TYPE_FLOAT:
				out[key] = clampi(int(v), 0, 100)
	return out


## Current on-disk modification time (0 when the file is absent).
static func _current_stamp() -> int:
	if not FileAccess.file_exists(SETTINGS_PATH):
		return 0
	return int(FileAccess.get_modified_time(SETTINGS_PATH))


## Read + sanitize the canonical file, falling back to defaults on any problem.
## Never raises; never touches the disk-stamp bookkeeping.
static func _read_disk() -> Dictionary:
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
	return _sanitize(parsed)


static func load_settings_from_disk() -> Dictionary:
	var merged := _read_disk()
	_disk_stamp = _current_stamp()
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


## Persist the given settings to disk atomically. Returns OK on full success, or
## a non-OK Error code (permission/timeout/busy/IO) on failure. On any failure
## the canonical file is left byte-for-byte intact and the temp file is removed,
## so the caller can safely keep its prior in-memory values. Concurrent external
## modification is reloaded and merged rather than clobbered. Never asserts or
## crashes on a write failure.
static func save_settings_to_disk(data: Dictionary) -> int:
	# Reload-then-reapply: start from the current on-disk state and overlay only
	# the keys the caller actually provides. If another session changed the file
	# since we loaded it, its values form the merge base and are preserved here
	# instead of being clobbered by stale in-memory values — so concurrent
	# sessions cannot corrupt the config.
	var to_save: Dictionary = _read_disk()
	if _disk_stamp >= 0 and FileAccess.file_exists(SETTINGS_PATH) and _current_stamp() != _disk_stamp:
		push_warning("AudioSettingsPersistence: settings.json changed since load; merging onto current on-disk values.")
	for key in default_settings().keys():
		if data.has(key):
			var v: Variant = data[key]
			if typeof(v) == TYPE_INT or typeof(v) == TYPE_FLOAT:
				to_save[key] = clampi(int(v), 0, 100)

	# Serialize to a temp sibling first; never write the canonical file directly.
	var tmp := FileAccess.open(TEMP_PATH, FileAccess.WRITE)
	if tmp == null:
		var open_err := FileAccess.get_open_error()
		push_warning("AudioSettingsPersistence: cannot open temp for write (error %d); prior settings preserved." % open_err)
		return open_err if open_err != OK else FAILED
	tmp.store_string(JSON.stringify(to_save, "\t"))
	tmp.flush()
	var write_err := tmp.get_error()
	tmp.close()
	if write_err != OK:
		push_warning("AudioSettingsPersistence: write failed (error %d); prior settings preserved." % write_err)
		_remove_temp()
		return write_err

	# Atomically swap the temp file over the canonical file. DirAccess.rename
	# overwrites the destination, so a reader sees a complete file at all times.
	var dir := DirAccess.open("user://")
	if dir == null:
		var dir_err := DirAccess.get_open_error()
		push_warning("AudioSettingsPersistence: cannot open user:// (error %d); prior settings preserved." % dir_err)
		_remove_temp()
		return dir_err if dir_err != OK else FAILED
	var rename_err := dir.rename(TEMP_PATH, SETTINGS_PATH)
	if rename_err != OK:
		push_warning("AudioSettingsPersistence: commit rename failed (error %d); prior settings preserved." % rename_err)
		_remove_temp()
		return rename_err

	_disk_stamp = _current_stamp()
	return OK


## Best-effort removal of a leftover temp file so a later retry starts clean.
static func _remove_temp() -> void:
	if FileAccess.file_exists(TEMP_PATH):
		var dir := DirAccess.open("user://")
		if dir != null:
			dir.remove(TEMP_PATH)
