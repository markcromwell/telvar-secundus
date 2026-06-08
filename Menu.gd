extends Node

## Menu autoload: coordinates settings sliders with volume persistence.
##
## Wraps spec 1311's AudioSettingsPersistence. On _ready it loads the saved
## Master/Music/SFX levels from user://settings.json and applies them to the
## AudioServer buses, then caches them in memory. Screens (settings, load,
## credits) read/write volumes through get_volume()/set_volume() so values
## restore on returning to the menu after gameplay.

## Emitted whenever a volume changes so open screens can refresh their sliders.
signal settings_changed

## Valid volume channels (match AudioSettingsPersistence keys).
const CHANNELS := ["master", "music", "sfx"]

## In-memory percentages (0–100) for each channel.
var _volumes: Dictionary = {}


func _ready() -> void:
	# Load persisted settings (or defaults) and apply them to the AudioServer.
	var data: Dictionary = AudioSettingsPersistence.load_settings_from_disk()
	AudioSettingsPersistence.apply_settings(data)
	for channel in CHANNELS:
		_volumes[channel] = clampi(int(data.get(channel, 100)), 0, 100)


## Returns the cached percentage (0–100) for the given channel.
func get_volume(channel: String) -> int:
	return int(_volumes.get(channel, 100))


## Updates a channel volume: caches it, re-applies to the AudioServer, persists
## to disk, and notifies listeners via settings_changed.
func set_volume(channel: String, pct: int) -> void:
	if not CHANNELS.has(channel):
		push_warning("Menu.set_volume: unknown channel '%s'" % channel)
		return
	_volumes[channel] = clampi(int(pct), 0, 100)
	AudioSettingsPersistence.apply_settings(_volumes)
	AudioSettingsPersistence.save_settings_to_disk(_volumes)
	settings_changed.emit()
