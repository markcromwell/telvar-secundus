extends Control

signal choice_selected(index: int)

const CHARS_PER_SEC: float = 30.0

@onready var _portrait: TextureRect = $PanelContainer/VBoxContainer/HBoxContainer/PortraitRect
@onready var _name_label: Label = $PanelContainer/VBoxContainer/HBoxContainer/NameLabel
@onready var _text_label: Label = $PanelContainer/VBoxContainer/TextLabel
@onready var _choices_root: VBoxContainer = $PanelContainer/VBoxContainer/ChoicesContainer

var _full_text: String = ""
var _visible_chars: float = 0.0
var _typing_complete: bool = false
var _choice_buttons: Array[Button] = []


func _ready() -> void:
	hide_dialogue()


func show_dialogue(entry: Dictionary) -> void:
	hide_dialogue()
	visible = true
	mouse_filter = Control.MOUSE_FILTER_STOP
	_name_label.text = str(entry.get("speaker", ""))
	_full_text = str(entry.get("text", ""))
	_visible_chars = 0.0
	_typing_complete = false
	_text_label.text = ""
	_apply_portrait(entry)
	_build_choice_buttons(entry.get("choices", []))
	if _full_text.is_empty():
		_complete_typing()
	else:
		set_process(true)


func hide_dialogue() -> void:
	visible = false
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_process(false)
	_full_text = ""
	_visible_chars = 0.0
	_typing_complete = false
	_text_label.text = ""
	_name_label.text = ""
	_portrait.texture = null
	for b in _choice_buttons:
		b.queue_free()
	_choice_buttons.clear()


func _process(delta: float) -> void:
	if not visible or _typing_complete:
		return
	_visible_chars = minf(float(_full_text.length()), _visible_chars + CHARS_PER_SEC * delta)
	_update_typewriter_text()
	if _visible_chars >= _full_text.length():
		_complete_typing()


func _unhandled_input(event: InputEvent) -> void:
	if not visible:
		return
	if event is InputEventKey and event.pressed and not event.echo:
		var key := (event as InputEventKey).keycode
		if key == KEY_ESCAPE:
			hide_dialogue()
			get_viewport().set_input_as_handled()
			return
		if key == KEY_SPACE:
			if not _typing_complete:
				_visible_chars = _full_text.length()
				_complete_typing()
				get_viewport().set_input_as_handled()
			return
		if key >= KEY_1 and key <= KEY_4:
			var idx: int = key - KEY_1
			if idx < _choice_buttons.size() and _typing_complete and not _choice_buttons[idx].disabled:
				_on_choice_button_pressed(idx)
				get_viewport().set_input_as_handled()


func _apply_portrait(entry: Dictionary) -> void:
	var pt: Variant = entry.get("portrait", null)
	if pt is String and ResourceLoader.exists(pt):
		_portrait.texture = load(pt)
	elif pt is Texture2D:
		_portrait.texture = pt
	else:
		_portrait.texture = null


func _build_choice_buttons(choices: Variant) -> void:
	if choices is not Array:
		return
	var i := 0
	for ch in choices:
		if i >= 4:
			break
		if ch is Dictionary:
			var btn := Button.new()
			btn.text = str(ch.get("text", "?"))
			btn.disabled = true
			btn.focus_mode = Control.FOCUS_ALL
			btn.pressed.connect(_on_choice_button_pressed.bind(i))
			_choices_root.add_child(btn)
			_choice_buttons.append(btn)
		i += 1


func _on_choice_button_pressed(idx: int) -> void:
	if idx < 0 or idx >= _choice_buttons.size():
		return
	if not _typing_complete:
		return
	choice_selected.emit(idx)
	hide_dialogue()


func _complete_typing() -> void:
	_visible_chars = _full_text.length()
	_typing_complete = true
	_update_typewriter_text()
	for b in _choice_buttons:
		b.disabled = false
	set_process(false)


func _update_typewriter_text() -> void:
	var n: int = int(floor(_visible_chars))
	_text_label.text = _full_text.substr(0, n)
