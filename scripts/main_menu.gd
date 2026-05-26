extends Control


@onready var _credits_btn: Button = %Credits


func _ready() -> void:
	_credits_btn.pressed.connect(_on_credits_pressed)


func _notify_and_go(next_scene: String) -> void:
	var prev: String = ""
	var cur := get_tree().current_scene
	if cur != null:
		prev = str(cur.scene_file_path)
	SceneTransition.notify_scene_changed(prev, next_scene)
	get_tree().change_scene_to_file(next_scene)


func _on_credits_pressed() -> void:
	_notify_and_go("res://scenes/credits.tscn")
