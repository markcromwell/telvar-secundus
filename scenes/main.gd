extends Node


@onready var _spell_panel: Node = $CanvasLayer/CastSpellPanel


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_just_pressed(&"toggle_cast_spell"):
		_spell_panel.toggle_visible()
		get_viewport().set_input_as_handled()
