extends CharacterBody2D
## Player movement + district sensor → AudioManager ambient crossfades (phase 2734).
## Place Secundus districts as Area2D on `district_physics_layer` with meta `district_key`
## (e.g. "Merchant District", "veneficturis", "rookery") or name `District_<label>`.

const SETTINGS_PATH := "user://settings.json"

## Godot physics layer index (1–32) reserved for district trigger areas.
@export var district_physics_layer: int = 9
@export var speed: float = 64.0  # pixels/sec (2 tiles at 32px)
@export var can_move: bool = true

@onready var _district_sensor: Area2D = $DistrictSensor


func _ready() -> void:
	_configure_district_sensor_mask()
	_district_sensor.area_entered.connect(_on_district_area_entered)
	_load_settings()
	call_deferred("_refresh_district_from_overlaps")


func _configure_district_sensor_mask() -> void:
	var layer_i: int = clampi(district_physics_layer, 1, 32)
	_district_sensor.collision_mask = 1 << (layer_i - 1)


func _exit_tree() -> void:
	_save_settings()


func _physics_process(_delta: float) -> void:
	if not can_move:
		return
	var dir := Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")
	velocity = dir * speed
	move_and_slide()


func _district_label_from_area(area: Area2D) -> String:
	if area == null:
		return ""
	if area.has_meta(&"district_key"):
		return str(area.get_meta(&"district_key"))
	var n := String(area.name)
	const prefix := "District_"
	if n.begins_with(prefix):
		return n.substr(prefix.length())
	return n


func _on_district_area_entered(area: Area2D) -> void:
	_apply_district_for_area(area)


func _refresh_district_from_overlaps() -> void:
	for a in _district_sensor.get_overlapping_areas():
		var label := _district_label_from_area(a)
		if not label.is_empty():
			AudioManager.set_current_district(label)
			return


func _apply_district_for_area(area: Area2D) -> void:
	var label := _district_label_from_area(area)
	if label.is_empty():
		return
	AudioManager.set_current_district(label)


func _load_settings() -> void:
	if not FileAccess.file_exists(SETTINGS_PATH):
		return
	var f := FileAccess.open(SETTINGS_PATH, FileAccess.READ)
	if f == null:
		return
	var parsed = JSON.parse_string(f.get_as_text())
	f.close()
	if typeof(parsed) != TYPE_DICTIONARY:
		return
	var d: Dictionary = parsed
	if d.has("music_volume_db"):
		AudioManager.set_volume("Music", float(d.get("music_volume_db", 0.0)))
	if d.has("sfx_volume_db"):
		AudioManager.set_volume("SFX", float(d.get("sfx_volume_db", 0.0)))


func _save_settings() -> void:
	var d := {}
	var idx_music := AudioServer.get_bus_index("Music")
	var idx_sfx := AudioServer.get_bus_index("SFX")
	if idx_music >= 0:
		d["music_volume_db"] = AudioServer.get_bus_volume_db(idx_music)
	if idx_sfx >= 0:
		d["sfx_volume_db"] = AudioServer.get_bus_volume_db(idx_sfx)
	var f := FileAccess.open(SETTINGS_PATH, FileAccess.WRITE)
	if f == null:
		return
	f.store_string(JSON.stringify(d, "\t"))
	f.close()
