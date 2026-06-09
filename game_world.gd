extends Node2D

@onready var scene_router: SceneRouter = $SceneRouter
@onready var world_root: Node2D = $WorldRoot

var _save_data: Dictionary

func _ready() -> void:
	# Per spec, start ambient audio for the initial scene.
	var audio_manager = get_node_or_null("/root/AudioManager")
	if audio_manager != null and audio_manager.has_method("start_ambient"):
		audio_manager.start_ambient("apprentice_room")

	# Load the most recent state.
	_save_data = SaveSystem.load_from_slot(SaveSystem.AUTOSAVE_SLOT)

	# Determine the scene to load. Fallback to apprentice_room if not specified
	# or on first run. SceneRouter itself also has a fallback, but we can be explicit.
	var scene_to_load: String = _save_data.get("current_scene", "res://apprentice_room.tscn")
	if scene_to_load.is_empty():
		scene_to_load = "res://apprentice_room.tscn"

	# Connect to the scene_changed signal to restore player position AFTER the
	# new scene is loaded and parented under WorldRoot.
	scene_router.scene_changed.connect(_on_scene_changed, CONNECT_ONE_SHOT)
	scene_router.swap_to(scene_to_load)


func _notification(what: int) -> void:
	if what == NOTIFICATION_WM_CLOSE_REQUEST:
		_autosave()


func _on_scene_changed(_scene_name: String) -> void:
	# The new scene is now active. Find the player and restore position.
	# The player node is expected to be named "Player".
	var player: Node2D = world_root.find_child("Player", true, false)
	if player != null:
		var pos: Dictionary = _save_data.get("player_pos", {"x": 0.0, "y": 0.0})
		# Player position in save file could be from an older format.
		if pos.has("x") and pos.has("y"):
			player.global_position = Vector2(pos["x"], pos["y"])

	# Reconnect for the next transition.
	scene_router.scene_changed.connect(_on_scene_changed, CONNECT_ONE_SHOT)


func _autosave() -> void:
	var player: Node2D = world_root.find_child("Player", true, false)
	if player == null:
		push_warning("GameWorld: cannot autosave, Player node not found.")
		return

	var current_data: Dictionary = {
		"player_pos": {
			"x": player.global_position.x,
			"y": player.global_position.y
		},
		"current_scene": scene_router.get_active_scene_path()
	}

	# Merge with existing save data to preserve other state.
	var merged_data: Dictionary = SaveSystem.load_from_slot(SaveSystem.AUTOSAVE_SLOT)
	for key in current_data:
		merged_data[key] = current_data[key]

	SaveSystem.save_to_slot(SaveSystem.AUTOSAVE_SLOT, merged_data)
