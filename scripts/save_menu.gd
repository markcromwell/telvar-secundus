extends Control
## Save menu: three manual slots (1–3). Slot 0 is autosave and is not shown here.
## Button labels use each save file's last modified time as the displayed timestamp.

@onready var _slot1: Button = %Slot1
@onready var _slot2: Button = %Slot2
@onready var _slot3: Button = %Slot3

const _SAVE_FILE_PATTERN: String = "user://save_slot_%d.json"


func _ready() -> void:
	_refresh_all_slots()
	visibility_changed.connect(_on_visibility_changed)


func _on_visibility_changed() -> void:
	if visible:
		_refresh_all_slots()


func _refresh_all_slots() -> void:
	_set_slot_button(_slot1, 1)
	_set_slot_button(_slot2, 2)
	_set_slot_button(_slot3, 3)


func _set_slot_button(btn: Button, slot: int) -> void:
	var path: String = _SAVE_FILE_PATTERN % slot
	if not FileAccess.file_exists(path):
		btn.text = "Slot %d\n(empty)" % slot
		return
	var modified: int = int(FileAccess.get_modified_time(path))
	var when: String = _format_unix_local(modified)
	btn.text = "Slot %d\n%s" % [slot, when]


func _format_unix_local(unix_time: int) -> String:
	if unix_time <= 0:
		return "unknown time"
	var dt: Dictionary = Time.get_datetime_dict_from_unix_time(unix_time, false)
	return "%04d-%02d-%02d %02d:%02d" % [
		int(dt.year),
		int(dt.month),
		int(dt.day),
		int(dt.hour),
		int(dt.minute),
	]
