extends Node

## Autoload singleton: one dialogue at a time, optional player movement lock.

var is_dialogue_active: bool = false

const _DIALOGUE_BOX_SCENE: PackedScene = preload("res://scenes/DialogueBox.tscn")

var _flags: Dictionary = {}
var _dialogue_ui: Control = null
var _player_ref: CharacterBody2D = null
var _active_npc_id: String = ""

func show_dialogue(npc_id: String, dialogue_json: Array, portrait: Texture2D = null) -> void:
	if is_dialogue_active:
		return
	var start_node: Dictionary = _find_node_by_id(dialogue_json, "start")
	if start_node.is_empty():
		push_warning("DialogueManager: missing id 'start' in dialogue for %s" % npc_id)
		return
	is_dialogue_active = true
	_active_npc_id = npc_id
	_player_ref = get_tree().get_first_node_in_group("player") as CharacterBody2D
	if _player_ref:
		_player_ref.can_move = false
	_dialogue_ui = _DIALOGUE_BOX_SCENE.instantiate() as Control
	get_tree().root.add_child(_dialogue_ui)
	var vbox: VBoxContainer = _dialogue_ui.get_node("VBoxContainer") as VBoxContainer
	var name_label: Label = vbox.get_node("NameLabel") as Label
	var text_label: Label = vbox.get_node("TextLabel") as Label
	var portrait_tex: TextureRect = vbox.get_node("PortraitTexture") as TextureRect
	name_label.text = str(start_node.get("speaker", ""))
	text_label.text = str(start_node.get("text", ""))
	if portrait:
		portrait_tex.texture = portrait
		portrait_tex.visible = true
	else:
		portrait_tex.texture = null
		portrait_tex.visible = false
	_dialogue_ui.visible = true


func hide_dialogue() -> void:
	if _dialogue_ui and is_instance_valid(_dialogue_ui):
		_dialogue_ui.queue_free()
	_dialogue_ui = null
	if _player_ref and is_instance_valid(_player_ref):
		_player_ref.can_move = true
	_player_ref = null
	_active_npc_id = ""
	is_dialogue_active = false


func set_flag(key: String, value) -> void:
	_flags[key] = value


func get_flag(key: String):
	return _flags.get(key)


func _find_node_by_id(dialogue_json: Array, node_id: String) -> Dictionary:
	for item in dialogue_json:
		if typeof(item) == TYPE_DICTIONARY and str(item.get("id", "")) == node_id:
			return item
	return {}
