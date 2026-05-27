extends Control
class_name DialogueBox
## UI for one dialogue step: speaker, body text, optional choices, or Continue.
## Layout matches spec: Control > VBoxContainer > NameLabel, TextLabel, ChoicesContainer.

signal continue_pressed
signal choice_pressed(next_id: String)

@onready var _name_label: Label = %NameLabel
@onready var _text_label: Label = %TextLabel
@onready var _choices_container: VBoxContainer = %ChoicesContainer
@onready var _continue_button: Button = %ContinueButton


func _ready() -> void:
	_continue_button.pressed.connect(_on_continue_pressed)


func present_node(node: Dictionary) -> void:
	_name_label.text = str(node.get("speaker", ""))
	_text_label.text = str(node.get("text", ""))
	for c in _choices_container.get_children():
		c.queue_free()

	var choices: Variant = node.get("choices", [])
	var has_choices := typeof(choices) == TYPE_ARRAY and (choices as Array).size() > 0

	_continue_button.visible = not has_choices
	_choices_container.visible = has_choices

	if has_choices:
		for ch in choices as Array:
			if typeof(ch) != TYPE_DICTIONARY:
				continue
			var d := ch as Dictionary
			if not d.has("next"):
				continue
			var btn := Button.new()
			btn.text = str(d.get("text", "…"))
			var next_id := str(d["next"])
			btn.pressed.connect(func() -> void: choice_pressed.emit(next_id))
			_choices_container.add_child(btn)


func _on_continue_pressed() -> void:
	continue_pressed.emit()
