extends CanvasLayer
class_name UI

func _ready() -> void:
	_add_minimap()

func _add_minimap() -> void:
	var minimap_scene = load("res://scenes/Minimap.tscn")
	var minimap = minimap_scene.instantiate()
	add_child(minimap)
