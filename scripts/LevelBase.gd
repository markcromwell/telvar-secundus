extends Node2D
class_name LevelBase

func _setup_level() -> void:
	_add_location_markers()

func _add_location_markers() -> void:
	var marker_script = load("res://scripts/LocationMarker.gd")
	for location_name in GameManager.KEY_LOCATIONS:
		var pos = GameManager.KEY_LOCATIONS[location_name]
		var marker = marker_script.new()
		marker.location_name = location_name
		marker.position = pos
		add_child(marker)
