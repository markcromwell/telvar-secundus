extends Node
## Autoload: coordinates scene flow, manual save UI, and serializable game state.

const SAVE_DIALOG_SCENE := preload("res://ui/save_dialog.tscn")

var _save_dialog_layer: CanvasLayer = null


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	_ensure_save_action()


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("save_game"):
		get_viewport().set_input_as_handled()
		open_save_dialog()


func _ensure_save_action() -> void:
	if not InputMap.has_action("save_game"):
		InputMap.add_action("save_game")
	if InputMap.action_get_events("save_game").is_empty():
		var ev := InputEventKey.new()
		ev.physical_keycode = KEY_F5
		InputMap.action_add_event("save_game", ev)


func is_save_dialog_open() -> bool:
	return _save_dialog_layer != null and is_instance_valid(_save_dialog_layer)


func open_save_dialog() -> void:
	if is_save_dialog_open():
		return
	var layer := CanvasLayer.new()
	layer.process_mode = Node.PROCESS_MODE_ALWAYS
	layer.layer = 100
	layer.name = "SaveDialogLayer"
	var dlg: Control = SAVE_DIALOG_SCENE.instantiate()
	layer.add_child(dlg)
	get_tree().root.add_child(layer)
	dlg.dialog_closed.connect(_on_save_dialog_closed.bind(layer), CONNECT_ONE_SHOT)
	_save_dialog_layer = layer


func _on_save_dialog_closed(layer: CanvasLayer) -> void:
	_save_dialog_layer = null
	if is_instance_valid(layer):
		layer.queue_free()


func get_save_state() -> Dictionary:
	var state := {
		"version": 1,
		"saved_at": Time.get_datetime_string_from_system(),
		"scene_path": "",
	}
	var cs := get_tree().current_scene
	if cs:
		state["scene_path"] = String(cs.scene_file_path)
	var players := get_tree().get_nodes_in_group("player_controllers")
	if not players.is_empty():
		var p: Node = players[0]
		if p.has_method("capture_save_state"):
			state["player"] = p.call("capture_save_state")
	return state


## Writes [method get_save_state] JSON to `user://save_slot_{slot_index}.json` (slots 1–3).
func save_to_user_slot(slot_index: int) -> bool:
	if slot_index < 1 or slot_index > 3:
		push_error("save_to_user_slot: slot_index must be 1–3, got %d" % slot_index)
		return false
	var path := "user://save_slot_%d.json" % slot_index
	var text := JSON.stringify(get_save_state())
	var file := FileAccess.open(path, FileAccess.WRITE)
	if file == null:
		push_error("Save failed (could not open path): %s" % path)
		return false
	file.store_string(text)
	file.close()
	return true
