extends Node2D
## Final corridor beat: Myramar line, scrolling credits (incl. NPO), end screen + completion flag.

const DIALOGUE_LINE := "And so it begins."
const CREDITS_PATH := "res://CREDITS.md"
const TEST_OF_FIRE_URL := "https://newpaladinorder.com/"

@onready var _tile_map: TileMap = $CorridorFloor
@onready var _myramar_sprite: Sprite2D = $Myramar/Sprite2D
@onready var _ui_layer: CanvasLayer = $UILayer

var _dialogue_label: Label
var _credits_host: Control
var _credits_label: Label
var _end_panel: PanelContainer
var _play_time_label: Label
var _link: RichTextLabel


func _ready() -> void:
	_setup_corridor_visuals()
	_setup_dialogue_ui()
	_run_sequence()


func _setup_corridor_visuals() -> void:
	var tex: Texture2D = load("res://assets/tilesets/lpc_terrain.png")
	var tile_set := TileSet.new()
	var atlas := TileSetAtlasSource.new()
	atlas.texture = tex
	atlas.texture_region_size = Vector2i(16, 16)
	var source_id := tile_set.add_source(atlas)
	_tile_map.tile_set = tile_set
	for x in range(-8, 48):
		for y in range(-4, 14):
			var ax := abs(x) % 4
			var ay := abs(y) % 2
			_tile_map.set_cell(0, Vector2i(x, y), source_id, Vector2i(ax, ay))
	_myramar_sprite.texture = tex
	_myramar_sprite.region_enabled = true
	_myramar_sprite.region_rect = Rect2(0, 0, 16, 32)
	_myramar_sprite.centered = true


func _setup_dialogue_ui() -> void:
	_dialogue_label = Label.new()
	_dialogue_label.text = DIALOGUE_LINE
	_dialogue_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_dialogue_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_dialogue_label.add_theme_font_size_override("font_size", 28)
	var dwrap := MarginContainer.new()
	dwrap.set_anchors_preset(Control.PRESET_FULL_RECT)
	dwrap.add_child(_dialogue_label)
	_dialogue_label.set_anchors_preset(Control.PRESET_FULL_RECT)
	_ui_layer.add_child(dwrap)
	dwrap.name = "DialogueWrap"
	_dialogue_label.visible = true


func _run_sequence() -> void:
	await get_tree().create_timer(3.5).timeout
	if is_instance_valid(_dialogue_label.get_parent()):
		_dialogue_label.get_parent().queue_free()
	await _play_credits_scroll()
	_show_end_screen()


func _play_credits_scroll() -> void:
	var body := _load_credits_body()
	_credits_host = Control.new()
	_credits_host.set_anchors_preset(Control.PRESET_FULL_RECT)
	_credits_host.clip_contents = true
	_ui_layer.add_child(_credits_host)
	_credits_label = Label.new()
	_credits_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_credits_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_credits_label.custom_minimum_size.x = _viewport_size().x - 80.0
	_credits_label.size.x = _viewport_size().x - 80.0
	_credits_label.text = body
	_credits_label.position = Vector2(40, _viewport_size().y)
	_credits_label.add_theme_font_size_override("font_size", 20)
	_credits_host.add_child(_credits_label)
	# Two frames: Label line-wrap/layout is stable after first layout pass (Web / mobile).
	await get_tree().process_frame
	await get_tree().process_frame
	var lines := max(_credits_label.get_line_count(), 1)
	var content_h := _credits_label.get_line_height() * float(lines) + 40.0
	var travel := _viewport_size().y + content_h + 120.0
	var duration := clampf(travel / 90.0, 18.0, 55.0)
	var tw := create_tween()
	tw.set_parallel(false)
	tw.tween_property(_credits_label, "position:y", -content_h - 40.0, duration)
	await tw.finished
	if is_instance_valid(_credits_host):
		_credits_host.queue_free()


func _show_end_screen() -> void:
	ProgressStore.mark_game_complete()
	_end_panel = PanelContainer.new()
	_end_panel.set_anchors_preset(Control.PRESET_CENTER)
	_end_panel.offset_left = -320.0
	_end_panel.offset_top = -200.0
	_end_panel.offset_right = 320.0
	_end_panel.offset_bottom = 200.0
	var vb := VBoxContainer.new()
	_end_panel.add_child(vb)
	_play_time_label = Label.new()
	_play_time_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	var secs := GameSession.get_elapsed_seconds()
	_play_time_label.text = "Play time: %s" % _format_duration(secs)
	_link = RichTextLabel.new()
	_link.bbcode_enabled = true
	_link.fit_content = true
	_link.custom_minimum_size = Vector2(560, 0)
	_link.scroll_active = false
	_link.text = (
		"[center]The story continues in [url=%s][b]Test of Fire[/b][/url].[/center]" % TEST_OF_FIRE_URL
	)
	_link.meta_clicked.connect(_on_test_of_fire_link)
	vb.add_child(_play_time_label)
	vb.add_child(_link)
	_ui_layer.add_child(_end_panel)


func _on_test_of_fire_link(meta: Variant) -> void:
	var url := str(meta)
	if url.is_empty():
		url = TEST_OF_FIRE_URL
	_open_external_url(url)


## Desktop/Linux export uses OS.shell_open; HTML5 needs the browser bridge (shell_open is unreliable in WASM).
func _open_external_url(url: String) -> void:
	if url.is_empty():
		return
	if OS.has_feature("web"):
		var js := Engine.get_singleton("JavaScriptBridge")
		if js:
			var code := "window.open(%s, '_blank')" % JSON.stringify(url)
			js.eval(code, true)
			return
	var err := OS.shell_open(url)
	if err != OK:
		push_warning("Cutscene: could not open URL %s (error %s)" % [url, err])


func _load_credits_body() -> String:
	if not FileAccess.file_exists(CREDITS_PATH):
		return "# Credits\n(Missing CREDITS.md)\n\n## Story\n- New Paladin Order series by Mark Cromwell"
	var raw := FileAccess.get_file_as_string(CREDITS_PATH)
	return raw.strip_edges()


func _viewport_size() -> Vector2:
	return get_viewport().get_visible_rect().size


func _format_duration(seconds: float) -> String:
	var total := int(floor(seconds))
	var m := total / 60
	var s := total % 60
	if m <= 0:
		return "%ds" % s
	return "%dm %02ds" % [m, s]
