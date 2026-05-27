extends CanvasLayer

signal transition_error(path)

@onready var color_rect: ColorRect = $ColorRect

var return_position: Vector2 = Vector2.ZERO
var overworld_scene_path: String = ""

func _ready() -> void:
	color_rect.color.a = 0.0
	color_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE

func fade_to_scene(target_path: String, spawn_point_id: String = "") -> void:
	var player = get_tree().get_first_node_in_group("player")
	if player and "global_position" in player:
		return_position = player.global_position
	
	if get_tree().current_scene:
		overworld_scene_path = get_tree().current_scene.scene_file_path

	var tween = create_tween()
	tween.tween_property(color_rect, "color:a", 1.0, 0.3)
	await tween.finished

	if ResourceLoader.exists(target_path):
		var err = get_tree().change_scene_to_file(target_path)
		if err != OK:
			transition_error.emit(target_path)
	else:
		transition_error.emit(target_path)

	tween = create_tween()
	tween.tween_property(color_rect, "color:a", 0.0, 0.3)
	await tween.finished

func return_to_overworld() -> void:
	var tween = create_tween()
	tween.tween_property(color_rect, "color:a", 1.0, 0.3)
	await tween.finished

	if ResourceLoader.exists(overworld_scene_path):
		var err = get_tree().change_scene_to_file(overworld_scene_path)
		if err != OK:
			transition_error.emit(overworld_scene_path)
	else:
		transition_error.emit(overworld_scene_path)
		
	await get_tree().process_frame
	
	var player = get_tree().get_first_node_in_group("player")
	if player and "global_position" in player:
		player.global_position = return_position
	if player and "can_move" in player:
		player.can_move = false

	tween = create_tween()
	tween.tween_property(color_rect, "color:a", 0.0, 0.3)
	await tween.finished
