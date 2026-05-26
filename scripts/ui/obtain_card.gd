extends CanvasLayer

## Seconds before the card hides. Set 0 to only dismiss manually.
@export var auto_hide_seconds: float = 4.0

@onready var _dimmer: ColorRect = $Root/Dimmer
@onready var _panel: PanelContainer = $Root/Center/Panel
@onready var _title: Label = $Root/Center/Panel/Margin/VBox/TitleLabel
@onready var _description: Label = $Root/Center/Panel/Margin/VBox/DescriptionLabel
@onready var _tags: Label = $Root/Center/Panel/Margin/VBox/TagsLabel

var _hide_timer: Timer
var _closing: bool = false


func _ready() -> void:
	visible = false
	layer = 80
	_hide_timer = Timer.new()
	_hide_timer.one_shot = true
	_hide_timer.timeout.connect(_on_hide_timer_timeout)
	add_child(_hide_timer)
	_dimmer.gui_input.connect(_on_overlay_gui_input)
	_panel.gui_input.connect(_on_overlay_gui_input)


func _input(event: InputEvent) -> void:
	if not visible:
		return
	if event.is_action_pressed(&"ui_cancel") or event.is_action_pressed(&"ui_accept"):
		get_viewport().set_input_as_handled()
		_close()


func _on_overlay_gui_input(event: InputEvent) -> void:
	if not visible:
		return
	if event is InputEventMouseButton:
		var mb := event as InputEventMouseButton
		if mb.pressed and mb.button_index == MOUSE_BUTTON_LEFT:
			get_viewport().set_input_as_handled()
			_close()


## Shows the obtain overlay for one frame of item data (name, description, tags).
func show_for_item(item: Item) -> void:
	if item == null:
		return
	_hide_timer.stop()
	_closing = false
	_title.text = item.display_name
	_description.text = item.description
	if item.tags.is_empty():
		_tags.visible = false
	else:
		_tags.visible = true
		_tags.text = "Tags: " + ", ".join(item.tags)
	visible = true
	if auto_hide_seconds > 0.0:
		_hide_timer.start(auto_hide_seconds)


func _on_hide_timer_timeout() -> void:
	_close()


func _close() -> void:
	if _closing:
		return
	_closing = true
	_hide_timer.stop()
	visible = false
