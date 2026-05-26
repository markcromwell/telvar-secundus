extends Control
## Scrolling credits from CREDITS.md (incl. NPO); exits to end screen or main menu per GameSession flag.

const CREDITS_PATH := "res://CREDITS.md"

@onready var _ui_layer: CanvasLayer = $CanvasLayer


func _ready() -> void:
	await _play_credits_scroll()
	_go_next()


func _go_next() -> void:
	if GameSession.credits_exit_to_main_menu:
		get_tree().change_scene_to_file("res://scenes/main_menu.tscn")
	else:
		get_tree().change_scene_to_file("res://scenes/end_screen_main.tscn")


func _play_credits_scroll() -> void:
	var body := _load_credits_body()
	var credits_host := Control.new()
	credits_host.set_anchors_preset(Control.PRESET_FULL_RECT)
	credits_host.clip_contents = true
	_ui_layer.add_child(credits_host)
	var credits_label := Label.new()
	credits_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	credits_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	credits_label.custom_minimum_size.x = _viewport_size().x - 80.0
	credits_label.size.x = _viewport_size().x - 80.0
	credits_label.text = body
	credits_label.position = Vector2(40, _viewport_size().y)
	credits_label.add_theme_font_size_override("font_size", 20)
	credits_host.add_child(credits_label)
	await get_tree().process_frame
	await get_tree().process_frame
	var lines := max(credits_label.get_line_count(), 1)
	var content_h := credits_label.get_line_height() * float(lines) + 40.0
	var travel := _viewport_size().y + content_h + 120.0
	var duration := clampf(travel / 90.0, 18.0, 55.0)
	var tw := create_tween()
	tw.set_parallel(false)
	tw.tween_property(credits_label, "position:y", -content_h - 40.0, duration)
	await tw.finished
	if is_instance_valid(credits_host):
		credits_host.queue_free()


func _load_credits_body() -> String:
	if not FileAccess.file_exists(CREDITS_PATH):
		return "# Credits\n(Missing CREDITS.md)\n\n## Story\n- New Paladin Order series by Mark Cromwell"
	var raw := FileAccess.get_file_as_string(CREDITS_PATH)
	return raw.strip_edges()


func _viewport_size() -> Vector2:
	return get_viewport().get_visible_rect().size
