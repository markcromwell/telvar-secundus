extends Control

## Settings UI: Master / Music / SFX (0–100). Updates AudioServer buses live and
## persists via AudioSettingsPersistence → user://settings.json.
##
## Hardened (spec #1542): a failed save (permission / disk timeout / busy / IO)
## never corrupts the on-disk config and never crashes. On failure the sliders
## and audio buses revert to the last-known-good values and `save_failed` is
## emitted, so a parent menu can return the player to the menu with intact prior
## values.

## Emitted when a save could not be committed. `message` is human-readable; the
## sliders have already been reverted to the last-known-good values.
signal save_failed(message: String)

@onready var _master_slider: HSlider = $VBoxContainer/MasterRow/MasterSlider
@onready var _music_slider: HSlider = $VBoxContainer/MusicRow/MusicSlider
@onready var _sfx_slider: HSlider = $VBoxContainer/SfxRow/SfxSlider

var _suppress_slider_feedback: bool = false

## Last values successfully persisted; restored if a later save fails so the
## in-memory state always matches what is actually on disk.
var _last_good: Dictionary = AudioSettingsPersistence.default_settings()


func _ready() -> void:
	_refresh_sliders_from_disk()


func _notification(what: int) -> void:
	if what == NOTIFICATION_VISIBILITY_CHANGED and visible:
		_refresh_sliders_from_disk()


func _refresh_sliders_from_disk() -> void:
	var data: Dictionary = AudioSettingsPersistence.load_settings_from_disk()
	_last_good = data.duplicate(true)
	_apply_to_sliders(data)


func _apply_to_sliders(data: Dictionary) -> void:
	_suppress_slider_feedback = true
	_master_slider.value = float(data.get("master", 100))
	_music_slider.value = float(data.get("music", 100))
	_sfx_slider.value = float(data.get("sfx", 100))
	_suppress_slider_feedback = false


func _on_slider_value_changed(_value: float) -> void:
	if _suppress_slider_feedback:
		return
	var payload: Dictionary = {
		"master": int(_master_slider.value),
		"music": int(_music_slider.value),
		"sfx": int(_sfx_slider.value),
	}
	# Apply live so the player hears the change immediately, then try to persist.
	AudioSettingsPersistence.apply_settings(payload)
	var err: int = AudioSettingsPersistence.save_settings_to_disk(payload)
	if err != OK:
		# Save failed: roll the audio and sliders back to the last-known-good
		# values so nothing the player sees or hears diverges from disk, then
		# notify so a parent menu can return with intact prior values.
		AudioSettingsPersistence.apply_settings(_last_good)
		_apply_to_sliders(_last_good)
		save_failed.emit("Could not save settings (error %d); previous values kept." % err)
		return
	# Commit the new values as the last-known-good baseline only on full success.
	_last_good = payload.duplicate(true)
