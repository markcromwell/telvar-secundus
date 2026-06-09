extends Node
## Settings autoload: loads/saves user settings to ``user://settings.cfg`` (ConfigFile).
##
## Designed for adversarial conditions (MVP-7 Polish):
##   * An in-memory cache always holds the last-known-good values. Reads never
##     touch disk, so a failed write can never surface partial or empty values.
##   * Writes are atomic: the config is serialized to a temp sibling
##     (``user://settings.cfg.tmp``) and then renamed over the canonical file via
##     DirAccess. A reader (a concurrent session, an interrupted write, a disk
##     timeout) therefore always sees either the complete old file or the
##     complete new one — never a half-written one.
##   * Loading a missing, unreadable, or malformed file falls back to defaults
##     and never raises, so callers can return to the menu with intact values.

const SETTINGS_PATH: String = "user://settings.cfg"
const TEMP_PATH: String = "user://settings.cfg.tmp"

## Last-known-good values, kept as {section: {key: value}}. Always populated.
var _cache: Dictionary = {}

## Set when load()/save() fail, for callers (e.g. a settings menu) to inspect.
var last_error: String = ""


func _ready() -> void:
	load_settings()


## Canonical defaults. Nested as {section: {key: value}} to mirror ConfigFile.
func _defaults() -> Dictionary:
	return {
		"audio": {
			"master": 100,
			"music": 100,
			"sfx": 100,
		},
		"display": {
			"fullscreen": false,
			"vsync": true,
		},
	}


## Deep copy so the live cache can never alias the defaults template.
func _clone_defaults() -> Dictionary:
	var out: Dictionary = {}
	var defaults: Dictionary = _defaults()
	for section in defaults:
		out[section] = (defaults[section] as Dictionary).duplicate(true)
	return out


## Load settings from disk into the cache. Always leaves the cache fully
## populated with valid values; missing/unreadable/malformed files fall back to
## defaults without raising. Returns true if the on-disk file was read cleanly.
func load() -> bool:
	last_error = ""
	# Start from a complete set of defaults; overlay whatever the file provides.
	_cache = _clone_defaults()

	if not FileAccess.file_exists(SETTINGS_PATH):
		# No file yet is a normal first-run case, not an error.
		return false

	var cf: ConfigFile = ConfigFile.new()
	var err: int = cf.load(SETTINGS_PATH)
	if err != OK:
		# Unreadable or malformed file: keep defaults, report, never crash.
		last_error = "Could not read %s (error %d); using defaults." % [SETTINGS_PATH, err]
		push_warning("Settings: " + last_error)
		return false

	# Overlay only keys we know about, and only when the type matches the
	# default, so a corrupted/tampered file can't poison the cache.
	for section in _cache:
		var defaults_section: Dictionary = _cache[section]
		for key in defaults_section:
			var fallback: Variant = defaults_section[key]
			var value: Variant = cf.get_value(section, key, fallback)
			if typeof(value) == typeof(fallback):
				defaults_section[key] = value
	return true


## Atomically persist the cache to disk. Serializes to a temp sibling and then
## renames it over the canonical file via DirAccess, so the canonical file is
## never partially written and a failure preserves the prior on-disk values.
## Returns true on success; on failure the cache (and prior disk file) are intact.
func save() -> bool:
	last_error = ""

	var cf: ConfigFile = ConfigFile.new()
	for section in _cache:
		var section_data: Dictionary = _cache[section]
		for key in section_data:
			cf.set_value(section, key, section_data[key])

	# Write the full document to a temp file first. If this fails (permission
	# error, disk timeout, full disk), the canonical file is untouched.
	var err: int = cf.save(TEMP_PATH)
	if err != OK:
		last_error = "Could not write %s (error %d); prior settings preserved." % [TEMP_PATH, err]
		push_warning("Settings: " + last_error)
		_remove_temp()
		return false

	# Atomically swap the temp file over the canonical file. DirAccess.rename
	# overwrites an existing destination, so readers see a complete file.
	var dir: DirAccess = DirAccess.open("user://")
	if dir == null:
		last_error = "Could not open user:// to commit settings (error %d)." % DirAccess.get_open_error()
		push_warning("Settings: " + last_error)
		_remove_temp()
		return false

	var rename_err: int = dir.rename(TEMP_PATH, SETTINGS_PATH)
	if rename_err != OK:
		last_error = "Could not commit settings via rename (error %d); prior settings preserved." % rename_err
		push_warning("Settings: " + last_error)
		_remove_temp()
		return false

	return true


func load_settings() -> bool:
	return load()


func save_settings() -> bool:
	return save()


## Best-effort cleanup of a leftover temp file so retries start clean.
func _remove_temp() -> void:
	if FileAccess.file_exists(TEMP_PATH):
		var dir: DirAccess = DirAccess.open("user://")
		if dir != null:
			dir.remove(TEMP_PATH)


## Read a value from the in-memory cache. Returns ``default`` when the caller
## passes one for an unknown section/key, otherwise the built-in default, else
## ``null``. Never touches disk, so it always returns a sane value.
func get_value(section: String, key: String, default: Variant = null) -> Variant:
	if _cache.has(section):
		var section_data: Dictionary = _cache[section]
		if section_data.has(key):
			return section_data[key]
	if default != null:
		return default
	var defaults: Dictionary = _defaults()
	if defaults.has(section) and (defaults[section] as Dictionary).has(key):
		return defaults[section][key]
	return null


## Update a value in the in-memory cache. Does not write to disk; call save()
## to persist. Keeping this in-memory means a later failed save cannot corrupt
## the values already shown to the user.
func set_value(section: String, key: String, value: Variant) -> void:
	if not _cache.has(section):
		_cache[section] = {}
	(_cache[section] as Dictionary)[key] = value
