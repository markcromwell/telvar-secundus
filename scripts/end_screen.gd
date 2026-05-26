extends Control


@onready var _play_time: Label = %PlayTime
@onready var _credits_btn: Button = %ToCredits


func _ready() -> void:
	_refresh_play_time()
	_credits_btn.pressed.connect(_on_to_credits_pressed)


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


func _on_to_credits_pressed() -> void:
	var prev: String = ""
	var cur := get_tree().current_scene
	if cur != null:
		prev = str(cur.scene_file_path)
	SceneTransition.notify_scene_changed(prev, "res://scenes/credits.tscn")
	get_tree().change_scene_to_file("res://scenes/credits.tscn")
