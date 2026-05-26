extends Node2D
## Telvar's private room: resting here sets the flag that gates the sealed-wings night sequence.

@onready var _rest_bed: Area2D = $BedRestArea
@onready var _night: Node = $NightEventRunner

var _player_in_bed_zone: bool = false
var _rest_in_progress: bool = false


func _ready() -> void:
	_rest_bed.body_entered.connect(_on_bed_body_entered)
	_rest_bed.body_exited.connect(_on_bed_body_exited)


func _unhandled_input(event: InputEvent) -> void:
	if _rest_in_progress:
		return
	if not _player_in_bed_zone:
		return
	if event.is_action_pressed("ui_accept"):
		_start_rest_sequence()
		get_viewport().set_input_as_handled()


func _on_bed_body_entered(body: Node2D) -> void:
	if body.is_in_group("player"):
		_player_in_bed_zone = true


func _on_bed_body_exited(body: Node2D) -> void:
	if body.is_in_group("player"):
		_player_in_bed_zone = false


func _start_rest_sequence() -> void:
	_rest_in_progress = true
	await get_tree().create_timer(1.5).timeout
	_rest_in_progress = false
	GameFlags.mark_rested_in_telvar_room()
	await _night.try_play_sequence()
