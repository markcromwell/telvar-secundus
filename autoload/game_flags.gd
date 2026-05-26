extends Node
## Session flags for scripted progression (Telvar room rest, one-shot events).

var rested_in_telvar_room: bool = false
var sealed_wings_night_scene_completed: bool = false


func mark_rested_in_telvar_room() -> void:
	rested_in_telvar_room = true


func mark_sealed_wings_night_scene_completed() -> void:
	sealed_wings_night_scene_completed = true
