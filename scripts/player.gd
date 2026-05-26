extends CharacterBody2D

var can_move: bool = true
var current_entrance: EntranceTrigger = null


func _ready() -> void:
	add_to_group("player")


func set_current_entrance(entrance: EntranceTrigger) -> void:
	current_entrance = entrance


func clear_current_entrance(entrance: EntranceTrigger) -> void:
	if current_entrance == entrance:
		current_entrance = null


func _unhandled_input(event: InputEvent) -> void:
	if not can_move:
		return
	if current_entrance == null:
		return
	if not _is_interact_e(event):
		return
	var entrance := current_entrance
	_begin_entrance_transition(entrance)


func _is_interact_e(event: InputEvent) -> bool:
	if event is InputEventKey:
		var key_event := event as InputEventKey
		return key_event.pressed and not key_event.echo and key_event.keycode == KEY_E
	return false


func _begin_entrance_transition(entrance: EntranceTrigger) -> void:
	can_move = false
	var path := entrance.target_scene
	var spawn_id := entrance.spawn_point_id
	current_entrance = null
	await TransitionManager.fade_to_scene(path, spawn_id)
	can_move = true
