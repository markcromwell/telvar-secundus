extends Control
## UI panel for branching dialogue. Listens to `DialogueManager.dialogue_requested`
## and is opened via `show_dialogue(npc_id)`.

@onready var _name_label: Label = $VBoxContainer/NameLabel
@onready var _text_label: Label = $VBoxContainer/TextLabel
@onready var _choices: VBoxContainer = $VBoxContainer/ChoicesContainer

var _flag_strip: RegEx

var _npc_id: String = ""
var _graph: Dictionary = {}
var _node_id: String = ""


func _ready() -> void:
	_flag_strip = RegEx.new()
	_flag_strip.compile("\\[[a-zA-Z0-9_]+\\]")
	DialogueManager.dialogue_requested.connect(_on_dialogue_requested)


func show_dialogue(npc_id: String) -> void:
	DialogueManager.show_dialogue(npc_id)


func _on_dialogue_requested(npc_id: String, graph: Dictionary, entry_id: String) -> void:
	_npc_id = npc_id
	_graph = graph
	_node_id = entry_id
	_render_current_node()


func _render_current_node() -> void:
	if _node_id.is_empty() or not _graph.has(_node_id):
		_close_dialogue()
		return

	var node: Dictionary = _graph[_node_id] as Dictionary
	var speaker := str(node.get("speaker", ""))
	_name_label.text = speaker if not speaker.is_empty() else _npc_id
	_text_label.text = _strip_bracket_flags(str(node.get("text", "")))
	_clear_choices()

	var next_id := str(node.get("next", ""))
	if not next_id.is_empty() and _graph.has(next_id):
		_add_choice_button("Continue", _advance_to.bind(next_id))
	elif not next_id.is_empty():
		Log.warn("DialogueBox: missing next node '%s' for id '%s'" % [next_id, _node_id])
		_add_choice_button("Close", _close_dialogue)
	else:
		_add_choice_button("Close", _close_dialogue)

	visible = true


func _advance_to(next_id: String) -> void:
	_node_id = next_id
	_render_current_node()


func _close_dialogue() -> void:
	visible = false
	_npc_id = ""
	_graph.clear()
	_node_id = ""
	_clear_choices()
	_name_label.text = ""
	_text_label.text = ""


func _clear_choices() -> void:
	for child in _choices.get_children():
		child.free()


func _add_choice_button(label_text: String, on_pressed: Callable) -> void:
	var btn := Button.new()
	btn.text = label_text
	btn.pressed.connect(on_pressed)
	_choices.add_child(btn)


func _strip_bracket_flags(body: String) -> String:
	return _flag_strip.sub(body, "", true)
