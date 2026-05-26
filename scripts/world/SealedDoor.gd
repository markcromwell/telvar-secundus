extends Node2D
## Blocks with a StaticBody2D until the player spends a Sealed Wing Key from [member Inventory].
## Plays a slow eased rotation on the door pivot (stone swing).

const REQUIRED_ITEM: StringName = &"sealed_wing_key"

@export var swing_degrees: float = -88.0
@export var swing_duration_sec: float = 2.35

@onready var _door_pivot: Node2D = $DoorPivot
@onready var _body: StaticBody2D = $DoorPivot/StaticBody2D
@onready var _interact: Area2D = $InteractArea

var _opened: bool = false
var _player_in_range: bool = false
var _busy: bool = false


func _ready() -> void:
	_interact.body_entered.connect(_on_body_entered)
	_interact.body_exited.connect(_on_body_exited)


func _unhandled_input(event: InputEvent) -> void:
	if _opened or _busy or not _player_in_range:
		return
	if not event.is_action_just_pressed(&"ui_accept"):
		return
	get_viewport().set_input_as_handled()
	_try_open()


func _try_open() -> void:
	if not ItemDatabase.has_item(REQUIRED_ITEM):
		push_warning("SealedDoor: item id not defined in item table: %s" % String(REQUIRED_ITEM))
		return
	if not Inventory.has_item(REQUIRED_ITEM, 1):
		return
	if not Inventory.remove_item(REQUIRED_ITEM, 1):
		return
	_busy = true
	_play_stone_swing()


func _play_stone_swing() -> void:
	var tw := create_tween()
	tw.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN_OUT)
	tw.tween_property(_door_pivot, ^"rotation_degrees", swing_degrees, swing_duration_sec)
	tw.finished.connect(_on_swing_finished, CONNECT_ONE_SHOT)


func _on_swing_finished() -> void:
	_opened = true
	_busy = false
	_disable_blocking_collision()


func _disable_blocking_collision() -> void:
	for child in _body.get_children():
		if child is CollisionShape2D:
			(child as CollisionShape2D).set_deferred(&"disabled", true)


func _on_body_entered(body: Node) -> void:
	if body is CharacterBody2D:
		_player_in_range = true


func _on_body_exited(body: Node) -> void:
	if body is CharacterBody2D:
		_player_in_range = false


func is_opened() -> bool:
	return _opened
