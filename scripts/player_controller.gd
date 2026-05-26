extends Node2D
## Minimal player root used by SceneManager for serialized state.


func _ready() -> void:
	add_to_group("player_controllers")


func capture_save_state() -> Dictionary:
	return {"position": {"x": position.x, "y": position.y}}
