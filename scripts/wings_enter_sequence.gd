extends Node
## Phase 2714 — Enter Sealed Wings: consume key, door anim, walk 5 tiles forward, fade to black, then final cutscene.
## Skip input (e.g. ui_cancel) is ignored until the full sequence completes.

signal sequence_finished

const RENDERED_TILE_PX: float = 32.0  # 16px art * 2x content scale
const WALK_TILE_COUNT: int = 5

@export var player: NodePath
@export var door_animation_player: NodePath
@export var fade_rect: NodePath
@export var walk_direction: Vector2 = Vector2.DOWN
@export var door_animation_name: StringName = &""
@export var fade_seconds: float = 1.25
@export var final_cutscene_scene: String = ""

var _playback_complete: bool = false
var _running: bool = false

var _player: TelvarPlayer
var _door: AnimationPlayer
var _fade: ColorRect

var _walk_start: Vector2
var _walk_target_along: float
var _walk_dir: Vector2


func _ready() -> void:
	set_process_unhandled_input(true)


func try_begin_enter_from_choice() -> bool:
	if _running:
		return false
	if not Inventory.try_consume_sealed_wings_key():
		return false
	_resolve_nodes()
	_running = true
	_playback_complete = false
	_player.manual_input_enabled = false
	_player.clear_scripted_velocity()
	_run_sequence()
	return true


func _resolve_nodes() -> void:
	_player = get_node(player) as TelvarPlayer
	_door = get_node(door_animation_player) as AnimationPlayer
	_fade = get_node(fade_rect) as ColorRect


func _run_sequence() -> void:
	await _play_door_then_walk()
	await _fade_to_black()

	_playback_complete = true
	_running = false
	sequence_finished.emit()

	if final_cutscene_scene != "" and ResourceLoader.exists(final_cutscene_scene):
		get_tree().change_scene_to_file(final_cutscene_scene)
		return

	_player.manual_input_enabled = true
	_player.clear_scripted_velocity()


func _play_door_then_walk() -> void:
	if _door != null:
		if String(door_animation_name) != "" and _door.has_animation(door_animation_name):
			_door.play(door_animation_name)
			await _door.animation_finished
		else:
			# Hook present for scenes that add clips later; still yields one physics tick.
			await get_tree().physics_frame

	_walk_dir = walk_direction.normalized()
	if _walk_dir == Vector2.ZERO:
		_walk_dir = Vector2.DOWN

	_walk_start = _player.global_position
	_walk_target_along = float(WALK_TILE_COUNT) * RENDERED_TILE_PX

	while true:
		var along: float = (_player.global_position - _walk_start).dot(_walk_dir)
		if along >= _walk_target_along:
			_player.global_position = _walk_start + _walk_dir * _walk_target_along
			_player.clear_scripted_velocity()
			break
		_player.set_scripted_velocity(_walk_dir * _player.speed)
		await get_tree().physics_frame


func _fade_to_black() -> void:
	_fade.visible = true
	_fade.color = Color(0.0, 0.0, 0.0, 0.0)
	var tw := create_tween()
	tw.tween_property(_fade, "color", Color(0.0, 0.0, 0.0, 1.0), fade_seconds)
	await tw.finished


func _unhandled_input(event: InputEvent) -> void:
	if not _running:
		return
	if _playback_complete:
		return
	if event.is_action_pressed(&"ui_cancel"):
		get_viewport().set_input_as_handled()
