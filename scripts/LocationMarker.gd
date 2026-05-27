extends Node2D

@export var location_name: String = ""
@export var marker_color: Color = Color.WHITE

var _label: Label


func _ready() -> void:
	_label = Label.new()
	_label.name = "Label"
	_label.z_index = 10
	_label.top_level = true
	_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_label.add_theme_color_override("font_color", marker_color)
	add_child(_label)


func _process(_delta: float) -> void:
	if not is_instance_valid(_label):
		return
	_label.text = location_name
	_label.add_theme_color_override("font_color", marker_color)
	var xf: Transform2D = get_viewport_transform()
	var anchor_viewport: Vector2 = xf * Vector2.ZERO
	var zoom: Vector2 = xf.get_scale()
	if zoom.x > 0.0001 and zoom.y > 0.0001:
		_label.scale = Vector2(1.0 / zoom.x, 1.0 / zoom.y)
	else:
		_label.scale = Vector2.ONE
	var half: Vector2 = _label.size * _label.scale * 0.5
	_label.global_position = anchor_viewport - half
