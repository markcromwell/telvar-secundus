extends CanvasLayer

var _notified_quests: Dictionary = {}


func _ready() -> void:
	QuestManager.quest_updated.connect(func(id: String) -> void:
		if _notified_quests.has(id):
			return
		if not QuestManager.quests.has(id):
			return
		var quest: Dictionary = QuestManager.quests[id]
		_notified_quests[id] = true
		show_quest_notification(str(quest.get("title", id)))
	)


func show_lore_popup(text: String) -> void:
	var toast := Panel.new()
	toast.size = Vector2(520, 56)
	toast.set_anchors_and_offsets_preset(Control.PRESET_TOP_WIDE)
	toast.offset_top = 48.0
	toast.offset_bottom = 104.0
	toast.offset_left = 80.0
	toast.offset_right = -80.0
	toast.modulate.a = 0.0
	toast.z_index = 60

	var label := Label.new()
	label.set_anchors_preset(Control.PRESET_FULL_RECT)
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	label.add_theme_font_size_override("font_size", 11)
	label.text = text
	toast.add_child(label)
	add_child(toast)

	var tween := create_tween()
	tween.tween_property(toast, "modulate:a", 1.0, 0.3)
	tween.tween_interval(3.0)
	tween.tween_property(toast, "modulate:a", 0.0, 0.4)
	tween.tween_callback(toast.queue_free)


func show_quest_notification(quest_title: String) -> void:
	var toast := Label.new()
	toast.text = "New Quest!\n%s" % quest_title
	toast.set_anchors_and_offsets_preset(Control.PRESET_TOP_WIDE)
	toast.offset_top = 48.0
	toast.offset_bottom = 112.0
	toast.offset_left = 80.0
	toast.offset_right = -80.0
	toast.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	toast.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	toast.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	toast.add_theme_font_size_override("font_size", 14)
	toast.modulate.a = 0.0
	toast.z_index = 65
	add_child(toast)

	var tween := create_tween()
	tween.tween_property(toast, "modulate:a", 1.0, 0.3)
	tween.tween_interval(2.0)
	tween.tween_property(toast, "modulate:a", 0.0, 0.4)
	tween.tween_callback(toast.queue_free)
