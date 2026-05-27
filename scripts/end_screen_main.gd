extends Control
## Post-credits end card: play time, Test of Fire link, and persisted completion flag.

const TEST_OF_FIRE_URL := "https://newpaladinorder.com/"

@onready var _ui_layer: CanvasLayer = $CanvasLayer


func _ready() -> void:
	ProgressStore.mark_game_complete()
	_show_end_screen()


func _show_end_screen() -> void:
	var end_panel := PanelContainer.new()
	end_panel.set_anchors_preset(Control.PRESET_CENTER)
	end_panel.offset_left = -320.0
	end_panel.offset_top = -200.0
	end_panel.offset_right = 320.0
	end_panel.offset_bottom = 200.0
	var vb := VBoxContainer.new()
	end_panel.add_child(vb)
	var play_time_label := Label.new()
	play_time_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	var secs := GameSession.get_elapsed_seconds()
	play_time_label.text = "Play time: %s" % _format_duration(secs)
	var link := RichTextLabel.new()
	link.bbcode_enabled = true
	link.fit_content = true
	link.custom_minimum_size = Vector2(560, 0)
	link.scroll_active = false
	link.text = (
		"[center]The story continues in [url=%s][b]Test of Fire[/b][/url].[/center]" % TEST_OF_FIRE_URL
	)
	link.meta_clicked.connect(_on_test_of_fire_link)
	vb.add_child(play_time_label)
	vb.add_child(link)
	_ui_layer.add_child(end_panel)


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
		push_warning("End screen: could not open URL %s (error %s)" % [url, err])


func _format_duration(seconds: float) -> String:
	var total := int(floor(seconds))
	var m := total / 60
	var s := total % 60
	if m <= 0:
		return "%ds" % s
	return "%dm %02ds" % [m, s]
