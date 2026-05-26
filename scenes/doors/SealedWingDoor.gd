extends Node2D
## Sealed Wing door: [StaticBody2D] blocks passage; [Area2D] handles pointer/touch.
## Plays locked SFX and shows act-dependent copy. Add a node in group `story_state`
## with an `act` property (int) to drive Acts 1–3 whisper; use [member act_override] in the inspector for isolated scenes.

const MSG_AUTHORISED := "Authorised personnel only"
const MSG_ABYSS_WHISPER := "The seal hums. Far below, something remembers your name."

@export var act_override: int = 0

@onready var _area: Area2D = $Area2D
@onready var _audio: AudioStreamPlayer2D = $AudioStreamPlayer2D
@onready var _lock_sprite: Sprite2D = $LockSprite
@onready var _message_panel: PanelContainer = $Overlay/MessagePanel
@onready var _message_label: Label = $Overlay/MessagePanel/MarginContainer/MessageLabel
@onready var _hide_timer: Timer = $Overlay/HideTimer


func _ready() -> void:
	_area.input_event.connect(_on_area_input)
	_hide_timer.timeout.connect(_on_hide_timer_timeout)


func _on_area_input(_viewport: Node, event: InputEvent, _shape_idx: int) -> void:
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		_handle_interact()
	elif event is InputEventScreenTouch and event.pressed:
		_handle_interact()


func _handle_interact() -> void:
	if _audio.stream:
		_audio.play()
	var tw := create_tween()
	_lock_sprite.scale = Vector2.ONE
	tw.tween_property(_lock_sprite, "scale", Vector2(1.12, 1.12), 0.08).set_trans(Tween.TRANS_SINE)
	tw.tween_property(_lock_sprite, "scale", Vector2.ONE, 0.12).set_trans(Tween.TRANS_SINE)

	var act := _resolve_act()
	var text := MSG_AUTHORISED
	if act >= 1 and act <= 3:
		text = "%s\n\n%s" % [MSG_AUTHORISED, MSG_ABYSS_WHISPER]
	_message_label.text = text
	_message_panel.visible = true
	_hide_timer.stop()
	_hide_timer.start(4.0)


func _on_hide_timer_timeout() -> void:
	_message_panel.visible = false


func _resolve_act() -> int:
	if act_override > 0:
		return act_override
	var n := get_tree().get_first_node_in_group("story_state")
	if n == null:
		return 1
	var v: Variant = n.get("act")
	if v == null:
		return 1
	return int(v)
