extends Area2D
## South nave exit: fade out then return to Secundus overworld with spawn hint.

const OVERWORLD_SCENE := "res://scenes/world/secundus_overworld.tscn"
const SPAWN_MARKER_NAME := "paladin_temple_exit"
const FADE_SECONDS := 0.3

var _triggered: bool = false


func _ready() -> void:
	body_entered.connect(_on_body_entered)


func _on_body_entered(body: Node2D) -> void:
	if _triggered or body == null:
		return
	if body is CharacterBody2D or body.is_in_group("player"):
		_triggered = true
		_fade_and_leave()


func _fade_and_leave() -> void:
	var fade_rect: ColorRect = get_node("../UICanvas/FadeRect") as ColorRect
	var tw := create_tween()
	tw.tween_property(fade_rect, "color", Color(0, 0, 0, 1.0), FADE_SECONDS)
	await tw.finished
	if not ResourceLoader.exists(OVERWORLD_SCENE):
		push_error("ExitDoor: overworld scene missing: %s" % OVERWORLD_SCENE)
		_triggered = false
		return
	var bridge: Node = get_node_or_null("/root/GameBridge")
	if bridge and bridge.has_method("set_next_spawn"):
		bridge.set_next_spawn(SPAWN_MARKER_NAME)
	get_tree().change_scene_to_file(OVERWORLD_SCENE)
