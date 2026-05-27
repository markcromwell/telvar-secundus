extends Node
## One-shot night sequence after resting in Telvar's room: directional growl, Myramar glance, quest update.
## Silent beat: no popup lines or modal text during this sequence.

@onready var _growl: AudioStreamPlayer2D = %SealedWingGrowl
@onready var _myramar_anchor: Marker2D = %MyramarSpawn

var _running: bool = false


func try_play_sequence() -> void:
	if _running:
		return
	if GameFlags.sealed_wings_night_scene_completed:
		return
	if not GameFlags.rested_in_telvar_room:
		return
	_running = true
	await _run_sequence()
	GameFlags.mark_sealed_wings_night_scene_completed()
	_running = false


func _run_sequence() -> void:
	var room := get_parent() as Node2D
	var player := get_tree().get_first_node_in_group("player") as Node2D
	_growl.play()
	await get_tree().create_timer(0.35).timeout
	var sprite := Sprite2D.new()
	sprite.texture = preload("res://assets/sprites/myramar_placeholder.png")
	sprite.centered = true
	room.add_child(sprite)
	sprite.global_position = _myramar_anchor.global_position
	if player != null:
		var face_right := player.global_position.x >= sprite.global_position.x
		sprite.flip_h = face_right
	await get_tree().create_timer(0.75).timeout
	if player != null:
		sprite.flip_h = player.global_position.x < sprite.global_position.x
	var tw := create_tween()
	var end_y := sprite.global_position.y - 22.0
	tw.tween_property(sprite, "modulate:a", 0.0, 0.45)
	tw.parallel().tween_property(sprite, "global_position:y", end_y, 0.45)
	await tw.finished
	sprite.queue_free()
	QuestLog.apply_sealed_wings_after_telvar_room_night()
