extends Control


@onready var _body: RichTextLabel = %CreditsBody
@onready var _play_time: Label = %PlayTime
@onready var _finish: Button = %Finish


func _ready() -> void:
	_load_credits_file()
	_refresh_play_time()
	_finish.pressed.connect(_on_finish_pressed)


func _load_credits_file() -> void:
	var path: String = "res://CREDITS.md"
	if not FileAccess.file_exists(path):
		_body.text = "Credits file missing."
		return
	var file := FileAccess.open(path, FileAccess.READ)
	if file == null:
		_body.text = "Could not open credits file."
		return
	_body.text = file.get_as_text()


func _refresh_play_time() -> void:
	var slot: int = ActiveSaveSlot.slot
	if not SaveSystem.is_slot_valid(slot):
		slot = SaveSystem.AUTOSAVE_SLOT
	var data: Dictionary = SaveSystem.load_from_slot(slot)
	var seconds: float = float(data.get("play_time", 0.0))
	_play_time.text = "Play time: %s" % _format_play_time(seconds)


func _format_play_time(seconds: float) -> String:
	var s: int = int(floor(seconds))
	var h: int = s / 3600
	var m: int = (s % 3600) / 60
	var sec: int = s % 60
	return "%d:%02d:%02d" % [h, m, sec]


func _on_finish_pressed() -> void:
	_persist_completion()
	var prev: String = ""
	var cur := get_tree().current_scene
	if cur != null:
		prev = str(cur.scene_file_path)
	SceneTransition.notify_scene_changed(prev, "res://scenes/main_menu.tscn")
	get_tree().change_scene_to_file("res://scenes/main_menu.tscn")


func _persist_completion() -> void:
	var slot: int = ActiveSaveSlot.slot
	if not SaveSystem.is_slot_valid(slot):
		slot = SaveSystem.AUTOSAVE_SLOT
	var data: Dictionary = SaveSystem.load_from_slot(slot)
	data["game_complete"] = true
	data["dark_robe_unlocked"] = true
	if not SaveSystem.save_to_slot(slot, data):
		push_warning("Completion save failed: %s" % SaveSystem.last_save_error)
