extends Node

## Spawn marker id for the destination scene (e.g. overworld `Marker2D` name).
var pending_spawn_marker: String = ""

var _fade_layer: CanvasLayer
var _fade_rect: ColorRect


func fade_to(scene_path: String, spawn_marker: String = "") -> void:
	pending_spawn_marker = spawn_marker
	_ensure_fade_ui()
	var tree := get_tree()
	var tween := create_tween()
	tween.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	tween.tween_property(_fade_rect, "color:a", 1.0, 0.22)
	tween.tween_callback(func() -> void:
		var err := tree.change_scene_to_file(scene_path)
		if err != OK:
			push_error("SceneTransition: change_scene_to_file failed: %s (%d)" % [scene_path, err])
	)
	tween.tween_property(_fade_rect, "color:a", 0.0, 0.28).set_delay(0.03)


func _ensure_fade_ui() -> void:
	if is_instance_valid(_fade_layer) and is_instance_valid(_fade_rect):
		return
	_fade_layer = CanvasLayer.new()
	_fade_layer.layer = 100
	_fade_rect = ColorRect.new()
	_fade_rect.set_anchors_preset(Control.PRESET_FULL_RECT)
	_fade_rect.offset_left = 0.0
	_fade_rect.offset_top = 0.0
	_fade_rect.offset_right = 0.0
	_fade_rect.offset_bottom = 0.0
	_fade_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_fade_rect.color = Color(0, 0, 0, 0)
	_fade_layer.add_child(_fade_rect)
	get_tree().root.add_child(_fade_layer)
