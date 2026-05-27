extends Control

const _CREDITS_SCENE := preload("res://Credits.tscn")

@onready var _credits_button: Button = $CenterContainer/VBoxContainer/CreditsButton

var _credits_ui_layer: CanvasLayer


func _ready() -> void:
	_credits_button.pressed.connect(_on_credits_pressed)


func _on_credits_pressed() -> void:
	if _credits_ui_layer != null:
		return
	var layer := CanvasLayer.new()
	layer.layer = 100
	var credits: Control = _CREDITS_SCENE.instantiate()
	layer.add_child(credits)
	add_child(layer)
	_credits_ui_layer = layer
	set_process_unhandled_input(true)


func _unhandled_input(event: InputEvent) -> void:
	if _credits_ui_layer == null:
		return
	if event.is_action_pressed("ui_cancel"):
		_credits_ui_layer.queue_free()
		_credits_ui_layer = null
		set_process_unhandled_input(false)
		get_viewport().set_input_as_handled()
