extends Control

## UI root for NPC dialogue: speaker name, body text, and choice buttons.

@onready var _name_label: Label = $VBoxContainer/NameLabel
@onready var _text_label: Label = $VBoxContainer/TextLabel
@onready var _choices_container: VBoxContainer = $VBoxContainer/ChoicesContainer


func populate(speaker: String, text: String, choices: Array) -> void:
	_name_label.text = speaker
	_text_label.text = text
	for child in _choices_container.get_children():
		_choices_container.remove_child(child)
		child.free()
	for item in choices:
		var btn := Button.new()
		if item is String:
			btn.text = item
		elif item is Dictionary and (item as Dictionary).has("text"):
			btn.text = str((item as Dictionary)["text"])
		else:
			btn.text = str(item)
		_choices_container.add_child(btn)
