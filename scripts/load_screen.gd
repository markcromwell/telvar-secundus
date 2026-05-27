extends Control
## Four-slot load UI (manual 1–3 + autosave). Uses autoload [member SaveManager] only.

const SLOT_COUNT := 4


func _ready() -> void:
	visibility_changed.connect(_on_visibility_changed)
	for i in range(SLOT_COUNT):
		var btn := get_node("MarginContainer/VBoxContainer/Slot%d" % i) as Button
		btn.pressed.connect(_on_slot_pressed.bind(i))
	_refresh_display()


func _on_visibility_changed() -> void:
	if is_visible_in_tree():
		_refresh_display()


func _refresh_display() -> void:
	for i in range(SLOT_COUNT):
		var btn := get_node("MarginContainer/VBoxContainer/Slot%d" % i) as Button
		var meta: Dictionary = SaveManager.read_slot_metadata(i)
		var empty: bool = bool(meta.get("empty", true))
		btn.disabled = empty
		btn.text = _slot_button_caption(i, meta)
		btn.modulate = Color(0.5, 0.5, 0.55, 1.0) if empty else Color.WHITE


func _slot_header(slot_index: int) -> String:
	if slot_index < 3:
		return "Manual slot %d" % (slot_index + 1)
	return "Autosave"


func _slot_button_caption(slot_index: int, meta: Dictionary) -> String:
	var header := _slot_header(slot_index)
	if bool(meta.get("empty", true)):
		var err := str(meta.get("error", ""))
		if err != "":
			return "%s\nEmpty — %s" % [header, err]
		return "%s\nEmpty" % header
	var ts := int(meta.get("timestamp_unix", 0))
	var time_str := "—"
	if ts > 0:
		time_str = Time.get_datetime_string_from_unix_time(ts, true)
	var act := int(meta.get("act_number", 0))
	var quest := str(meta.get("current_quest_name", ""))
	if quest.is_empty():
		quest = "—"
	return "%s\n%s\nAct %d\n%s" % [header, time_str, act, quest]


func _on_slot_pressed(slot_index: int) -> void:
	var meta: Dictionary = SaveManager.read_slot_metadata(slot_index)
	if bool(meta.get("empty", true)):
		return
	var err: Error = SaveManager.restore_from_slot(slot_index)
	if err != OK:
		push_warning("LoadScreen: restore_from_slot(%d) failed: %d" % [slot_index, err])
