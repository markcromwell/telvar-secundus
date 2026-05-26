extends Node
## Cross-scene gameplay hints (spawn markers, etc.) until a fuller GameState lands.

var next_spawn_marker_name: String = ""


func set_next_spawn(marker_name: String) -> void:
	next_spawn_marker_name = marker_name


func take_next_spawn_marker_name() -> String:
	var n := next_spawn_marker_name
	next_spawn_marker_name = ""
	return n
