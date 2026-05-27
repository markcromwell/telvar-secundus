extends Control

## Settings UI: Master / Music / SFX (0–100). Updates AudioServer buses live and
## persists via AudioSettingsPersistence → user://settings.json.

@onready var _master_slider: HSlider = $VBoxContainer/MasterRow/MasterSlider
@onready var _music_slider: HSlider = $VBoxContainer/MusicRow/MusicSlider
@onready var _sfx_slider: HSlider = $VBoxContainer/SfxRow/SfxSlider

var _suppress_slider_feedback: bool = false


func _ready() -> void:
	_refresh_sliders_from_disk()


func _notification(what: int) -> void:
	if what == NOTIFICATION_VISIBILITY_CHANGED and visible:
		_refresh_sliders_from_disk()


func _refresh_sliders_from_disk() -> void:
	var data: Dictionary = AudioSettingsPersistence.load_settings_from_disk()
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
	AudioSettingsPersistence.apply_settings(payload)
	AudioSettingsPersistence.save_settings_to_disk(payload)
