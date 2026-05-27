extends Node

## Full-screen fade overlay; persists as an autoload across scene changes.

const DEFAULT_FADE_DURATION := 0.3

var _layer: CanvasLayer
var _rect: ColorRect
var _active_tween: Tween


func _ready() -> void:
	_layer = CanvasLayer.new()
	_layer.layer = 128
	_rect = ColorRect.new()
	_rect.color = Color.BLACK
	_rect.set_anchors_preset(Control.PRESET_FULL_RECT)
	_rect.mouse_filter = Control.MOUSE_FILTER_STOP
	_rect.modulate = Color(1, 1, 1, 0)
	_layer.add_child(_rect)
	get_tree().root.call_deferred("add_child", _layer)


func fade_to(scene_path: String, duration: float = DEFAULT_FADE_DURATION) -> void:
	if not is_instance_valid(_rect):
		return
	if _active_tween and is_instance_valid(_active_tween):
		_active_tween.kill()

	var d := maxf(duration, 0.01)
	_active_tween = create_tween()
	_active_tween.set_parallel(false)
	_active_tween.tween_property(_rect, "modulate:a", 1.0, d)
	_active_tween.tween_callback(func() -> void:
		var err := get_tree().change_scene_to_file(scene_path)
		if err != OK:
			push_error("FadeTransition: change_scene_to_file failed: %s (%s)" % [err, scene_path])
	)
	_active_tween.tween_property(_rect, "modulate:a", 0.0, d)
