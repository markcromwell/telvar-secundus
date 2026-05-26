## Autoload: paints overworld tiles when OverworldMap (or any scene with a TileMap child) loads.
extends Node


func _ready() -> void:
	get_tree().scene_changed.connect(_on_scene_changed)
	# Main scene is not current_scene until after the first frame; autoload _ready runs earlier.
	await get_tree().process_frame
	_try_paint()


func _on_scene_changed() -> void:
	call_deferred("_try_paint")


func _try_paint() -> void:
	var scene := get_tree().current_scene
	if scene == null:
		return
	var tilemap := scene.find_child("TileMap", true, false)
	if tilemap == null or not (tilemap is TileMap):
		return
	OverworldTilePopulator.populate(tilemap as TileMap)
